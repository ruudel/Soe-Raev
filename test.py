# -*- coding: utf-8 -*-
import cv2 
import numpy as np
import cv2.cv as cv
import serial
import time
from time import sleep

seadmed = []

def kasPall():
    parem.write('gb\n')
    v=parem.readline()
    if v=='<b:1>\n':
        return True
    else:
        return False

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

while(1):
    if kasPall():
        print('pall')
    else:
        print('tyhi')
