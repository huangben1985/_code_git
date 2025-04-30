from picamera2 import Picamera2, encoders
import time
import subprocess
from datetime import datetime
import RPi.GPIO as GPIO

# Set up GPIO
GPIO.setmode(GPIO.BCM)
BUTTON_PIN = 17  # Using GPIO 17, change this to your desired pin
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

camera = Picamera2()

# Set up video config
video_config = camera.create_video_configuration(main={"size": (1640, 1232)})
camera.configure(video_config)

# Create an encoder
encoder = encoders.H264Encoder()

print("Program started. Press button to toggle recording (press Ctrl+C to exit)")
is_recording = False
last_button_state = GPIO.HIGH

try:
    while True:
        current_button_state = GPIO.input(BUTTON_PIN)
        
        # Check for button press (falling edge)
        if current_button_state == GPIO.LOW and last_button_state == GPIO.HIGH:
            if not is_recording:
                # Start recording
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                h264_filename = f"video_{timestamp}.h264"
                
                camera.start_recording(encoder, h264_filename)
                is_recording = True
                print("Recording started...")
            else:
                # Stop recording
                camera.stop_recording()
                is_recording = False
                print("Recording stopped")
            
            # Wait for button release
            while GPIO.input(BUTTON_PIN) == GPIO.LOW:
                time.sleep(0.1)
        
        last_button_state = current_button_state
        time.sleep(0.1)  # Small delay to prevent CPU overuse

except KeyboardInterrupt:
    print("\nProgram stopped by user")
    if is_recording:
        camera.stop_recording()
finally:
    GPIO.cleanup()  # Clean up GPIO on exit
