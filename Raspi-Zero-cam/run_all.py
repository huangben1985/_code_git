import subprocess
import sys
import time
import signal
import os

def run_scripts():
    # Start both scripts as subprocesses
    app_process = subprocess.Popen([sys.executable, "app.py"])
    web_process = subprocess.Popen([sys.executable, "web_server.py"])
    
    print("Started both applications:")
    print("- Camera recording app")
    print("- Web server (access at http://localhost:5000)")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping applications...")
        # Terminate both processes
        app_process.terminate()
        web_process.terminate()
        # Wait for them to finish
        app_process.wait()
        web_process.wait()
        print("Applications stopped.")

if __name__ == "__main__":
    run_scripts() 