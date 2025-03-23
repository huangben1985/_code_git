import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np

def list_input_devices():
    print("Available input devices:")
    for i, device in enumerate(sd.query_devices()):
        if device['max_input_channels'] > 0:
            print(f"{i}: {device['name']}")

def record_audio(device_index, duration=5, sample_rate=44100):
    print(f"\nRecording for {duration} seconds...")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate,
                        channels=1, dtype='int16', device=device_index)
    sd.wait()
    print("Recording complete.")
    return audio_data, sample_rate

def play_audio(audio_data, sample_rate):
    print("\nPlaying back the recorded audio...")
    sd.play(audio_data, samplerate=sample_rate)
    sd.wait()

def save_audio(filename, audio_data, sample_rate):
    wav.write(filename, sample_rate, audio_data)
    print(f"Audio saved to {filename}")

def main():
    list_input_devices()
    device_index = int(input("\nEnter the input device index to use: "))
    duration = int(input("Enter duration to record (seconds): "))
    
    audio_data, sample_rate = record_audio(device_index, duration)
    play_audio(audio_data, sample_rate)
    
    save = input("Do you want to save the audio? (y/n): ").strip().lower()
    if save == 'y':
        save_audio("recorded_audio.wav", audio_data, sample_rate)

if __name__ == "__main__":
    main()
