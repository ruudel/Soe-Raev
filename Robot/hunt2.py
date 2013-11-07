# -*- coding: utf-8 -*-
import cv2 
import numpy as np
import serial
import time
from time import sleep

seadmed = []

def saaseadmed(): # saab id´d ainult siis kui aku toide on peal!!!!!
    global parem, vasak, coil
##    parem = serial.Serial('/dev/ttyACM2')
##    vasak = serial.Serial('/dev/ttyACM0')
##    coil = serial.Serial('/dev/ttyACM1')
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
        

##################### ARA VALJA KOMMENTEERI! #######################
saaseadmed()            # sebib oiged seadmed ja avab pordid
saada(coil, 'c')        # laeb kondeka
##########################################################

c = cv2.VideoCapture(1)

c.set(3, 320)   #Pildi korgus
c.set(4, 240)   #Laius

pall_min = [0,225,140]
pall_max = [10,255,200]

sinine_min = [105,160,90]
sinine_max =  [115,210,165]

kollane_min = [26,155,126]
kollane_max = [38,201,164]

must_min = [61, 26, 0]
must_max = [91, 67, 92]

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

    moments = cv2.moments(dilate)

    joon = cv2.moments(dilatejoon)

    joonarea = joon['m00']

    area = moments['m00']

    x = 0
    y = 0

    cnt = 0

    if joon['m01'] > 200:   #kui must joon pole nina all siis vaata edasis
        if(area > 0):       #aga kui pole ja naed mingit palli voi varavat
            saada(coil, 'c')
            saada(coil, 'p')

            x = moments['m10']/area
            y = moments['m01']/area

            if joonarea>0:  #kui musta joont on naha 
                if joon['m01']/joonarea < y: #kui must joon on nina all
                    
                    if hele != pall_max:    #kui otsitakse varavat
                        if x < 300 and x > 100: #ja varav on enamvahem keskel
                            stop()
                            annatuld(32000)
                            tume = pall_min
                            hele = pall_max
                        else:                   #muidu kui keskel pole siis otsi edasi
                            saadaseadmetele('-sd10')
                            cnt +=1
                            if cnt > 20:
                                soidaedasi(30)
                                cnt = 0
                            
                    elif x < 140:   #kui sihik on vasakul siis vasakule
                        soidavasakule(30)
                    elif x > 190:   #kui paremal siis paremale
                        soidaparemale(30)
                    else:           #kui kuskil keskel siis edasi
                        soidaedasi(30)

                else:   #kui pole musta yldse ja on pall
                    if x < 240 and x > 100: #ja varav on enamvahem keskel
                        stop()
                        annatuld(32000)
                        tume = pall_min
                        hele = pall_max
                    
            else:   #aga kui musta joont pole naha siis keerle ringi
                saadaseadmetele('sd10')
                cnt +=1
                if cnt > 20:
                    soidaedasi(30)
                    sleep(0.5)
                    cnt = 0
        else:   #kui ei nae sihtmarki siis keerle
            saadaseadmetele('sd10')
            cnt +=1
            if cnt > 20:
                soidaedasi(30)
                sleep(0.5)
                cnt = 0
    else:   #kui must joon on nina all siis keerle
        saadaseadmetele('sd10')
        cnt +=1
        if cnt > 20:
            soidaedasi(30)
            sleep(0.5)
            cnt = 0

    print("FPS: " + (str)(1/(time.time()-start)))
    
##    cv2.imshow("Susivisoon", dilate)
##    cv2.imshow("Jooned", dilatejoon)
        
    if cv2.waitKey(25) == 27:
        stop()
        cv2.destroyAllWindows()
        c.release()
        break
