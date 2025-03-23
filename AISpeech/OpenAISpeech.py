import openai
import os
import time
import pyaudio
from pathlib import Path
from dotenv import load_dotenv
import threading
import logging

# Load environment variables from .env file
load_dotenv()

# Retrieve API key from environment variables for openai
openai_key = os.getenv("openai_key")
openai.api_key = openai_key
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"),)

# Retrieve API key from environment variables for azure speech
speech_key = os.getenv("speech_key")
service_region = os.getenv("service_region")

try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
 
    print("""
    Importing the Speech SDK for Python failed.
    Refer to
    https://docs.microsoft.com/azure/cognitive-services/speech-service/quickstart-python for
    installation instructions.
    """)
    import sys
    sys.exit(1)

# Configure speech recognition for Chinese
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
speech_config.speech_recognition_language = "zh-CN"  # Set language to Chinese
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

# Global thread-safe event for controlling TTS playback
stop_tts_event = threading.Event()

# tts(text): Text-to-Speech function that takes a string and speaks it out loud via the computer's speakers.
def tts(text) -> None:
    global stop_tts_event
    stop_tts_event.clear()  # Reset the event before playback
    player_stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1, rate=24000, output=True)

    with openai.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="alloy",
        response_format="pcm",  # similar to WAV, but without a header chunk at the start.
        input=text,
    ) as response:
        for chunk in response.iter_bytes(chunk_size=1024):
            if stop_tts_event.is_set():  # Stop playback if the event is set
                break
            player_stream.write(chunk)
    player_stream.stop_stream()
    player_stream.close()

# askOpenAI(question): Send a question to the OpenAI GPT model and return the generated answer. (You can choose other versions of gpt models)
def askOpenAI(question):
    # Initialize the message with the system's role
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    # Append the user's question as a message
    messages.append({"role": "user", "content": question})
    
    # Call the OpenAI API  # gpt-3.5-turbo",
    completion = client.chat.completions.create(
        model="gpt-4-turbo" ,
        messages=messages
    )
    answer = completion.choices[0].message.content
    
    # Return the assistant's response
    return answer 


#Function: Recognize speech from default microphone
# · Use default microphone to synthesize speech
# · recognize_once_async：
#   Performs recognition in a non-blocking (asynchronous) mode. This will recognize a single utterance. The end of a single 
#   utterance is determined by listening for silence at the end or until a maximum of 15 seconds of audio is processed.
# speech to text
def recognize_from_microphone():
    try:
        time.sleep(0.1)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
        speech_recognition_result = speech_recognizer.recognize_once_async().get()
        
        if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return speech_recognition_result.text
        elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
            logging.warning(f"No speech could be recognized: {speech_recognition_result.no_match_details}")
            return ""
        elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_recognition_result.cancellation_details
            logging.error(f"Speech Recognition canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                logging.error(f"Error details: {cancellation_details.error_details}")
                logging.error("Did you set the speech resource key and region values?")
            return ""
    except Exception as e:
        logging.error(f"Error in speech recognition: {e}")
        return ""



if __name__ == '__main__':
    # Test the functions
    tts(' 你好,欢迎使用OpenAI语音助手。')
