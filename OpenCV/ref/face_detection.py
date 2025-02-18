"""
An example of face detection using OpenCV.
"""
import cv2
import sys

# Load the Haar Cascade for face detection
casc_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(casc_path)

# Set the device for the camera (default: 0 for front camera)
device = 0
try:
    device = int(sys.argv[1])  # Use command-line argument for the camera device
except IndexError:
    pass

# Open the video capture
cap = cv2.VideoCapture(device, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Error: Cannot access the camera.")
    sys.exit()

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture frame.")
        break

    # Convert frame to grayscale (required for face detection)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Perform face detection
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Draw rectangles around detected faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # Display the resulting frame
    cv2.imshow('Face Detection', frame)

    # Exit the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close windows
cap.release()
cv2.destroyAllWindows()
