import cv2
import numpy as np

# Print OpenCV version for reference
print(cv2.__version__)

# Define display dimensions and animation parameters
dispW = 640
dispH = 480
flip = 2

# Logo size and initial position
BW = 75  # Box width
BH = 75  # Box height
Xpos = 10  # Initial X position
Ypos = 10  # Initial Y position
dx = 2    # X direction movement speed
dy = 2    # Y direction movement speed

# Load and prepare the OpenCV logo
PL = cv2.imread('ref/images/PL.jpg')
PL = cv2.resize(PL, (75, 75))  # Resize logo to box dimensions

# Convert logo to grayscale for mask creation
PLGray = cv2.cvtColor(PL, cv2.COLOR_BGR2GRAY)

# Create binary mask for logo
# Threshold at 20 - pixels below 20 become black (0), above become white (255)
_, BGMask = cv2.threshold(PLGray, 20, 255, cv2.THRESH_BINARY)

# Create inverted mask for background
FGMask = cv2.bitwise_not(BGMask)

# Create foreground by applying mask to logo
FG = cv2.bitwise_and(PL, PL, mask=BGMask)

# Create background color (gray)
img2 = np.zeros((75, 75, 1), np.uint8)
img2[0:75, 0:75] = [66]  # Set to gray value

# Initialize video capture
cam = cv2.VideoCapture(0)

# Main processing loop
while True:
    ret, frame = cam.read()
    
    # Process the region of interest (ROI)
    ROI = frame[Ypos:Ypos+BH, Xpos:Xpos+BW].copy()
    
    # Create masked foreground from ROI
    ROIBG = cv2.bitwise_and(ROI, ROI, mask=FGMask)
    
    # Create background for logo
    ROIINV = frame[Ypos:Ypos+BH, Xpos:Xpos+BW].copy()
    ROIINV = cv2.cvtColor(ROIINV, cv2.COLOR_BGR2GRAY)
    ROIINV = cv2.merge([ROIINV, ROIINV, img2])
    ROIINV = cv2.bitwise_and(ROIINV, ROIINV, mask=BGMask)
    
    # Combine foreground and background
    ROIBG = cv2.add(ROIBG, ROIINV)
    
    # Place combined image back into frame
    frame[Ypos:Ypos+BH, Xpos:Xpos+BW] = ROIBG
    
    # Display result
    cv2.imshow('nanoCam', frame)
    cv2.moveWindow('nanoCam', 0, 0)
    
    # Update logo position for animation
    Xpos = Xpos + dx
    Ypos = Ypos + dy
    
    # Bounce logo off window boundaries
    if Xpos > 638-BW or Xpos < 1:
        dx = -dx
    if Ypos > 478-BH or Ypos < 1:
        dy = -dy
    
    # Check for quit command
    if cv2.waitKey(1) == ord('q'):
        break

# Clean up
cam.release()
cv2.destroyAllWindows()
