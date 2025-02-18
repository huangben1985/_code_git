import cv2
import numpy as np
print(cv2.__version__)

dispW=640
dispH=480
flip=2

BW=75
BH=75
Xpos=10
Ypos=10
dx=2
dy=2


cam=cv2.VideoCapture(0)

while True:
    ret, frame = cam.read()
    #------------magic starts----------
    gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

    # b=cv2.split(frame)[0]
    # g=cv2.split(frame)[1]
    # r=cv2.split(frame)[2]
    b,g,r =cv2.split(frame)
    
    #print(frame[50,45,1])
    cv2.imshow('nanoCam',frame)
    cv2.moveWindow('nanoCam',0,0)
    cv2.imshow('blue',b)
    cv2.moveWindow('blue',710,0)
    cv2.imshow('green',g)
    cv2.moveWindow('green',0,500)
    cv2.imshow('red',r)
    cv2.moveWindow('red',710,500)


    if cv2.waitKey(1)==ord('q'):
        break
cam.release()
cv2.destroyAllWindows()
