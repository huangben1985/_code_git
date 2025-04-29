# pyintsaller --onefile --noconsole paint_app.py
# pyinstaller --noconsole --icon=app_icon.ico paint_app.py
# pyinstaller --noconsole --icon=app_icon.ico --add-data="icon.ico;." paint_app.py
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSizeGrip, QInputDialog, QDialog, QLineEdit
from PyQt5.QtWidgets import QPushButton, QSlider, QLabel, QColorDialog, QFontDialog
from PyQt5.QtCore import Qt, QPoint, QRect, QTimer
from PyQt5.QtGui import QPainter, QPen, QColor, QImage, QFont, QFontMetrics, QScreen
import sys
import cv2
import numpy as np
from datetime import datetime
import os

# Add new TitleBar class
class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Set fixed height for title bar
        self.setFixedHeight(35)
        
        # Create title bar widget with its own layout
        titleBar = QWidget()
        titleBar.setFixedHeight(35)
        titleBarLayout = QHBoxLayout(titleBar)
        titleBarLayout.setContentsMargins(0, 0, 0, 0)
        
        titleBar.setStyleSheet("""
            QWidget {
                background-color: gray;
                border: 1px solid DarkOrange;
            }
        """)
        
        # Create and add title to titleBar
        title = QLabel("Drawing On Screen")
        title.setStyleSheet("""
            QLabel {
                color: DarkOrange;
                font-family: "Comic Sans MS";
                font-size: 25px;
                font-weight: bold;
                width: 100%;
                border: 1px solid DarkOrange;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        titleBarLayout.addWidget(title)
        
        # Add titleBar to main layout
        layout.addWidget(titleBar)
        
        # Minimize button
        minimize_btn = QPushButton("−")
        minimize_btn.setFixedSize(50, 50)
        minimize_btn.clicked.connect(self.parent.showMinimized)
        minimize_btn.setStyleSheet("""
            QPushButton {
                background-color: gray;
                color: DarkOrange;
                font-size: 30px;
                border: 1px solid DarkOrange;
            }
            QPushButton:hover {
                background-color: #666666;
                color: white;
            }
        """)
        
        layout.addWidget(minimize_btn)
        
        # Close button
        close_btn = QPushButton("×")
        close_btn.setFixedSize(50, 50)
        close_btn.clicked.connect(self.parent.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: gray;
                color: DarkOrange;
                font-size: 30px;
                border: 1px solid DarkOrange;
            }
            QPushButton:hover {
                background-color: #ff0000;
                color: white;
            }
        """)
        
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        self.start = QPoint(0, 0)
        self.pressing = False
        
    def mousePressEvent(self, event):
        self.start = self.mapToGlobal(event.pos())
        self.pressing = True

    def mouseMoveEvent(self, event):
        if self.pressing:
            end = self.mapToGlobal(event.pos())
            movement = end - self.start
            self.parent.setGeometry(
                self.parent.x() + movement.x(),
                self.parent.y() + movement.y(),
                self.parent.width(),
                self.parent.height()
            )
            self.start = end

    def mouseReleaseEvent(self, event):
        self.pressing = False

class TextInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        self.setMinimumWidth(400)
        
        # Set dialog background and border
        self.setStyleSheet("""
            QDialog {
                background-color: rgba(255, 255, 255, 240);
                border: 1px solid #333333;
                border-radius: 5px;
            }
        """)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Add a label
        label = QLabel("Enter Text:")
        label.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 15px;
                font-weight: bold;
                margin-bottom: 5px;
                border: none;
                
            }
        """)
        layout.addWidget(label)
        
        # Create text input
        self.text_input = QLineEdit()
        self.text_input.setMinimumHeight(80)
        self.text_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #007bff;
            }
        """)
        
        # Add to layout
        layout.addWidget(self.text_input)
        
    def get_text(self):
        if self.exec_() == QDialog.Accepted:
            return self.text_input.text(), True
        return "", False
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.accept()
        elif event.key() == Qt.Key_Escape:
            self.reject()

class TextElement:
    def __init__(self, text, pos, font, color):
        self.text = text
        self.pos = pos
        self.font = font
        self.color = color
        self.rect = None
        self.update_rect()
    
    def update_rect(self):
        metrics = QFontMetrics(self.font)
        rect = metrics.boundingRect(self.text)
        self.rect = QRect(self.pos.x(), self.pos.y() - rect.height(), 
                         rect.width(), rect.height())
    
    def contains(self, point):
        return self.rect.contains(point)

class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        # self.setMinimumSize(1600, 900)  # Updated minimum size
        # Make widget background transparent
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.drawing = False
        self.last_point = QPoint()
        self.current_color = QColor(250, 0, 0)  # Default black
        self.brush_size = 2
        self.current_font = QFont('Arial', 12)
        self.text_mode = False
        self.text_elements = []
        self.dragging_text = None
        self.drag_offset = QPoint()
        self.is_hollow = False  # New property for hollow frame mode

        # Create frame widget with updated style
        self.frame = QWidget(self)
        self.frame.setStyleSheet("""
            QWidget {
                border: none; 
                border-radius: 2px;
                background-color: transparent;
            }
        """)
        
        # Initialize empty image
        self.image = None
        self.clear_canvas()
        
        # Add history for undo/redo
        self.history = []
        self.current_step = -1
        self.save_state()  # Save initial blank state
                

    def clear_canvas(self):
        self.image = QImage(self.size(), QImage.Format_ARGB32)
        self.image.fill(Qt.transparent)  # Make background transparent
        self.text_elements.clear()  # Clear text elements too
        self.update()

    def save_state(self):
        # Remove any redo states
        if self.current_step + 1 < len(self.history):
            self.history = self.history[:self.current_step + 1]
            
        # Save current state
        current_image = self.image.copy()
        current_texts = [TextElement(t.text, t.pos, t.font, t.color) for t in self.text_elements]
        self.history.append((current_image, current_texts))
        self.current_step += 1
        
    def undo(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.image, self.text_elements = self.history[self.current_step]
            self.image = self.image.copy()
            self.text_elements = [TextElement(t.text, t.pos, t.font, t.color) for t in self.text_elements]
            self.update()
            
    def redo(self):
        if self.current_step + 1 < len(self.history):
            self.current_step += 1
            self.image, self.text_elements = self.history[self.current_step]
            self.image = self.image.copy()
            self.text_elements = [TextElement(t.text, t.pos, t.font, t.color) for t in self.text_elements]
            self.update()

    def set_hollow_mode(self, is_hollow):
        self.is_hollow = is_hollow
        if is_hollow:
            self.setAttribute(Qt.WA_TransparentForMouseEvents)
        else:
            self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.update()

    def mousePressEvent(self, event):
        if self.is_hollow:
            # Forward the event to the window behind
            event.ignore()
            return
        if self.text_mode:
            dialog = TextInputDialog(self)
            dialog.move(event.globalPos())
            text, ok = dialog.get_text()
            if ok and text:
                text_elem = TextElement(text, event.pos(), 
                                      self.current_font, 
                                      self.current_color)
                self.text_elements.append(text_elem)
                self.update()
        else:
            # Check if clicking on existing text
            for text_elem in self.text_elements:
                if text_elem.contains(event.pos()):
                    self.dragging_text = text_elem
                    self.drag_offset = event.pos() - text_elem.pos
                    return
            
            # If not clicking text, handle normal drawing
            if event.button() == Qt.LeftButton:
                self.drawing = True
                self.last_point = event.pos()

    def mouseMoveEvent(self, event):
        if self.is_hollow:
            # Forward the event to the window behind
            event.ignore()
            return
        if self.dragging_text:
            self.dragging_text.pos = event.pos() - self.drag_offset
            self.dragging_text.update_rect()
            self.update()
        elif event.buttons() & Qt.LeftButton and self.drawing:
            painter = QPainter(self.image)
            painter.setPen(QPen(self.current_color, self.brush_size, 
                              Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(self.last_point, event.pos())
            self.last_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if self.is_hollow:
            # Forward the event to the window behind
            event.ignore()
            return
        if self.dragging_text or self.drawing:
            self.save_state()  # Save state after drawing or moving text
        self.dragging_text = None
        if event.button() == Qt.LeftButton:
            self.drawing = False

    def paintEvent(self, event):
        painter = QPainter(self)
        
        if self.is_hollow:
            # Draw hollow frame
            painter.setPen(QPen(QColor(0, 0, 0), 2, Qt.DashLine))
            painter.drawRect(0, 0, self.width() - 1, self.height() - 1)
        else:
            # Draw normal content
            painter.drawImage(0, 0, self.image)
            
            # Draw text elements
            for text_elem in self.text_elements:
                painter.setFont(text_elem.font)
                painter.setPen(QPen(text_elem.color))
                painter.drawText(text_elem.pos, text_elem.text)

    def resizeEvent(self, event):
        # Update frame size to match canvas
        self.frame.setGeometry(4, 4, self.width()-8, self.height()-8)  # Account for padding
        
        if self.image is None:
            self.image = QImage(self.size(), QImage.Format_ARGB32)
            self.image.fill(Qt.transparent)
        else:
            # Create new image with new size
            new_image = QImage(self.size(), QImage.Format_ARGB32)
            new_image.fill(Qt.transparent)
            
            # Draw old image onto new image
            painter = QPainter(new_image)
            painter.drawImage(0, 0, self.image)
            painter.end()
            
            # Replace old image with new image
            self.image = new_image

class PaintApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Paint App")
 
        # Set initial window size
        self.resize(1600, 900)

        # Initialize recording variables
        self.is_recording = False
        self.recording_timer = QTimer()
        self.recording_timer.timeout.connect(self.capture_frame)
        self.frames = []
        self.fps = 30
        
        # Create video directory if it doesn't exist
        self.video_dir = "video"
        if not os.path.exists(self.video_dir):
            os.makedirs(self.video_dir)

        # Create main widget and layout
        main_widget = QWidget()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # Create canvas first
        self.canvas = Canvas()
        
        # Define common button style
        self.BUTTON_STYLE = """
            QPushButton {
                color: black;
                background-color: DarkOrange;
                padding: 3px 10px;
                border-radius: 3px;
                min-height: 20px;
                height: 26px;
                border: none;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: DarkOrange;
                color: white;
            }
            QPushButton[active="true"] {
                background-color: DarkOrange;
                color: white;
                border: 1px solid white;
            }
            QPushButton[active="true"]:hover {
                background-color: rgb(255, 140, 0);
            }
        """
        
        # Update main widget style
        main_widget.setStyleSheet(f"""
            QWidget {{
                border: 1px solid DarkOrange;
                border-radius: 3px;
                background-color: rgba(0, 0, 0, 10);
            }}
            {self.BUTTON_STYLE}
            QSlider {{
                background-color: rgb(246, 247, 243);
            }}
            QSizeGrip {{
                background-color: transparent;
                width: 56px;
                height: 16px;
            }}
            QLabel {{
                font-weight: bold;
                font-size: 12px;
            }}
        """)
        
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Add title bar
        self.title_bar = TitleBar(self)
        
        # Create controls
        controls_layout = QHBoxLayout()
        
        # Text button
        self.text_btn = QPushButton("Add Text")
        self.text_btn.clicked.connect(self.toggle_text_mode)
        self.text_btn.setStyleSheet(self.BUTTON_STYLE)
        
        # Font button
        font_btn = QPushButton("Choose Font")
        font_btn.clicked.connect(self.change_font)
        font_btn.setStyleSheet(self.BUTTON_STYLE)
        # Color button
        color_btn = QPushButton("Choose Color")
        color_btn.clicked.connect(self.change_color)
        color_btn.setStyleSheet(self.BUTTON_STYLE)
        # Clear button
        clear_btn = QPushButton("Clear Canvas")
        clear_btn.clicked.connect(self.canvas.clear_canvas)
        clear_btn.setStyleSheet(self.BUTTON_STYLE)
        # Brush size slider label
        slider_label = QLabel("Brush Size:")
        slider_label.setStyleSheet("""
            QLabel {
                color: rgb(5, 5, 2);
                background-color: gray;
                padding: 1px 1px;
                border-radius: 2px;
                min-height: 10px;
                border: 1px solid DarkOrange;
            }
        """)
        
        # Add brush slider back
        self.brush_slider = QSlider(Qt.Horizontal)
        self.brush_slider.setMinimum(1)
        self.brush_slider.setMaximum(50)
        self.brush_slider.setValue(2)
        self.brush_slider.valueChanged.connect(self.change_brush_size)
        
        # Capture button
        capture_btn = QPushButton("Capture Screen")
        capture_btn.clicked.connect(self.capture_screen)
        capture_btn.setStyleSheet(self.BUTTON_STYLE)
        # Undo button
        undo_btn = QPushButton("↶ Undo")
        undo_btn.clicked.connect(self.canvas.undo)
        undo_btn.setStyleSheet(self.BUTTON_STYLE)
        # Redo button
        redo_btn = QPushButton("↷ Redo")
        redo_btn.clicked.connect(self.canvas.redo)
        redo_btn.setStyleSheet(self.BUTTON_STYLE)
        # Add record button
        self.record_btn = QPushButton("Record Screen")
        self.record_btn.clicked.connect(self.toggle_recording)
        self.record_btn.setStyleSheet(self.BUTTON_STYLE)
        # Add hollow frame toggle button
        self.hollow_btn = QPushButton("Show Frame")
        self.hollow_btn.clicked.connect(self.toggle_hollow_frame)
        self.hollow_btn.setStyleSheet(self.BUTTON_STYLE)
        # Add widgets to controls layout
        controls_layout.addWidget(self.text_btn)
        controls_layout.addWidget(font_btn)
        controls_layout.addWidget(color_btn)
        controls_layout.addWidget(clear_btn)
        controls_layout.addWidget(slider_label)
        controls_layout.addWidget(self.brush_slider)
        controls_layout.addWidget(capture_btn)
        controls_layout.addWidget(undo_btn)
        controls_layout.addWidget(redo_btn)
        controls_layout.addWidget(self.record_btn)
        controls_layout.addWidget(self.hollow_btn)
        controls_layout.addStretch()
        
        # Create bottom layout for resize grip
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        # Add size grip
        size_grip = QSizeGrip(self)
        bottom_layout.addWidget(size_grip)
        
        # Create controls frame with fixed height
        controls_frame = QWidget()
        controls_frame.setFixedHeight(50)
        controls_frame.setLayout(controls_layout)
        controls_frame.setStyleSheet("""
            QWidget {
                color: rgb(5, 5, 2);
                border: 1px solid DarkOrange;
                border-radius: 3px;
                background-color: gray;
                height: 20px;
                font-size: 15px;
            }
        """)
        
        # Add layouts to main layout
        layout.addWidget(self.title_bar)
        layout.addWidget(controls_frame)
        layout.addWidget(self.canvas, 1)  # Add stretch factor
        layout.addLayout(bottom_layout)
        
    def change_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.canvas.current_color = color
            
    def change_brush_size(self, size):
        self.canvas.brush_size = size

    def toggle_text_mode(self):
        self.canvas.text_mode = not self.canvas.text_mode
        # Update button appearance
        self.text_btn.setProperty("active", "true" if self.canvas.text_mode else "false")
        self.text_btn.style().unpolish(self.text_btn)
        self.text_btn.style().polish(self.text_btn)
        
    def change_font(self):
        font, ok = QFontDialog.getFont(self.canvas.current_font, self)
        if ok:
            self.canvas.current_font = font

    def capture_screen(self):
        # Get canvas position and size in global coordinates
        canvas_geo = self.canvas.geometry()
        canvas_pos = self.canvas.mapToGlobal(QPoint(0, 0))
        
        # Capture the screen area of just the canvas
        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(
            0,  # Window ID (0 means entire screen)
            canvas_pos.x(),  # X coordinate of canvas in screen coordinates
            canvas_pos.y(),  # Y coordinate of canvas in screen coordinates
            canvas_geo.width(),  # Width of canvas
            canvas_geo.height()  # Height of canvas
        )
        
        # Copy to clipboard
        clipboard = QApplication.clipboard()
        clipboard.setImage(screenshot.toImage())

    def toggle_recording(self):
        if not self.is_recording:
            # Start recording
            self.is_recording = True
            self.frames = []
            self.record_btn.setText("Stop Recording")
            self.record_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ff0000;
                    color: white;
                    padding: 3px 10px;
                    border-radius: 3px;
                    min-height: 20px;
                    height: 26px;
                    border: none;
                    font-weight: bold;
                    font-size: 15px;
                }
            """)
            self.recording_timer.start(1000 // self.fps)  # Start timer for 30fps
        else:
            # Stop recording
            self.is_recording = False
            self.recording_timer.stop()
            self.record_btn.setText("Record Screen")
            self.record_btn.setStyleSheet(self.BUTTON_STYLE)
            self.save_recording()

    def capture_frame(self):
        # Get canvas position and size in global coordinates
        canvas_geo = self.canvas.geometry()
        canvas_pos = self.canvas.mapToGlobal(QPoint(0, 0))
        
        # Capture the screen area
        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(
            0,
            canvas_pos.x(),
            canvas_pos.y(),
            canvas_geo.width(),
            canvas_geo.height()
        )
        
        # Convert QImage to numpy array
        image = screenshot.toImage()
        width = image.width()
        height = image.height()
        ptr = image.bits()
        ptr.setsize(image.byteCount())
        arr = np.array(ptr).reshape(height, width, 4)  # 4 = RGBA
        
        # Convert RGBA to BGR for OpenCV
        frame = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
        self.frames.append(frame)

    def save_recording(self):
        if not self.frames:
            return
            
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.video_dir, f"recording_{timestamp}.mp4")
        
        # Get frame dimensions
        height, width, _ = self.frames[0].shape
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(filename, fourcc, self.fps, (width, height))
        
        # Write frames to video
        for frame in self.frames:
            out.write(frame)
        
        out.release()
        self.frames = []  # Clear frames after saving

    def toggle_hollow_frame(self):
        self.canvas.set_hollow_mode(not self.canvas.is_hollow)
        self.hollow_btn.setText("Show Paint" if self.canvas.is_hollow else "Show Frame")
        self.hollow_btn.setProperty("active", "true" if self.canvas.is_hollow else "false")
        self.hollow_btn.style().unpolish(self.hollow_btn)
        self.hollow_btn.style().polish(self.hollow_btn)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PaintApp()
    window.setWindowFlags(window.windowFlags() | Qt.WindowStaysOnTopHint)
    window.show()
    sys.exit(app.exec_()) 