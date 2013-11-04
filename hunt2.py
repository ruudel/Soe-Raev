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

def annatuld(tugevus):
    saada(coil,'k'+str(tugevus))
        

##################### ARA VALJA KOMMENTEERI! #######################
saaseadmed()            # sebib oiged seadmed ja avab pordid
saada(coil, 'c')        # laeb kondeka
##########################################################

c = cv2.VideoCapture(1)

c.set(3, 320)   #Pildi korgus
c.set(4, 240)   #Laius

pall_min = [0,200,120]
pall_max = [20,255,255]

sinine_min = [104,153,0]
sinine_max =  [117,255,255]

kollane_min = [22,46,121]
kollane_max = [52,223,210]

must_min = [95, 35, 0]
must_max = [135, 180, 55]

tume = pall_min
hele = pall_max

kernel = np.ones((5,5), "uint8")    #dilate jaoks

while(1):

    saada(coil, 'c')
    saada(coil, 'p')
    start=time.time()
    _,f = c.read()
    hsv = cv2.cvtColor(f,cv2.COLOR_BGR2HSV)

    #Mis varvi on vaja taga ajada
    if kasPall():
        if kasA():
            tume = kollane_min
            hele = kollane_max
        else:
            tume = sinine_min
            hele = sinine_max
    else:
        tume = pall_min
        hele = pall_max

    
    thresh = cv2.inRange(hsv,np.array(tume), np.array(hele))

    jooned = cv2.inRange(hsv, np.array(must_min), np.array(must_max))

    dilatejoon = cv2.dilate(jooned, kernel)

    dilate = cv2.dilate(thresh, kernel)

    moments = cv2.moments(dilate)

    joon = cv2.moments(dilatejoon)

    joonarea = joon['m00']

    area = moments['m00']

    x = 0
    y = 0
    
    if(area > 0):
        saada(coil, 'c')
        saada(coil, 'p')

        x = moments['m10']
        y = moments['m01']

        if joonarea>0:
            if joon['m01'] < y:
                
                if hele != pall_max:
                    if x < 170 and x > 140:
                        annatuld(10000)
                        tume = pall_min
                        hele = pall_max
                    else:
                        saadaseadmetele('-sd10')

                elif x < 140:
                    soidavasakule(30)
                elif x > 160:
                    soidaparemale(30)
                else:
                    soidaedasi(30)
                    
    else:
        saadaseadmetele('sd15')

    print("FPS: " + (str)(1/(time.time()-start)))
    
    cv2.imshow("Susivisoon", dilate)
##    cv2.imshow("Jooned", dilatejoon)
        
    if cv2.waitKey(25) == 27:
        stop()
        cv2.destroyAllWindows()
        c.release()
        break
