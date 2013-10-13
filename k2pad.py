# fs0 - k2sk mootori automaatse peatamise lopetamsiseks
# sudo idle-python2.7 k2pad.py 

import serial
from time import sleep
vasak = serial.Serial('/dev/ttyACM0')
parem = serial.Serial('/dev/ttyACM1')

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
    

saadaseadmetele('fs0') ## ARA VALJA KOMMENTEERI! lylitab autom peatamise v2lja

while (1):
    print(kasPall())
    sleep(0.5)

##soidaedasi(10)
##while True:
##    loeseadmest(vasak, 's')
##    loeseadmest(parem, 's')
##    sleep(0.5)

##eih(20)
##soidaedasi(20)
##sleep(1)
##tagane(30)
##stop()
##ymberpoord()
##soidavasakule(30)
##sleep(2)
##soidaparemale(30)
##sleep(2)
##ymberpoord()

