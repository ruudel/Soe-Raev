import cv2
import cv2.cv as cv
import numpy as np
from time import time
 
# create video capture
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)
cap.set(6, 60)
width, height = cap.get(3), cap.get(4)
 
minhue = 0
maxhue = 255
minsat = 0
maxsat = 255
minval = 0
maxval = 255
 
minvalues = np.array((minhue,minsat,minval), np.uint8)
maxvalues = np.array((maxhue,maxsat,maxval), np.uint8)
kernel = np.ones((8,8), 'uint8')
#print minhue,maxhue,minsat,maxsat,minval,maxval
 
def changeMinHue(n):
    global minvalues
    minvalues[0] = n
     
 
def changeMaxHue(n):
    global maxvalues
    maxvalues[0] = n
     
 
def changeMinSat(n):
    global minvalues
    minvalues[1] = n
 
def changeMaxSat(n):
    global maxvalues
    maxvalues[1] = n
 
def changeMinVal(n):
    global minvalues
    minvalues[2] = n
 
def changeMaxVal(n):
    global maxvalues
    maxvalues[2] = n
 
 
cv2.namedWindow('HSV')
cv.CreateTrackbar("Huehuehue", 'HSV', minhue, 180, changeMinHue)
cv.CreateTrackbar("Maxhue", 'HSV', maxhue, 180, changeMaxHue)
cv.CreateTrackbar("Minsat", 'HSV', minsat, 255, changeMinSat)
cv.CreateTrackbar("Maxsat", 'HSV', maxsat, 255, changeMaxSat)
cv.CreateTrackbar("Minval", 'HSV', minval, 255, changeMinVal)
cv.CreateTrackbar("Maxval", 'HSV', maxval, 255, changeMaxVal)
              
start_time = time()
times = [0, 0, 0, 0, 0, 0, 0]
while(1):
    times[0] = (times[0] + (time() - start_time)) / 2
    # read the frames
    _,frame = cap.read()
    times[1] = (times[1] + (time() - start_time) - times[0]) / 2
 
     
    # convert to hsv and find range of colors
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    thresh = cv2.inRange(hsv,minvalues, maxvalues)
    times[2] = (times[2] + (time() - start_time) - times[1]) / 2
     
    dil = cv2.dilate(thresh, kernel)
    times[3] = (times[3] + (time() - start_time) - times[2]) / 2
    cont = cv2.findContours(dil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    times[4] = (times[4] + (time() - start_time) - times[3]) / 2
    contours = cont[0]
    for contour in contours:
        if len(contour) > 20:
            cordX = 0
            cordY = 0
            for i in contour:
                cordX += i[0][0]
                cordY += i[0][1]
            cordX /= len(contour)
            cordY /= len(contour)
 
    times[5] = (times[5] + (time() - start_time) - times[4]) / 2
 
    cv2.imshow('thresh',thresh)
    if cv2.waitKey(5)== 27:
        break
    times[6] = (times[6] + (time() - start_time) - times[5]) / 2
    now = time()
    seconds_from_last = now - start_time
    print round(1 /seconds_from_last, 0)
    start_time = now
 
# Clean up everything before leaving
for i in times:
    print i * 1000
 
print 1 / sum(times)
cv2.destroyAllWindows()
cap.release()
