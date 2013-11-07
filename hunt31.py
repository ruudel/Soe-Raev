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
    saada(coil,'c')
    saada(coil,'k'+str(tugevus))

def tuld(tugevus):
    saada(coil,'fs0')
    print 'ohtlik'
    saada(coil,'c')
    print 'laadida'
    sleep(3)
    print 'pauk'
    saada(coil,'k'+str(tugevus))
    saada(coil,'fs1')
    print 'ohutu'

def t2():
    saada(coil,'fs0')
    print 'ohtlik'
    saada(coil,'c')
    print 'laadida'
    sleep(3)
    print 'pauk'
    saada(coil,'k'+str(5000))
    saada(coil,'fs1')
    print 'ohutu' 
        



# kood alaku
print 'tuld'
x = 0
##################### ARA VALJA KOMMENTEERI! #######################
saaseadmed()            # sebib oiged seadmed ja avab pordid
#saadaseadmetele('fs1')  # lylitab autom peatamise v2lja, kommisin valja 
saada(coil, 'c')        # laeb kondeka
##########################################################

c = cv2.VideoCapture(0)


c.set(3, 240)   #Pildi korgus
c.set(4, 320)   #Laius

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
    saada(coil,'c')
    _,f = c.read()
    blur = cv2.medianBlur(f,5)
    hsv = cv2.cvtColor(f,cv2.COLOR_BGR2HSV)

    thresh = cv2.inRange(hsv,np.array(tume), np.array(hele))

    erode = cv2.erode(thresh, kernel)
    dilate = cv2.dilate(erode, kernel)

    moments = cv2.moments(thresh)
    area = moments['m00']
    saada(coil, 'p') # pingib coilguni, et kondekad tyhjaks ei laeks
    
    if area > 0:
        x = moments['m10'] / area
        if x < 85:
            soidavasakule(30)
            print 'vasak 30'
        elif x > 100:
            soidaparemale(30)
            print 'parem 30'
        elif x>=85 and x<=100:
            soidaedasi(30)
            print 'edasi 30'
    else:
        parem.write('sd10')
        vasak.write('sd10')
        print 'parem vasak 10'

    parem.write('gb\n')
    if parem.readline()=='<b:1>\n':
        if kasA():
            tume = sinine_min
            hele = sinine_max
            print 'kas a'

        elif kasB():
            tume = kollane_min
            hele = kollane_max
            print 'kas b'
            
        if x > 70 and x < 110:
            saada(coil,'k500')
            print 'pauk'
        
        elif x > 110:
            parem.write('sd10')
            vasak.write('sd10')
            print 'parem vasak 10'

        elif x < 70:
            parem.write('sd-10')
            vasak.write('sd-10')
            print 'parem vasak 10'
        
    else:
        tume = pall_min
        hele = pall_max
        
        print("FPS: " + (str)((int)(1/(time.time()-start))) + ", X: " + str(x))
    
    cv2.imshow("Susivisoon", dilate)
        
    if cv2.waitKey(25) == 27:
        stop()
        break

cv2.destroyAllWindows()
c.release()
