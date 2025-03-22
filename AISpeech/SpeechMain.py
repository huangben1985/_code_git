#https://alphacephei.com/vosk/models
#lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
#pip install azure-cognitiveservices-speech
#pip install openai
#pip install vosk
#pip install pyaudio 
#pip install python-dotenv


from vosk import Model, KaldiRecognizer
import pyaudio
from queue import Queue
from OpenAISpeech import askOpenAI,tts,recognize_from_microphone,stop_tts_event
import logging
import time
from threading import Thread

# Configure logging to write to a file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("./log/vosk_playback.log", mode='a', encoding='utf-8'),  # Log file
        logging.StreamHandler()  # Optional: Also log to console
    ]
)

model = Model(r"./vosk-model-small-cn-0.22")
#model = Model(r"./vosk-model-en-us-0.22")
# You can also specify the possible word list
#rec = KaldiRecognizer(model, 16000, "zero oh one two three four five six seven eight nine")

recognizer = KaldiRecognizer(model, 16000)
mic = pyaudio.PyAudio()
logging.info(mic.get_default_input_device_info())
stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4096)
stream.start_stream()
msg_queue = Queue()
running = True


def continuous_listen():
    global running
    text = ''  # Initial text
    while running:
        try:
            # Listen for audio
            data = stream.read(4096)
            if recognizer.AcceptWaveform(data):
                text = recognizer.Result()[14:-3] #.replace(" ", "")
            else:
                text = ''
            msg_queue.put(text)
            
            if text:
                logging.info(f"Vosk heard: {text}")
                if '小奔奔' in text or '停止' in text:
                    #print('stop')
                    stop_tts_event.set()
            text = ''
        except Exception as e:
            logging.error(f"Error: {e}")
            # 建议添加具体的异常类型，而不是捕获所有异常
            # 建议添加最大重试次数
            try:
                stream.stop_stream()
                stream.close()
                mic.terminate()
            except Exception as cleanup_error:  # 添加具体的异常处理
                logging.error(f"Cleanup error: {cleanup_error}")

def thread_continuous_listen():
    t = Thread(target=continuous_listen, daemon=True)
    t.start()
    logging.info('Continuous listen thread started')
    return t

# Main logic
if __name__ == '__main__':
    try:
        running = True
        thread = thread_continuous_listen()
        logging.info("Listening continuously...what can I do for you?")

        while running:
            if not msg_queue.empty():
                msg = msg_queue.get()
                if '小本本' in msg or '小笨笨' in msg or '小奔奔' in msg or stop_tts_event.set():
                    # Example: Respond using TTS or pass message to OpenAI for processing
                    tts(' 我在 ')
                    #print(msg)
                    msg1 = recognize_from_microphone()  # Recognize user query           
                    logging.info(f"Heard: {msg1}")
                    try:
                        response = askOpenAI(msg1)  # Assuming askOpenAI is a valid function
                        tts(response)  # Assuming tts function reads the response
                        logging.info(f"Response: {response}")
                    except Exception as e:
                        logging.error(f"Error processing message: {e}")
            
            time.sleep(0.1)  # Avoid busy-waiting

    except KeyboardInterrupt:
        logging.info("Stopped listening. Exiting...")
        running = False  # Set the flag to False to exit the loop
    except Exception as e:
        logging.error(f"Break: {e}")
