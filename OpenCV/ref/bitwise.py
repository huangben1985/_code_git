import cv2
import numpy as np

# Print OpenCV version for reference
print(cv2.__version__)

# Define display dimensions
dispW = 640
dispH = 480
flip = 2  # Flip parameter (unused in current code)

# Create first mask image (img1): left half is white, right half is black
img1 = np.zeros((480, 640, 1), np.uint8)
img1[0:480, 0:320] = [255]  # Set left half to white

# Create second mask image (img2): small white rectangle in center
img2 = np.zeros((480, 640, 1), np.uint8)
img2[190:290, 270:370] = [255]  # Set center rectangle to white

# Perform bitwise operations between the two masks
bitAnd = cv2.bitwise_and(img1, img2)  # Shows overlapping white regions
bitOR = cv2.bitwise_or(img1, img2)    # Shows all white regions combined
bitXOR = cv2.bitwise_xor(img1, img2)  # Shows non-overlapping white regions

# Initialize video capture from default camera (index 0)
cam = cv2.VideoCapture(0)

# Main video processing loop
while True:
    # Read frame from camera
    ret, frame = cam.read()
    
    # Apply mask to frame using bitwise AND operation
    # This will only show the part of the frame where img2 is white
    frame = cv2.bitwise_and(frame, frame, mask=img2)
    
    # Display all windows
    # Main camera feed
    cv2.imshow('nanoCam', frame)
    cv2.moveWindow('nanoCam', 0, 0)
    
    # Display mask images
    cv2.imshow('img1', img1)
    cv2.moveWindow('img1', 715, 0)
    cv2.imshow('img2', img2)
    cv2.moveWindow('img2', 715, 550)
    
    # Display bitwise operation results
    cv2.imshow('AND', bitAnd)
    cv2.moveWindow('AND', 0, 550)
    cv2.imshow('OR', bitOR)
    cv2.moveWindow('OR', 1430, 0)
    cv2.imshow('XOR', bitXOR)
    cv2.moveWindow('XOR', 1430, 550)
    
    # Check for 'q' key to quit
    if cv2.waitKey(1) == ord('q'):
        break

# Clean up
cam.release()
cv2.destroyAllWindows()
