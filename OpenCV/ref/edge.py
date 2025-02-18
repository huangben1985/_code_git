import cv2
import sys

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
    cv2.imshow('Frame', frame)
    # Convert frame to grayscale (required for face detection)
    img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imshow('Gray', img_gray)
    img_blur = cv2.GaussianBlur(img_gray, (3,3), 0)
    cv2.imshow('Blur', img_blur)

    # Sobel Edge Detection
    sobelx = cv2.Sobel(src=img_blur, ddepth=cv2.CV_64F, dx=1, dy=0, ksize=5) # Sobel Edge Detection on the X axis
    sobely = cv2.Sobel(src=img_blur, ddepth=cv2.CV_64F, dx=0, dy=1, ksize=5) # Sobel Edge Detection on the Y axis
    sobelxy = cv2.Sobel(src=img_blur, ddepth=cv2.CV_64F, dx=1, dy=1, ksize=5) # Combined X and Y Sobel Edge Detection
    # Display Sobel Edge Detection Images
    cv2.imshow('Sobel X', sobelx)
    # cv2.waitKey(0)
    cv2.imshow('Sobel Y', sobely)
    # cv2.waitKey(0)
    cv2.imshow('Sobel X Y using Sobel() function', sobelxy)
    # cv2.waitKey(0)
    
    # Canny Edge Detection
    edges = cv2.Canny(image=img_blur, threshold1=100, threshold2=200) # Canny Edge Detection

    # Display the resulting frame
    cv2.imshow('Edge Detection', edges)

    # Exit the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close windows
cap.release()
cv2.destroyAllWindows()
