import serial
import TopLevel

class Seadmed:
    
    seadmed = []
    
    def __init__(self, seadmed):
        
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