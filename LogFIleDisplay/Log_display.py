import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
from datetime import datetime


class LogHandler(FileSystemEventHandler):
    def __init__(self, text_widget, status_label):
        self.text_widget = text_widget
        self.status_label = status_label
        self.last_content = ""
        self.last_size = 0
        self.is_connected = False
        self.retry_count = 0
        self.max_retries = 3
        self.log_path = None
        
    def set_log_path(self, new_path):
        self.log_path = new_path
        self.check_connection()
        
    def check_connection(self):
        if not self.log_path:
            self.status_label.config(text="No file selected. Please select a file to monitor.")
            return False
            
        try:
            # Try to access the file
            if not os.path.exists(self.log_path):
                self.is_connected = False
                self.status_label.config(text="Error: File not found. Please check the path.")
                return False
            
            # Try to read the file
            try:
                with open(self.log_path, 'r', encoding='utf-8') as file:
                    file.read(1)  # Just read one character to test access
            except Exception as e:
                self.status_label.config(text=f"File access error: {str(e)}")
                return False

            self.is_connected = True
            self.retry_count = 0
            self.status_label.config(text=f"Monitoring: {self.log_path}")
            return True
        except Exception as e:
            self.is_connected = False
            self.status_label.config(text=f"Connection Error: {str(e)}")
            return False
        
    def read_file(self):
        if not self.log_path:
            return "No file selected. Please select a file to monitor."
            
        if not self.is_connected:
            if self.retry_count < self.max_retries:
                self.retry_count += 1
                if self.check_connection():
                    return self.read_file()
            return "Error: Cannot access file. Please check your connection and try again."
        
        try:
            # Get file size
            current_size = os.path.getsize(self.log_path)
            
            # If file size is smaller than last size, it was probably cleared
            if current_size < self.last_size:
                self.last_content = ""
            
            self.last_size = current_size
            
            with open(self.log_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            self.is_connected = False
            return "Error: File not found at the specified location."
        except PermissionError:
            self.is_connected = False
            return "Error: Permission denied. Please check your access rights."
        except Exception as e:
            self.is_connected = False
            return f"Error reading file: {str(e)}"

    def on_modified(self, event):
        if self.log_path and event.src_path.replace('\\', '/').endswith(self.log_path.replace('\\', '/')):
            new_content = self.read_file()
            if new_content != self.last_content:
                # Get only the new content
                if self.last_content in new_content:
                    new_lines = new_content[len(self.last_content):]
                else:
                    new_lines = new_content
                
                # Add timestamp to new lines
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.text_widget.insert(tk.END, f"\n[{timestamp}] New content:\n{new_lines}")
                self.text_widget.see(tk.END)  # Auto-scroll to bottom
                self.last_content = new_content

class LogDisplayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Monitor")
        self.root.geometry("1200x800")
        
        # Create main frame
        main_frame = tk.Frame(root)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Create text widget with larger font
        self.text_widget = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=('Consolas', 10))
        self.text_widget.pack(expand=True, fill='both')
        
        # Add status label with connection status
        self.status_label = tk.Label(root, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create button frame
        button_frame = tk.Frame(root)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        
        # Add buttons
        select_button = tk.Button(button_frame, text="Select File", command=self.select_file)
        select_button.pack(side=tk.LEFT, padx=5)
        
        refresh_button = tk.Button(button_frame, text="Refresh", command=self.refresh_content)
        refresh_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = tk.Button(button_frame, text="Clear Display", command=self.clear_display)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Initialize file handler and observer
        self.event_handler = LogHandler(self.text_widget, self.status_label)
        self.observer = Observer()
        
        # Start periodic connection check
        self.check_connection_periodically()
        
        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Prompt for file selection
        self.select_file()
    
    def select_file(self):
        try:
            # Open file browser dialog
            path = filedialog.askopenfilename(
                title="Select File to Monitor",
                filetypes=(("All files", "*.*"),)
            )
            if path:
                self.event_handler.set_log_path(path)
                self.start_monitoring()
                self.refresh_content()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to select file: {str(e)}")
    
    def start_monitoring(self):
        try:
            # Stop existing observer if any
            if hasattr(self, 'observer') and self.observer.is_alive():
                self.observer.stop()
                self.observer.join()
            
            # Start new observer
            self.observer = Observer()
            self.observer.schedule(self.event_handler, path=os.path.dirname(self.event_handler.log_path), recursive=False)
            self.observer.start()
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to start monitoring: {str(e)}")
    
    def check_connection_periodically(self):
        if self.event_handler.check_connection():
            self.root.after(5000, self.check_connection_periodically)  # Check every 5 seconds
        else:
            self.root.after(1000, self.check_connection_periodically)  # Check more frequently when disconnected
    
    def refresh_content(self):
        new_content = self.event_handler.read_file()
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(tk.END, new_content)
        self.text_widget.see(tk.END)  # Auto-scroll to bottom
        self.event_handler.last_content = new_content
    
    def clear_display(self):
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(tk.END, "Display cleared. New content will appear here.\n")
    
    def on_closing(self):
        if hasattr(self, 'observer') and self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = LogDisplayApp(root)
    root.mainloop() 