import serial
from time import sleep

vasak = serial.Serial('/dev/ttyACM0')
parem = serial.Serial('/dev/ttyACM1')

def soidaedasi(kiirus):
    vasak.write('sd'+str(kiirus)+'\n')
    parem.write('sd-'+str(kiirus)+'\n')

def ymberpoord():
    vasak.write('sd20\n')
    parem.write('sd20\n')
##
##while (True):
##    soidaedasi(20)
##    sleep(1.5)
##    ymberpoord()

    
