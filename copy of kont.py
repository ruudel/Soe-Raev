# -*- coding: utf-8 -*-
import cv2 
import numpy as np
import cv2.cv as cv
import serial
import time
from time import sleep

parem = serial.Serial('/dev/ttyACM2')
vasak = serial.Serial('/dev/ttyACM1')
coil = serial.Serial('/dev/ttyACM0')

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
    
def kasSin():
    parem.write('go\n')
    v=parem.readline()
    if '<0mine>\n' in v:
        return True
    else:
        return False

def kasKol():
    parem.write('go\n')
    v=parem.readline()
    if '<1mine>\n' in v:
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

def kasPall(tase=0):
    if tase==2:
        return False
    parem.write('gb\n')
    v=parem.readline()
    if '<b:1>' in v:
        return True
    elif '<b:0>' in v:
        return False
    else:
        return kasPall(tase+1)

def annatuld(tugevus):
    saada(coil,'k'+str(tugevus))

def leiaTsenter(contours):
    x=0
    y=0
    for contour in contours:
        moments = cv2.moments(contour, True)

        #kui moment 0, siis eira
        if (len(filter(lambda i: i==0, moments.values())) > 0):
            continue
        if moments['m00']/maxArea:
            x=moments['m10']
            y=mometns['m01']

            center=(x,y)

            center = map(lambda i:int(round(i)), center)
            return center
        else:
            return None

def joonistaTsenter(center, image):
    cv2.circle(image, tuple(center), 20, cv.RGB(255,0,0),2)

c = cv2.VideoCapture(0)

c.set(3, 320)   #Pildi korgus
c.set(4, 240)   #Laius

pall_min = [2,183,92]
pall_max = [16,255,229]

sinine_min = [83,148,72]
sinine_max =  [124,213,172]

kollane_min = [20,148,132]
kollane_max = [29,255,218]

must_min = [61, 26, 0]
must_max = [91, 67, 92]

tume = pall_min
hele = pall_max

kernel = np.ones((5,5), "uint8")    #dilate jaoks

maxArea = 0

kiirus = 20

while(1):

    saada(coil, 'c')
    saada(coil, 'p')
    start=time.time()
    _,f = c.read()
    hsv = cv2.cvtColor(f,cv2.COLOR_BGR2HSV)

    #Mis varvi on vaja taga ajada
    if kasPall():
        if kasSin():
            tume = sinine_min
            hele = sinine_max
        elif kasKol():
            tume = kollane_min
            hele = kollane_max
    else:
        tume = pall_min
        hele = pall_max
    
    thresh = cv2.inRange(hsv,np.array(tume), np.array(hele))

    jooned = cv2.inRange(hsv, np.array(must_min), np.array(must_max))

    dilatejoon = cv2.dilate(jooned, kernel)

    dilate = cv2.dilate(thresh, kernel)

    kontuurimaagia = np.zeros((240,320, 3), np.uint8)

    contours, hierarchy = cv2.findContours(dilate, cv.CV_RETR_EXTERNAL, cv.CV_CHAIN_APPROX_NONE)

    cv2.drawContours(kontuurimaagia, contours, -1, cv2.cv.RGB(0,255,0),2)

    if center !=None:
        joonistaTsenter(center, kontuurimaagia)
    elif center[0] > 180:
        soidaparemale(kiirus)
    else:
        if kasPall():
            stop()
            annatuld()
        else:
            soidaedasi()
    else:
        stop()
    
##    print("FPS: " + str(int(1/(time.time()-start))))
    cv2.imshow("Susivisoon", kontuurimaagia)
##    cv2.imshow("Jooned", dilatejoon)
        
    if cv2.waitKey(2) >= 0:
        stop()
        cv2.destroyAllWindows()
        c.release()
        break
