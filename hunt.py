# -*- coding: utf-8 -*-
import cv2 
import numpy as np
import cv2.cv as cv
import serial
import time
from time import sleep

seadmed = []

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

saaseadmed()

c = cv2.VideoCapture(0)


c.set(3, 320)   #Pildi korgus
c.set(4, 240)   #Laius

#tty v2rv
##pall_min = [0,235,120]
##pall_max = [15,255,255]
##
##sinine_min = [105,185,45]
##sinine_max =  [115,240,130]
##
##kollane_min = [30,115,145]
##kollane_max = [45,175,180]

pall_min = [0,215,140]
pall_max = [15,255,195]

sinine_min = [80,150,60]
sinine_max =  [140,300,130]

kollane_min = [25,160,110]
kollane_max = [35,200,160]

tume = pall_min
hele = pall_max

kernel = np.ones((5,5), "uint8")    #dilate jaoks

while(1):
    start=time.time()
    _,f = c.read()
    hsv = cv2.cvtColor(f,cv2.COLOR_BGR2HSV)

    thresh = cv2.inRange(hsv,np.array(tume), np.array(hele))

    erode = cv2.erode(thresh, kernel)
    dilate = cv2.dilate(erode, kernel)

    moments = cv2.moments(dilate)
    area = moments['m00']
    coil.write('c')
    coil.write('p') # pingib coilguni, et kondekad tyhjaks ei laeks

    x = 0 # keskpunkt

    #kas on pall
    parem.write('gb')
    if parem.readline()=='<b:1>':
        coil.write('p')

        #kumb varav
        parem.write('go\n')
        v=parem.readline()
        if v=='<0mine>\n':
            tume = sinine_min
            hele = sinine_max
        elif v=='<1mine>\n':
            tume = kollane_min
            hele = kollane_max
        
        if x > 70 and x < 110:
            coil.write('k10000')
        
        elif x > 110:
            parem.write('sd10')
            vasak.write('sd10')

        elif x < 70:
            parem.write('sd-10')
            vasak.write('sd-10')
        
    else:
        tume = pall_min
        hele = pall_max
    
    if area > 0:
        x = moments['m10']
        if x < 150:
            parem.write('sd20')
            vasak.write('sd10')
        elif x > 170:
            parem.write('-sd20')
            vasak.write('-sd10')
        else:
            soidaedasi(30)
    else:
        parem.write('sd10')
        vasak.write('sd10')
        
    print("FPS: " + (str)((int)(1/(time.time()-start))))
    
    cv2.imshow("Susivisoon", dilate)
        
    if cv2.waitKey(25) == 27:
        parem.write('sd0')
        vasak.write('sd0')
        break

cv2.destroyAllWindows()
c.release()
