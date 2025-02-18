# 在文件开头添加新的导入
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import logging

# ... existing imports ...

class VoiceAssistantGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("语音助手")
        self.root.geometry("600x400")
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 状态显示
        self.status_var = tk.StringVar(value="准备就绪")
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var)
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # 日志显示区域
        self.log_area = scrolledtext.ScrolledText(self.main_frame, height=15, width=60)
        self.log_area.grid(row=1, column=0, pady=10, sticky=(tk.W, tk.E))
        
        # 控制按钮
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=2, column=0, pady=10)
        
        self.start_button = ttk.Button(self.button_frame, text="开始", command=self.start_listening)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(self.button_frame, text="停止", command=self.stop_listening)
        self.stop_button.grid(row=0, column=1, padx=5)
        
        # 配置日志处理
        self.setup_logging()
        
    def setup_logging(self):
        # 创建自定义日志处理器
        class GUILogHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
                
            def emit(self, record):
                msg = self.format(record)
                def append():
                    self.text_widget.insert(tk.END, msg + '\n')
                    self.text_widget.see(tk.END)
                self.text_widget.after(0, append)
        
        # 添加GUI日志处理器
        gui_handler = GUILogHandler(self.log_area)
        gui_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        logging.getLogger().addHandler(gui_handler)
    
    def start_listening(self):
        global running
        running = True
        self.status_var.set("正在监听...")
        self.start_button.state(['disabled'])
        self.stop_button.state(['!disabled'])
        
        # 在新线程中启动语音识别
        thread = thread_continuous_listen()
        
        # 启动主处理循环
        def main_loop():
            try:
                while running:
                    if not msg_queue.empty():
                        msg = msg_queue.get()
                        if any(word in msg for word in TRIGGER_WORDS):
                            self.status_var.set("正在处理...")
                            tts(' 我在 ')
                            msg1 = recognize_from_microphone()
                            logging.info(f"听到: {msg1}")
                            try:
                                response = askOpenAI(msg1)
                                tts(response)
                                logging.info(f"回复: {response}")
                            except Exception as e:
                                logging.error(f"处理消息时出错: {e}")
                            finally:
                                self.status_var.set("正在监听...")
                        elif any(word in msg for word in STOP_WORDS):
                            stop_tts_event.set()
                    
                    time.sleep(0.1)
            except Exception as e:
                logging.error(f"主循环错误: {e}")
                self.stop_listening()
        
        threading.Thread(target=main_loop, daemon=True).start()
    
    def stop_listening(self):
        global running
        running = False
        self.status_var.set("已停止")
        self.start_button.state(['!disabled'])
        self.stop_button.state(['disabled'])
        stop_tts_event.set()
    
    def run(self):
        self.root.mainloop()

# 修改主程序入口
if __name__ == '__main__':
    try:
        app = VoiceAssistantGUI()
        app.run()
    except Exception as e:
        logging.error(f"程序异常退出: {e}")