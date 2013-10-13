import cv2
import numpy as np
import cv2.cv as cv


import serial
from time import sleep
vasak = serial.Serial('/dev/ttyACM0')
parem = serial.Serial('/dev/ttyACM1')

def saada(seade, sonum):
    seade.write(sonum+'\n')

def saadaseadmetele(sonum):
    saada(vasak, sonum)
    saada(parem, sonum)

def stop():
    saadaseadmetele('sd0')

def soidaedasi(kiirus):
    saada(vasak,'sd'+str(kiirus))
    saada(parem,'sd-'+str(kiirus))

def tagane(kiirus):
    saada(vasak,'sd-'+str(kiirus))
    saada(parem,'sd'+str(kiirus))

def eih(kiirus):
    saada(vasak,'sd-'+str(kiirus))
    saada(parem,'sd'+str(kiirus))
    sleep(0.5)
    saada(vasak, 'sd-'+str(kiirus))
    saada(parem, 'sd'+str(kiirus-kiirus*0.3))
    

def ymberpoord():
    saadaseadmetele('sd80\n')
    sleep(0.7)
    saadaseadmetele('sd0')

def soidavasakule(kiirus):
    saada(vasak, 'sd-'+str(kiirus-kiirus*0.3))
    saada(parem, 'sd'+str(kiirus))

def soidaparemale(kiirus):
    saada(vasak, 'sd-'+str(kiirus))
    saada(parem, 'sd'+str(kiirus-kiirus*0.3))

def loeseadmest(seade, sonum):
    saada(seade,sonum)
    print(seade.readline())

saadaseadmetele('fs0') ## ARA VALJA KOMMENTEERI! lylitab autom peatamise v2lja


def getthresholdedimg(hsv):
    color = cv2.inRange(hsv,np.array(tume),np.array(hele))
    return color

c = cv2.VideoCapture(1)

## tume = [6,175,114]  ## meie palli v2rv
## hele = [14,255,220]
## tume = [0,64,17] ## labi kollase v6me
## hele = [0,135,90]
tume = [108,59,25]
hele = [164,123,65]

while(1):
    _,f = c.read()
    f = cv2.flip(f,1)
    blur = cv2.medianBlur(f,5)
    hsv = cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    color = getthresholdedimg(hsv)
    erode = cv2.erode(color,None,iterations = 3)
    dilate = cv2.dilate(erode,None,iterations = 10)
    
    thresh = cv2.inRange(hsv,np.array(tume), np.array(hele))

    

    #determine the objects moments and check that the area is large  
    #enough to be our object

    tr = cv.fromarray(thresh)
    F = cv.fromarray(f)
    
    moments = cv.Moments(tr, 0)
    area = cv.GetCentralMoment(moments, 0, 0)

    #there can be noise in the video so ignore objects with small areas 
    if(area > 100000):
        #determine the x and y coordinates of the center of the object 
        #we are tracking by dividing the 1, 0 and 0, 1 moments by the area 
        x = cv.GetSpatialMoment(moments, 1, 0)/area
        y = cv.GetSpatialMoment(moments, 0, 1)/area

        print 'x: ' + str(x) + ' y: ' + str(y) + ' area: ' + str(area) 

        #create an overlay to mark the center of the tracked object        
        overlay = cv.CreateImage(cv.GetSize(F), 8, 3)

        cv.Circle(overlay, (int(x), int(y)), 2, (255, 255, 255), 20)
        cv.Circle(tr, (int(x), int(y)), 50, (255, 255, 255), -20)
        cv.Add(F, overlay, F)
        #add the thresholded image back to the img so we can see what was  
        #left after it was applied 
        cv.Merge(tr, None, None, None, F)

    cv2.imshow('Varviotsing',f)
    cv2.imshow("thresh", thresh)
    

    if cv2.waitKey(25) == 27:
        break

cv2.destroyAllWindows()
c.release()
