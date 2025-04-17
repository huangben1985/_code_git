from vosk import Model, KaldiRecognizer
import pyaudio
from queue import Queue
from OpenAISpeech import askOpenAI,tts,stop_tts_event,recognize_from_microphone
import logging
import time
from threading import Thread
import json

# Configure logging to write to a file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("./log/vosk_playback.log", mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Initialize Vosk model
model = Model(r"./vosk-model-small-cn-0.22")

# Separate recognizers for different purposes
wake_word_recognizer = KaldiRecognizer(model, 16000)

class AudioManager:
    def __init__(self):
        self.mic = pyaudio.PyAudio()
        self.stream = None
        logging.info(self.mic.get_default_input_device_info())
        
    def __enter__(self):
        self.stream = self.mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4096)
        self.stream.start_stream()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.mic.terminate()

class AudioBuffer:
    def __init__(self, max_size=1000):
        self.buffer = []
        self.max_size = max_size
        
    def add(self, data):
        self.buffer.append(data)
        if len(self.buffer) > self.max_size:
            self.buffer.pop(0)
            
    def clear(self):
        self.buffer.clear()

msg_queue = Queue()
running = True
wake_words = ['小庄同学', '小张同学']

def continuous_listen(audio_manager):
    global running
    text = ''
    while running:
        try:
            data = audio_manager.stream.read(4096)
            if wake_word_recognizer.AcceptWaveform(data):
                result = json.loads(wake_word_recognizer.Result())
                text = result.get("text", "").strip().replace(" ", "")
            else:
                text = ''
            
            if text:
                # logging.info(f"Vosk heard: {text}")
                if any(kw.replace(" ", "") in text for kw in wake_words) or '停止' in text:
                    stop_tts_event.set()
            msg_queue.put(text)
            text = ''
        except Exception as e:
            logging.error(f"Error in continuous_listen: {e}")
            break

def thread_continuous_listen(audio_manager):
    t = Thread(target=continuous_listen, args=(audio_manager,), daemon=True)
    t.start()
    logging.info('Continuous listen thread started')
    return t

if __name__ == '__main__':
    audio_manager = None
    try:
        running = True
        with AudioManager() as audio_manager:
            thread = thread_continuous_listen(audio_manager)
            logging.info("Listening continuously...what can I do for you?")

            while running:
                if not msg_queue.empty():
                    msg = msg_queue.get()
                    if any(kw.replace(" ", "") in msg.replace(" ", "") for kw in wake_words):
                        stop_tts_event.clear()
                        msg = ''
                        tts('干嘛!')

                        collected_text = ''
                        try:
                            collected_text = recognize_from_microphone()
                            if collected_text:
                                collected_text = collected_text.strip().replace(" ", "")
                            
                            logging.info(f"Heard: {collected_text}")

                            if collected_text:
                                response = askOpenAI(collected_text)
                                tts(response)
                                logging.info(f"Response: {response}")
                            else:
                                logging.warning("No command was detected")
                                tts("抱歉，我沒有聽清楚")
                        except IOError as e:
                            logging.error(f"Audio input error: {e}")
                        except json.JSONDecodeError as e:
                            logging.error(f"JSON parsing error: {e}")
                        except Exception as e:
                            logging.error(f"Error processing message: {e}")
                    
                time.sleep(0.1)

    except KeyboardInterrupt:
        logging.info("Stopped listening. Exiting...")
        running = False
    except Exception as e:
        logging.error(f"Fatal error: {e}")
    finally:
        if audio_manager:
            try:
                audio_manager.stream.stop_stream()
                audio_manager.stream.close()
                audio_manager.mic.terminate()
            except Exception as e:
                logging.error(f"Error during cleanup: {e}")
