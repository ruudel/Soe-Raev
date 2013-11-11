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

def kasPall():
    parem.write('gb\n')
    v=parem.readline()
    if '<b:1>\n' in v:
        return True
    else:
        return False

def annatuld(tugevus):
    saada(coil,'k'+str(tugevus))

def leiaTsenter(contours):
    x = 0
    y = 0
    for contour in contours:
        moments = cv2.moments(contour, True)

        #kui moment on 0, siis eira
        if (len(filter(lambda i: i==0, moments.values())) > 0):
            continue

        if moments['m00'] > maxArea:
            x = moments['m10']/moments['m00']
            y = moments['m01']/moments['m00']
            
            center = (x,y)

            center = map(lambda i: int(round(i)), center)
    return center

def joonistaTsentrid(center, image):
    cv2.circle(image, tuple(center),20,cv.RGB(255,0,0),2)

c = cv2.VideoCapture(0)

c.set(3, 320)   #Pildi korgus
c.set(4, 240)   #Laius
c.set(cv.CV_CAP_PROP_FPS, 30)

pall_min = [0,163,61]
pall_max = [25,255,242]

sinine_min = [105,160,90]
sinine_max =  [115,210,165]

kollane_min = [23,116,137]
kollane_max = [32,165,231]

must_min = [61, 26, 0]
must_max = [91, 67, 92]

tume = pall_min
hele = pall_max

kernel = np.ones((5,5), "uint8")    #dilate jaoks

maxArea = 0

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

##    moments = cv2.moments(dilate)
##
##    joon = cv2.moments(dilatejoon)
##
##    joonarea = joon['m00']
##
##    area = moments['m00']
##
##    x = 0
##    y = 0

    kontuurimaagia = np.zeros((240,320, 3), np.uint8)

    contours, hierarchy = cv2.findContours(dilate, cv.CV_RETR_EXTERNAL, cv.CV_CHAIN_APPROX_NONE)

##    cv2.drawContours(kontuurimaagia, contours, -1, cv2.cv.RGB(0,255,0),-1) 

    centers = leiaTsenter(contours)

    cv2.drawContours(kontuurimaagia, contours, -1, cv.RGB(255,255,255),2)
    joonistaTsentrid(centers, kontuurimaagia)

    ##SIIN ALGAB LOOGIKA

    





    


    

##    print("FPS: " + str(int(1/(time.time()-start))))
    cv2.imshow("Susivisoon", kontuurimaagia)
##    cv2.imshow("Reaalvisoon", f)
##    cv2.imshow("Jooned", dilatejoon)
        
    if cv2.waitKey(2) >= 0:
        stop()
        cv2.destroyAllWindows()
        c.release()
        break
