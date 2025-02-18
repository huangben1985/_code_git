import cv2
print(cv2.__version__)
dispW=640
dispH=480
flip=2

def nothing():
    pass

#Uncomment These next Two Line for Pi Camera
#camSet='nvarguscamerasrc !  video/x-raw(memory:NVMM), width=3264, height=2464, format=NV12, framerate=21/1 ! nvvidconv flip-method='+str(flip)+' ! video/x-raw, width='+str(dispW)+', height='+str(dispH)+', format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink'
#cam= cv2.VideoCapture(camSet)
 
#Or, if you have a WEB cam, uncomment the next line
#(If it does not work, try setting to '1' instead of '0')
cam=cv2.VideoCapture(0)
cv2.namedWindow('nanoCam')
cv2.createTrackbar('xVal','nanoCam',0,dispW,nothing)
cv2.createTrackbar('yVal','nanoCam',0,dispH,nothing)
cv2.createTrackbar('circleR','nanoCam',25,dispH,nothing)

while True:
    ret, frame = cam.read()
    #------------magic starts----------
    xVal=cv2.getTrackbarPos('xVal','nanoCam')
    yVal=cv2.getTrackbarPos('yVal','nanoCam')
    circleR=cv2.getTrackbarPos('circleR','nanoCam')
    cv2.circle(frame,(xVal,yVal),circleR,(255,0,0),2)

    #------------magic ends------------
    cv2.imshow('nanoCam',frame)
    cv2.moveWindow('nanoCam',0,0)
    if cv2.waitKey(1)==ord('q'):
        break
cam.release()
cv2.destroyAllWindows()

