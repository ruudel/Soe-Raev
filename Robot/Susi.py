import cv2 
import numpy as np
import serial
import time
from time import sleep

#===============================================================================
# FUNKSID!
#===============================================================================

def saaseadmed(): # saab idﾴd ainult siis kui aku toide on peal!!!!!
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

def kasSinine():
    parem.write('go\n')
    v=parem.readline()
    if '<0mine>\n' in v:
        return True
    else:
        return False

def kasKollane():
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

#===============================================================================
# OLEKUTE FUNKSID
#===============================================================================

#Loogika, mida Susi teeb, kui ta hoiab hetkel palli
def pallOnSuus():
    stop()                      #Kõige pealt võtame hoo maha ja mõtleme ühe nanosekundi
    
    if x < 200 and x > 120:     #Kui varav on enamvahem keskel
        stop()      
        coil.write('k32000')    #Ja viruta pallile
        tume = pall_min         #Ja hakka uuesti palli otsima
        hele = pall_max
        
    else:                       #Aga kui varav pildi keskel pole siis otsi paremini
        if x >= 200:
            parem.write('sd-10')      #Keerle paremale poole
        elif x <= 120:
            vasak.write('sd10')

#Loogika, mida Susi teeb, kui palli pole
def pallPoleSuus():
    stop()
    
    if joon['m01'] > 210:       #Kui must joon, mis halba õnne toob, on päris nina all, 
        while joon['m01'] > 210:
            otsi(15)            #Siis Susi enam edasi sõita ei taha vaid keerab otsa ringi
    
    elif x < 140:               #kui sihik on vasakul siis soida vasakule
        vasak.write('sd15')
        
    elif x > 190:               #kui paremal siis paremale
        parem.write('sd-15')
        
    else:                       #kui kuskil keskel siis edasi
        soidaedasi(30)
        

#Loogika, kui ei leita palli või väravat
def otsi(kiirus):
    if cnt>20:
        stop()
        soidaedasi(30)
        sleep(0.5)
        cnt=0
        
    else:
        saadaseadmetele('sd'+str(kiirus))
        cnt+=1
    
#===============================================================================
# INIT
#===============================================================================

seadmed = []
saaseadmed()
saada(coil, 'c')

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

c = cv2.VideoCapture(1)

c.set(3, 320)   #Pildi korgus
c.set(4, 240)   #Laius

kernel = np.ones((5,5), "uint8")    #dilate jaoks

#koordinaadid
x = 0
y = 0

#kaunter keerlemise jaoks
cnt = 0


#===============================================================================
# PEATSÜKKEL
#===============================================================================

while(1):
    cnt = 0
    coil.write('c')
    coil.write('p')
    start=time.time()
    _,f = c.read()
    hsv = cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    
    #Esimese asjana, tulista platsi keskele
    soidaedasi(40)
    sleep(0.5)
    stop()

    #Mis varvi on vaja taga ajada
    if kasPall():
        if kasSinine():
            tume = sinine_min
            hele = sinine_max
        elif kasKollane():
            tume = kollane_min
            hele = kollane_max
    else:
        tume = pall_min
        hele = pall_max
    
    #igasugu pilditöötlus
    thresh = cv2.inRange(hsv,np.array(tume), np.array(hele))
    jooned = cv2.inRange(hsv, np.array(must_min), np.array(must_max))
    dilatejoon = cv2.dilate(jooned, kernel)
    dilate = cv2.dilate(thresh, kernel)
    moments = cv2.moments(dilate)
    joon = cv2.moments(dilatejoon)
    joonarea = joon['m00']
    area = moments['m00']
    
    
    #===========================================================================
    # ERINEVAD OLEKUD!
    #===========================================================================
    
    #Hommik on käes ja Susi teeb silmad lahti, mis ta näeb?
    #Lootuses kaadrisagedust tõsta, ei kasuta ma siin omatehtud funktsioone eriti
    
    if area > 0:                    #Kui ta üldse näeb midagi
        coil.write('p')
        x = moments['m10']/area     #Siis ärkab Susi sees matemaatik, ta arvutab oma sihtmärgi koordinaadid
        y = moments['m01']/area
        
        parem.write('gb\n')         #Susi kontrollib, kas tal juba midagi halbus pole
        if '<b:1>\n' in parem.readline():
            coil.write('p')
            pallOnSuus()
        else:
            pallPoleSuus()

    else:                           #Kui Susi saaki ei leia, peab ta paremaks ringi vaadata
        while(area <= 0):
            otsi(15)                #Kuskil miskit ikka hamba alla panna leidub
    
    
    #===========================================================================
    # TSÜKLI LÕPP
    #===========================================================================
    
    print("FPS: " + (str)(1/(time.time()-start)))
    
    cv2.imshow("Susivisoon", dilate)
##    cv2.imshow("Jooned", dilatejoon)
        
    if cv2.waitKey(25) == 27:
        stop()
        cv2.destroyAllWindows()
        c.release()
        break
