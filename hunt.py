# -*- coding: utf-8 -*-
import cv2 
import numpy as np
import cv2.cv as cv
import serial
import time
from time import sleep

seadmed = []

#vasak = serial.Serial('/dev/ttyACM3')
#parem = serial.Serial('/dev/ttyACM4')
#coil = serial.Serial('/dev/ttyACM5')

def saaseadmed(): # saab id´d ainult siis kui aku toide on peal!!!!!
    global parem, vasak, coil
    for i in range(256):
        try:
            s=serial.Serial('/dev/ttyACM'+str(i),timeout=1,parity=serial.PARITY_NONE,baudrate=115200)
            s.write("?\n")
            idstr=s.readline()
            if (idstr=='<id:1>\n'):
                parem=s
                seadmed.append(parem)
            elif (idstr=='<id:2>\n'):
                vasak=s
                seadmed.append(vasak)
            else:
                coil=s
                seadmed.append(coil)
        except serial.SerialException:
            pass
    if len(seadmed)==0:
        print('Seadmeid ei leitud!')

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
    saadaseadmetele('sd20\n')
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

def getthresholdedimg(hsv):
    color = cv2.inRange(hsv,np.array(tume),np.array(hele))
    return color

def kasA():
    parem.write('go\n')
    v=parem.readline()
    if v=='<0mine>\n':
        return True
    else:
        return False

def kasB():
    parem.write('gl\n')
    v=parem.readline()
    if v=='<0varav>\n':
        return True
    else:
        return False

def kasPall():
    parem.write('gb\n')
    v=parem.readline()
    if v=='<b:1>\n':
        return True
    else:
        return False

def annatuld(tugevus=5000):
    saada(coil,'k'+str(tugevus))

def otsiPall():
    print("Otsin palli")
    while area == 0:
        soidaparemale(50)
    else:
        stop()
        return
        

##################### ARA VALJA KOMMENTEERI! #######################
saaseadmed()            # sebib oiged seadmed ja avab pordid
saadaseadmetele('fs0')  # lylitab autom peatamise v2lja
saada(coil,'fs0')       # lylitab autom kondeka tyhjaks laadimise v2lja
saada(coil, 'c')        # laeb kondeka
##########################################################

c = cv2.VideoCapture(1)

c.set(3, 200)   #Pildi korgus
c.set(4, 200)   #Laius

pall_min = [0,200,120]
pall_max = [20,255,255]

sinine_min = [104,153,0]
sinine_max =  [117,255,255]

kollane_min = [22,46,121]
kollane_max = [52,223,210]

tume = pall_min
hele = pall_max

kernel = np.ones((5,5), "uint8")    #dilate jaoks

while(1):
    start=time.time()
    _,f = c.read()
##    f = cv2.flip(f,1)
    blur = cv2.medianBlur(f,5)
    hsv = cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
##    color = getthresholdedimg(hsv)

    #Mis varvi on vaja taga ajada
    if kasPall():
        if kasA():
            tume = sinine_min
            hele = sinine_max
        else:
            tume = kollane_min
            hele = kollane_max
    else:
        tume = pall_min
        hele = pall_max
    
    
    thresh = cv2.inRange(hsv,np.array(tume), np.array(hele))

    dilate = cv2.dilate(thresh, kernel)
    
    
    tr = cv.fromarray(thresh)

    moments = cv.Moments(tr, 0)
    area = cv.GetCentralMoment(moments, 0, 0)

    #there can be noise in the video so ignore objects with small areas 
    if(area > 0):
        #determine the x and y coordinates of the center of the object 
        #we are tracking by dividing the 1, 0 and 0, 1 moments by the area 
        x = cv.GetSpatialMoment(moments, 1, 0)/area
        y = cv.GetSpatialMoment(moments, 0, 1)/area

        print 'x: ' + str(x) + ' y: ' + str(y) + ' area: ' + str(area)

 #       soidaedasi(30)

 # x keskpunkt on 95
        if x < 95:
            soidavasakule(20)
        elif x > 105:
            soidaparemale(20)
        elif x>=95 and x<=105:
            soidaedasi(30)
##        else:
##            saadaseadmetele('sd5')

        if kasPall():
            if area>10000:
                annatuld(5000)
                tume = pall_min
                hele = pall_max
                
            
    else:
        saadaseadmetele('sd5')

    print("FPS: " + (str)(1/(time.time()-start)))
    
    cv2.imshow("Susivisoon", dilate)
        
    if cv2.waitKey(25) == 27:
        stop()
        break

cv2.destroyAllWindows()
c.release()
