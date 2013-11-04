import TopLevel
import numpy as np
import cv2

class Silmad(TopLevel):

    kernel = np.ones((5,5), "uint8")    #dilate jaoks
    
    c = cv2.VideoCapture(1)
    
    #===========================================================================
    # c.set(3, 200)   #Pildi korgus
    # c.set(4, 200)   #Laius
    #===========================================================================

    def __init__(self):
        _,f = self.c.read()
        hsv = cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    
        thresh = cv2.inRange(hsv,np.array(TopLevel.tume), np.array(TopLevel.hele))
    
        erode = cv2.erode(thresh, self.kernel)
        dilate = cv2.dilate(erode, self.kernel)
    
        moments = cv2.moments(dilate)
        area = moments['m00']
        
        if area > 0:
            TopLevel.sihik = moments['m10']
        else:
            TopLevel.sihik = 0