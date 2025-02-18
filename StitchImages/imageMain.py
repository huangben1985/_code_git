import cv2
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os
from datetime import datetime
import sys

class ImageStitcher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.images = []
        self.current_count = 0
        self.max_images = 9
        self.selected_image_index = None
        self.selected_popup = None
        self.current_camera = 0
        
        # Get the application path
        if getattr(sys, 'frozen', False):
            self.app_path = os.path.dirname(sys.executable)
        else:
            self.app_path = os.path.dirname(os.path.abspath(__file__))
        
        # Create directories
        self.image_dir = os.path.join(self.app_path, "captured_images")
        self.output_dir = os.path.join(self.app_path, "stitched_outputs")
        for directory in [self.image_dir, self.output_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
        
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        
        # Setup UI
        self.setWindowTitle("Image Stitcher")
        self.setGeometry(100, 100, 1000, 900)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # Left panel for buttons
        left_widget = QWidget()
        left_widget.setFixedWidth(150)  # Set fixed width for left panel
        left_panel = QVBoxLayout(left_widget)
        left_panel.setContentsMargins(5, 5, 5, 5)  # Reduce margins
        main_layout.addWidget(left_widget)
        
        # Right panel for preview and thumbnails
        right_widget = QWidget()
        right_panel = QVBoxLayout(right_widget)
        main_layout.addWidget(right_widget)
        
        # Camera selection in one row
        camera_widget = QWidget()
        camera_layout = QHBoxLayout(camera_widget)
        camera_layout.setContentsMargins(5, 5, 5, 5)
        camera_layout.setSpacing(5)
        
        camera_label = QLabel("Camera:")
        camera_label.setFixedWidth(45)
        camera_layout.addWidget(camera_label)
        
        self.camera_combo = QComboBox()
        self.camera_combo.addItems([str(i) for i in range(5)])
        self.camera_combo.currentIndexChanged.connect(self.change_camera)
        self.camera_combo.setFixedWidth(40)
        camera_layout.addWidget(self.camera_combo)
        
        left_panel.addWidget(camera_widget)
        
        # Make buttons smaller and uniform size
        button_style = """
            QPushButton {
                padding: 5px;
                min-height: 25px;
                min-width: 120px;
                max-width: 120px;
            }
        """
        
        # Control buttons
        self.capture_btn = QPushButton("Capture Image")
        self.capture_btn.setStyleSheet(button_style)
        self.capture_btn.clicked.connect(self.capture_image)
        left_panel.addWidget(self.capture_btn)
        
        # Add Import button after Capture button
        self.import_btn = QPushButton("Import Image")
        self.import_btn.setStyleSheet(button_style)
        self.import_btn.clicked.connect(self.import_image)
        left_panel.addWidget(self.import_btn)
        
        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.setStyleSheet(button_style)
        self.delete_btn.clicked.connect(self.delete_selected_image)
        self.delete_btn.setEnabled(False)
        left_panel.addWidget(self.delete_btn)
        
        self.retake_btn = QPushButton("Retake Selected")
        self.retake_btn.setStyleSheet(button_style)
        self.retake_btn.clicked.connect(self.retake_selected_image)
        self.retake_btn.setEnabled(False)
        left_panel.addWidget(self.retake_btn)
        
        self.reset_btn = QPushButton("Reset All")
        self.reset_btn.setStyleSheet(button_style)
        self.reset_btn.clicked.connect(self.reset_all)
        left_panel.addWidget(self.reset_btn)
        
        self.stitch_btn = QPushButton("Stitch Images")
        self.stitch_btn.setStyleSheet(button_style)
        self.stitch_btn.clicked.connect(self.stitch_images)
        self.stitch_btn.setEnabled(False)
        left_panel.addWidget(self.stitch_btn)
        
        self.status_label = QLabel(f"Images captured: 0/{self.max_images}")
        left_panel.addWidget(self.status_label)
        
        left_panel.addStretch()
        
        # Preview
        preview_group = QGroupBox("Camera Preview")
        preview_layout = QVBoxLayout()
        self.preview_label = QLabel()
        preview_layout.addWidget(self.preview_label)
        preview_group.setLayout(preview_layout)
        right_panel.addWidget(preview_group)
        
        # Thumbnails
        self.thumbnail_widget = QWidget()
        self.thumbnail_layout = QGridLayout(self.thumbnail_widget)
        right_panel.addWidget(self.thumbnail_widget)
        
        # Start timer for camera preview
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_preview)
        self.timer.start(30)  # Update every 30ms
    
    def update_preview(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.resize(frame, (640, 480))
            image = self.convert_cv_qt(frame)
            self.preview_label.setPixmap(image)
    
    def convert_cv_qt(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(convert_to_Qt_format)
    
    def capture_image(self):
        ret, frame = self.cap.read()
        if ret:
            # Save image to file
            image_path = os.path.join(self.image_dir, f"image_{self.current_count + 1}.jpg")
            cv2.imwrite(image_path, frame)
            
            self.images.append(frame)
            self.current_count += 1
            self.status_label.setText(f"Images captured: {self.current_count}/{self.max_images}")
            self.update_thumbnails()
            
            if self.current_count >= 2: #== self.max_images:
                #self.capture_btn['state'] = 'disabled'
                self.stitch_btn.setEnabled(True)
                #messagebox.showinfo("Complete", "All images captured! You can now stitch them.")
    
    def update_thumbnails(self):
        # Clear existing thumbnails
        for widget in self.thumbnail_widget.findChildren(QPushButton):
            widget.deleteLater()
        
        # Create new thumbnails
        for i, img in enumerate(self.images):
            # Create button with thumbnail
            btn = QPushButton()
            # Set different border style for selected image
            if i == self.selected_image_index:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: 3px solid red;
                        padding: 2px;
                    }
                    QPushButton:hover {
                        border: 3px solid orange;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: 2px solid gray;
                        padding: 2px;
                    }
                    QPushButton:hover {
                        border: 2px solid blue;
                    }
                """)
            btn.setFixedSize(160, 120)
            
            # Calculate row and column for grid layout
            row = i // 4
            col = i % 4
            
            # Create thumbnail
            thumbnail = cv2.resize(img, (160, 120))
            thumbnail = self.convert_cv_qt(thumbnail)
            
            # Keep a reference to prevent garbage collection
            if not hasattr(self, 'thumbnail_refs'):
                self.thumbnail_refs = []
            self.thumbnail_refs.append(thumbnail)
            
            icon = QIcon(thumbnail)
            btn.setIcon(icon)
            btn.setIconSize(QSize(156, 116))  # Slightly smaller to account for border
            btn.clicked.connect(lambda checked, index=i: self.select_image(index))
            self.thumbnail_layout.addWidget(btn, row, col)
    
    def select_image(self, index):
        self.selected_image_index = index
        self.delete_btn.setEnabled(True)
        self.retake_btn.setEnabled(True)
        
        # Update thumbnails to show selection
        self.update_thumbnails()
        
        # Close existing popup if it exists
        if self.selected_popup is not None:
            self.selected_popup.close()
        
        # Create popup window for selected image
        self.selected_popup = QDialog(self)
        self.selected_popup.setWindowTitle(f"Image {index + 1}")
        
        # Create layout for popup
        layout = QVBoxLayout(self.selected_popup)
        
        # Show selected image
        selected_frame = self.images[index]
        selected_frame = cv2.resize(selected_frame, (640, 480))
        selected_image = self.convert_cv_qt(selected_frame)
        
        # Create canvas in popup window
        canvas = QLabel()
        canvas.setPixmap(selected_image)
        canvas.setAlignment(Qt.AlignCenter)
        canvas.setStyleSheet("background-color: black;")
        layout.addWidget(canvas)
        
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.selected_popup.close)
        close_btn.setFixedWidth(100)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Set fixed size and center the window
        self.selected_popup.setFixedSize(660, 560)
        self.selected_popup.move(
            self.x() + (self.width() - self.selected_popup.width()) // 2,
            self.y() + (self.height() - self.selected_popup.height()) // 2
        )
        self.selected_popup.show()
    
    def delete_selected_image(self):
        if self.selected_image_index is not None:
            # Delete image file
            image_path = os.path.join(self.image_dir, f"image_{self.selected_image_index + 1}.jpg")
            if os.path.exists(image_path):
                os.remove(image_path)
            
            # Rename remaining files to maintain sequence
            for i in range(self.selected_image_index + 1, self.current_count):
                old_path = os.path.join(self.image_dir, f"image_{i + 1}.jpg")
                new_path = os.path.join(self.image_dir, f"image_{i}.jpg")
                if os.path.exists(old_path):
                    os.rename(old_path, new_path)
            
            self.images.pop(self.selected_image_index)
            self.current_count -= 1
            self.selected_image_index = None
            self.delete_btn.setEnabled(False)
            self.retake_btn.setEnabled(False)
            self.capture_btn.setEnabled(True)
            self.status_label.setText(f"Images captured: {self.current_count}/{self.max_images}")
            self.update_thumbnails()
    
    def retake_selected_image(self):
        if self.selected_image_index is not None:
            # Store the index before deleting
            index_to_retake = self.selected_image_index
            
            # Delete existing image file
            image_path = os.path.join(self.image_dir, f"image_{index_to_retake + 1}.jpg")
            if os.path.exists(image_path):
                os.remove(image_path)
            
            self.images.pop(self.selected_image_index)
            self.current_count -= 1
            self.selected_image_index = None
            self.delete_btn.setEnabled(False)
            self.retake_btn.setEnabled(False)
            
            # Capture new image and save with same index
            ret, frame = self.cap.read()
            if ret:
                cv2.imwrite(image_path, frame)
                self.images.insert(index_to_retake, frame)
                self.current_count += 1
            
            self.status_label.setText(f"Images captured: {self.current_count}/{self.max_images}")
            self.update_thumbnails()
    
    def reset_all(self):
        # Delete all images in the directory
        for file in os.listdir(self.image_dir):
            file_path = os.path.join(self.image_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        self.images = []
        self.current_count = 0
        self.selected_image_index = None
        self.capture_btn.setEnabled(True)
        self.delete_btn.setEnabled(False)
        self.retake_btn.setEnabled(False)
        self.stitch_btn.setEnabled(False)
        self.status_label.setText(f"Images captured: 0/{self.max_images}")
        self.update_thumbnails()
    
    def stitch_images(self):
        try:
            # Create a stitcher object
            stitcher = cv2.Stitcher.create()
            
            # Convert images list to tuple for stitching
            status, stitched = stitcher.stitch(self.images)
            
            if status == cv2.Stitcher_OK:
                # Generate timestamp for filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"stitched_{timestamp}.jpg"
                output_path = os.path.join(self.output_dir, output_filename)
                
                # Save the stitched image
                cv2.imwrite(output_path, stitched)
                
                # Create popup window for stitched image
                popup = QDialog(self)
                popup.setWindowTitle("Stitched Image")
                layout = QVBoxLayout(popup)
                
                # Resize stitched image to fit screen if too large
                h, w = stitched.shape[:2]
                aspect = w / h
                
                # Use 80% of screen size as maximum
                max_width = int(self.width() * 0.8)
                max_height = int(self.height() * 0.8)
                
                if w > max_width:
                    w = max_width
                    h = int(w / aspect)
                if h > max_height:
                    h = max_height
                    w = int(h * aspect)
                
                stitched_resized = cv2.resize(stitched, (w, h))
                stitched_image = self.convert_cv_qt(stitched_resized)
                
                # Create canvas and display image
                canvas = QLabel()
                canvas.setPixmap(stitched_image)
                canvas.setAlignment(Qt.AlignCenter)
                canvas.setStyleSheet("background-color: black;")
                layout.addWidget(canvas)
                
                # Add close button
                close_btn = QPushButton("Close")
                close_btn.clicked.connect(popup.close)
                close_btn.setFixedWidth(100)
                button_layout = QHBoxLayout()
                button_layout.addStretch()
                button_layout.addWidget(close_btn)
                button_layout.addStretch()
                layout.addLayout(button_layout)
                
                # Set size and center the window
                popup.setFixedSize(w + 20, h + 60)
                popup.move(
                    self.x() + (self.width() - popup.width()) // 2,
                    self.y() + (self.height() - popup.height()) // 2
                )
                popup.show()
                
                QMessageBox.information(self, "Success", 
                    f"Images stitched successfully! Saved as '{output_filename}' in {self.output_dir} folder")
            else:
                QMessageBox.critical(self, "Error", "Failed to stitch images!")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def change_camera(self, camera_index):
        # Release current camera
        if self.cap is not None:
            self.cap.release()
        
        # Try to open new camera
        self.cap = cv2.VideoCapture(int(camera_index))
        if not self.cap.isOpened():
            messagebox.showerror("Error", f"Could not open camera {camera_index}")
            # Revert to previous camera
            self.camera_combo.setCurrentText(str(self.current_camera))
            self.cap = cv2.VideoCapture(self.current_camera)
        else:
            self.current_camera = int(camera_index)
    
    def import_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        )
        
        if file_path:
            try:
                # Read the image
                img = cv2.imread(file_path)
                if img is None:
                    raise Exception("Failed to load image")
                
                # Save image to our directory
                new_path = os.path.join(self.image_dir, f"image_{self.current_count + 1}.jpg")
                cv2.imwrite(new_path, img)
                
                # Add to our list
                self.images.append(img)
                self.current_count += 1
                self.status_label.setText(f"Images captured: {self.current_count}/{self.max_images}")
                self.update_thumbnails()
                
                if self.current_count >= 2:
                    self.stitch_btn.setEnabled(True)
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import image: {str(e)}")
    
    def run(self):
        self.show()

def main():
    app = QApplication(sys.argv)
    window = ImageStitcher()
    window.run()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
