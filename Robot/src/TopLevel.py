# -*- coding: utf-8 -*-
import serial
import numpy as np
import cv2
import time


#===============================================================================
# MUUTUJAD
#===============================================================================

seadmed = []

global parem, vasak, coil

kernel = np.ones((5,5), "uint8")    #dilate jaoks
    
c = cv2.VideoCapture(1)

#===============================================================================
# VÄRVIDE INITSIALISEERIMINE
#===============================================================================

pallMin = [0,215,140]
pallMax = [15,255,195]

kollaneMin = [25,160,110]
kollaneMax = [35,200,160]

sinineMin = [80,150,60]
sinineMax = [140,300,130]

mustMin = [95,35,0]
mustMax = [135,180,55]

tume = pallMin
hele = pallMax

#===============================================================================
# LEIAB SEADMED
#===============================================================================

for i in range(10):
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
if len(seadmed)<2:
    print('Mingi seade on puudu!')

#===============================================================================
# PEATSÜKKEL
#===============================================================================

while(1):
    
    start = time.time()
    
    #===========================================================================
    # PINGIB COILI KOGU AEG, ET SEE OLEKS ALATI VALMIS
    #===========================================================================    
    coil.write('c')
    coil.write('p')
    
    #===========================================================================
    # SUSIVISIOON
    #===========================================================================
    
    _,f = c.read()
    hsv = cv2.cvtColor(f,cv2.COLOR_BGR2HSV)

    thresh = cv2.inRange(hsv,np.array(tume), np.array(hele))

    jooned = cv2.inRange(hsv, np.array(mustMin), np.array(mustMax))

    erode = cv2.erode(thresh, kernel)
    dilate = cv2.dilate(erode, kernel)

    moments = cv2.moments(dilate)
    area = moments['m00']
    
    if area > 0:
        sihik = moments['m10']
    else:
        sihik = 0
    
    #===========================================================================
    # UURIB KAS PALL ON HAMBUS
    #===========================================================================
    
    parem.write('gb\n')
    if parem.readline() == '<b:1>\n':
        
        #=======================================================================
        # KUI ON PALL, SIIS KONTROLLIB KUMB VÄRAV ON
        #=======================================================================
        coil.write('p') 
        
        parem.write('go\n')
        v=parem.readline()
        
        if v=='<0mine>\n':
            hele = sinineMax
            tume = sinineMin
            
        else:
            hele = kollaneMax
            tume = kollaneMin
            
        #=======================================================================
        # JA OTSI SEE ÜLES
        #=======================================================================
        
        if sihik > 0:
            coil.write('p') 
            if sihik < 70:
                parem.write('-sd10')
            elif sihik > 110:
                vasak.saada('sd10')
            else:
                coil.write('k10000')
        
        #=======================================================================
        # KUI EI NÄE VÄRAVAT, OTSI
        #=======================================================================
        
        else:
            parem.write('-sd10')
            vasak.prite('sd10')    
                    
    #===========================================================================
    # KUI PALLI POLE HAMBUS, SIIS AJA PALLI TAGA
    #===========================================================================
        
    else:
        hele = pallMax
        tume = pallMin
        
        parem.write('sd10')
        vasak.prite('-sd10')
        
    print("FPS: " + (str)((int)(1/(time.time()-start))) + ", X: " + str(sihik))

    cv2.imshow("Susivisoon", dilate)
    cv2.imshow("Jooned", jooned)
    
    if cv2.waitKey(25) == 27:
        parem.write('sd0')
        vasak.write('sd0')
        break

cv2.destroyAllWindows()
c.release()