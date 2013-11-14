# -*- coding: utf-8 -*-
import cv2 
import numpy as np
import cv2.cv as cv
import serial
import time
from time import sleep

parem = serial.Serial('/dev/ttyACM2', timeout=1, parity=serial.PARITY_NONE, baudrate=115200)
vasak = serial.Serial('/dev/ttyACM1', timeout=1, parity=serial.PARITY_NONE, baudrate=115200)
coil = serial.Serial('/dev/ttyACM0', timeout=1, parity=serial.PARITY_NONE, baudrate=115200)

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
    saadaseadmetele('sd20')
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
    for i in range(3):
        parem.write('go\n')
        v=parem.readline()
        if '<0mine>' in v:
            return True
        else:
            return False
    return False

def kasKol():
    for i in range(3):
        parem.write('go\n')
        v=parem.readline()
        if '<1mine>' in v:
            return True
        else:
            return False
    return False

def kasB():
    parem.write('gl\n')
    v=parem.readline()
    if v=='<0varav>\n':
        return True
    else:
        return False

def kasPall():
    for i in range(3):
        parem.write('gb\n')
        v=parem.readline()
        if '<b:1>' in v:
            return True
        elif '<b:0>' in v:
            return False
        else:
            pass
    return False
        
def annatuld(tugevus):
    saada(coil,'k'+str(tugevus))
    
def otsi():
    joonemomendid = cv2.moments(dilatejoon)
    
    #kui must joon ees on, siis edasi ei soida
    if joonemomendid['m01'] < 180:
        stop()
        ymberpoord()
        
        if joonemomendid['m01'] < 160:
            soidavasakule(kiirus)
        elif joonemomendid['m01'] >= 160:
            soidaparemale(kiirus)
    
    else:
        soidaedasi(kiirus)

def leiaTsenter(contours):
    x=0
    y=0

    maxArea = 0
    
    for contour in contours:
        moments = cv2.moments(contour, True)

        #kui moment 0, siis eira
        if (len(filter(lambda i: i==0, moments.values())) > 0):
            continue

        if moments['m00'] > maxArea:
            maxArea = moments['m00']
            x=moments['m10']/moments['m00']
            y=moments['m01']/moments['m00']

            center=(x,y)

            center = map(lambda i:int(round(i)), center)
            return center
        else:
            return None

def joonistaTsenter(center, image):
    cv2.circle(image, tuple(center), 20, cv.RGB(255,0,0),2)

def kasJoon(center):
    x = center[0]
    y = center[1]
    
    while y < 238:
        y+=1
        if dilatejoon[y, x]==255:
            return True
    return False
    
c = cv2.VideoCapture(0)

c.set(3, 320)   #Pildi korgus
c.set(4, 240)   #Laius

pall_min = [0,170,112]
pall_max = [20,255,255]

sinine_min = [107,180,54]
sinine_max =  [115,198,145]

kollane_min = [26,138,147]
kollane_max = [34,160,183]

must_min = [22, 53, 67]
must_max = [48, 94, 103]

tume = pall_min
hele = pall_max

kernel = np.ones((5,5), "uint8")    #dilate jaoks
dilatekernel = np.ones((8,8), "uint8")    #dilate jaoks

kiirus = 40

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

    dilatejoon = cv2.dilate(jooned, dilatekernel)

    dilate = cv2.dilate(thresh, kernel)

    kontuurimaagia = np.zeros((240,320, 3), np.uint8)

    contours, hierarchy = cv2.findContours(dilate, cv.CV_RETR_EXTERNAL, cv.CV_CHAIN_APPROX_NONE)

    cv2.drawContours(kontuurimaagia, contours, -1, cv2.cv.RGB(0,255,0),-1)

    center = leiaTsenter(contours)

    #kui on joon ees, siis kohe ots ringi
    if dilatejoon[230,160] == 255:
        ymberpoord()

    #Liikumise loogeka
    if center != None:

        if kasJoon(center) == False:
            joonistaTsenter(center, kontuurimaagia)
            joonemomendid = cv2.moments(dilatejoon)

            if joonemomendid['m01'] < center[1]:
                continue
            
            if center[0] > 180:
                if kasPall():
                    vasak.write('sd-25')
                else:
                    soidaparemale(kiirus)
            elif center[0] < 140:
                if kasPall():
                    vasak.write('sd25')
                else:
                    soidavasakule(kiirus)
            else:
                if kasPall():
                        stop()
                        annatuld(32000)
                else:
                    soidaedasi(kiirus)
        else:
            soidaedasi(kiirus)
    else:
        soidaedasi(kiirus)
        
    
##    print("FPS: " + str(int(1/(time.time()-start))))
    cv2.imshow("Susivisoon", kontuurimaagia)
    cv2.imshow("Joonevisioon", dilatejoon)

##    cv2.imshow("Reaalvisoon", f)
        
    if cv2.waitKey(2) >= 0:
        stop()
        cv2.destroyAllWindows()
        c.release()
        break
