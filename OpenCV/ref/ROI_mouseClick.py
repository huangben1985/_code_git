import cv2
print(cv2.__version__)

goFlag = 0

def mouse_click(event,x,y,flags,params):
    global x1,y1,x2,y2
    global goFlag
    if event==cv2.EVENT_LBUTTONDOWN:
        x1=x
        y1=y
        goFlag=0
    if event==cv2.EVENT_LBUTTONUP:
        x2=x
        y2=y
        goFlag=1      

cv2.namedWindow('nanoCam')
cv2.setMouseCallback('nanoCam', mouse_click)

dispW=640
dispH=480
flip=2

#if you have a WEB cam, uncomment the next line
#(If it does not work, try setting to '1' instead of '0')
cam=cv2.VideoCapture(0)

cv2.namedWindow('nanoCam')

while True:
    ret, frame = cam.read()
    # Region of interest (ROI)
    
    cv2.imshow('nanoCam',frame)
    
    if goFlag==1:
        frame=cv2.rectangle(frame,(x1,y1),(x2,y2),(255,0,0),2)
        
        roi=frame[y1:y2,x1:x2]    
        cv2.imshow('copy ROI',roi)
        cv2.moveWindow('copy ROI',715,0)

    cv2.moveWindow('nanoCam',0,0)
    if cv2.waitKey(1)==ord('q'):
        break
cam.release()
cv2.destroyAllWindows()

