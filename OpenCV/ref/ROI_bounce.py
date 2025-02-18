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
xRoi=10
yRoi=10
frameSize =250
xstep=3
ystep=2

while True:
    ret, frame = cam.read()
    # Region of interest (ROI)
    frameGray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    frameGray = cv2.cvtColor(frameGray,cv2.COLOR_GRAY2BGR)
    cv2.rectangle(frameGray,(xRoi-1,yRoi-1),(xRoi+frameSize,yRoi+frameSize),(128,128,128),1)
    # 
    roi=frame[yRoi:yRoi+frameSize,xRoi:xRoi+frameSize].copy()
    # roiGray = cv2.cvtColor(roi,cv2.COLOR_BGR2GRAY)
    # roiGray = cv2.cvtColor(roiGray,cv2.COLOR_GRAY2BGR)
    
    frameGray[yRoi:yRoi+frameSize,xRoi:xRoi+frameSize] = roi

    cv2.imshow('nanoCam',frameGray)
    cv2.moveWindow('nanoCam',0,0)

    xRoi = xRoi + xstep
    yRoi = yRoi + ystep
    if xRoi > 639-frameSize or xRoi < 1:
        xstep = -xstep
    if yRoi > 479-frameSize or yRoi < 1:
        ystep = -ystep
    
    #print(xRoi, yRoi)

    if cv2.waitKey(1)==ord('q'):
        break
cam.release()
cv2.destroyAllWindows()

