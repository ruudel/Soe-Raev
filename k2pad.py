# -*- coding: utf-8 -*-
# fs0 - k2sk mootori automaatse peatamise lopetamsiseks
# sudo idle-python2.7 k2pad.py 

import serial
from time import sleep

seadmed=[]
#coil=serial.Serial('/dev/ttyACM0')
#vasak=serial.Serial('/dev/ttyACM1')
#parem=serial.Serial('/dev/ttyACM2')

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
    saadaseadmetele('sd80\n')
    sleep(0.7)
    saadaseadmetele('sd0')

def soidavasakule(kiirus):
    saada(vasak, 'sd-'+str(kiirus-kiirus*0.3))
    saada(parem, 'sd'+str(kiirus))

def soidaparemale(kiirus):
    saada(vasak, 'sd-'+str(kiirus))
    saada(parem, 'sd'+str(kiirus-kiirus*0.3))

def loeseadmest(seade, sonum):
    saada(seade,sonum)
    print(seade.readline())

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

##################### ARA VALJA KOMMENTEERI! #######################
saaseadmed()            # sebib oiged seadmed ja avab pordid
saadaseadmetele('fs0')  # lylitab autom peatamise v2lja
saada(coil,'fs0')       # lylitab autom kondeka tyhjaks laadimise v2lja
saada(coil, 'c')        # laeb kondeka
####################################################################


##while (1):
##    print(kasPall())
##    sleep(0.5)

##soidaedasi(10)
##while True:
##    loeseadmest(vasak, 's')
##    loeseadmest(parem, 's')
##    sleep(0.5)
