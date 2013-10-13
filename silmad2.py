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

def ymberpoord():
    saadaseadmetele('sd80\n')
    sleep(0.7)
    saadaseadmetele('sd0')

def soidaparemale(kiirus):
    saada(vasak, 'sd'+str(kiirus-kiirus*0.3))
    saada(parem, 'sd-'+str(kiirus))

def soidavasakule(kiirus):
    saada(vasak, 'sd'+str(kiirus))
    saada(parem, 'sd-'+str(kiirus-kiirus*0.3))

def loeseadmest(seade, sonum):
    saada(seade,sonum)
    print(seade.readline())

saadaseadmetele('fs0') ## ARA VALJA KOMMENTEERI! lylitab autom peatamise v2lja


def getthresholdedimg(hsv):
    color = cv2.inRange(hsv,np.array(tume),np.array(hele))
    return color

c = cv2.VideoCapture(1)

tume = [6,175,114]
hele = [14,255,220]

while(1):
    _,f = c.read()
    f = cv2.flip(f,1)
    blur = cv2.medianBlur(f,5)
    hsv = cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    color = getthresholdedimg(hsv)
    erode = cv2.erode(color,None,iterations = 3)
    dilate = cv2.dilate(erode,None,iterations = 10)
    
    thresh = cv2.inRange(hsv,np.array(tume), np.array(hele))
    
    tr = cv.fromarray(thresh)
    
    moments = cv.Moments(tr, 0)
    area = cv.GetCentralMoment(moments, 0, 0)

    #there can be noise in the video so ignore objects with small areas 
    if(area > 10000):
        #determine the x and y coordinates of the center of the object 
        #we are tracking by dividing the 1, 0 and 0, 1 moments by the area 
        x = cv.GetSpatialMoment(moments, 1, 0)/area
        y = cv.GetSpatialMoment(moments, 0, 1)/area

        print 'x: ' + str(x) + ' y: ' + str(y) + ' area: ' + str(area)

 #       soidaedasi(30)
 # x keskpunkt on 325

        
        if x < 250:
            soidaparemale(10)
        elif x > 400:
            soidavasakule(10)
        else:
            soidaedasi(10)
        
    else:
        stop()
        
    if cv2.waitKey(25) == 27:
        break

cv2.destroyAllWindows()
c.release()
