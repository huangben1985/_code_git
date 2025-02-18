import cv2
print(cv2.__version__)
dispW=640
dispH=480
flip=2

def nothing():
    pass

#if you have a WEB cam, uncomment the next line
#(If it does not work, try setting to '1' instead of '0')
cam=cv2.VideoCapture(0)
cv2.namedWindow('nanoCam')
cv2.createTrackbar('xVal','nanoCam',1,dispW,nothing)
cv2.createTrackbar('yVal','nanoCam',1,dispH,nothing)

while True:
    ret, frame = cam.read()
    # Region of interest (ROI)
    xRoi=cv2.getTrackbarPos('xVal','nanoCam')
    yRoi=cv2.getTrackbarPos('yVal','nanoCam')
    cv2.rectangle(frame,(xRoi,yRoi),(xRoi+200,yRoi+200),(255,0,0),2)
    # *.copy() in roi means make a copy from frames, so ROI is not alway
    # looking at the frame
    # roi, takes section of the image and modifty the section
    roi=frame[yRoi:yRoi+200,xRoi:xRoi+200].copy()
    roiGray = cv2.cvtColor(roi,cv2.COLOR_BGR2GRAY)
    roiGray = cv2.cvtColor(roiGray,cv2.COLOR_GRAY2BGR)
    frame[yRoi:yRoi+200,xRoi:xRoi+200] = roiGray

    cv2.imshow('ROI',roi)
    cv2.imshow('Gray',roiGray)
    cv2.imshow('nanoCam',frame)
    cv2.moveWindow('ROI',720,0)
    cv2.moveWindow('Gray',720,280)
    cv2.moveWindow('nanoCam',0,0)
    if cv2.waitKey(1)==ord('q'):
        break
cam.release()
cv2.destroyAllWindows()

