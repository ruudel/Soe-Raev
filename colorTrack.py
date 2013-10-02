import cv2
import numpy as np
import cv2.cv as cv

def getthresholdedimg(hsv):
    color = cv2.inRange(hsv,np.array(tume),np.array(hele))
    return color

c = cv2.VideoCapture(0)

tume = [20,100,100]
hele = [30,255,255]

while(1):
    _,f = c.read()
    f = cv2.flip(f,1)
    blur = cv2.medianBlur(f,5)
    hsv = cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    color = getthresholdedimg(hsv)
    erode = cv2.erode(color,None,iterations = 3)
    dilate = cv2.dilate(erode,None,iterations = 10)
    
    thresh = cv2.inRange(hsv,np.array(tume), np.array(hele))

    #determine the objects moments and check that the area is large  
    #enough to be our object

    tr = cv.fromarray(thresh)
    F = cv.fromarray(f)
    
    moments = cv.Moments(tr, 0)
    area = cv.GetCentralMoment(moments, 0, 0)

    #there can be noise in the video so ignore objects with small areas 
    if(area > 100000):
        #determine the x and y coordinates of the center of the object 
        #we are tracking by dividing the 1, 0 and 0, 1 moments by the area 
        x = cv.GetSpatialMoment(moments, 1, 0)/area
        y = cv.GetSpatialMoment(moments, 0, 1)/area

##        print 'x: ' + str(x) + ' y: ' + str(y) + ' area: ' + str(area) 

        #create an overlay to mark the center of the tracked object        
        overlay = cv.CreateImage(cv.GetSize(F), 8, 3)

        cv.Circle(overlay, (x, y), 2, (255, 255, 255), 20)
        cv.Add(F, overlay, F)
        #add the thresholded image back to the img so we can see what was  
        #left after it was applied 
        cv.Merge(tr, None, None, None, F)

    cv2.rectangle(f ,(0,0), (50,50), tume ,-1)
    cv2.rectangle(f ,(50,0), (100,50), hele ,-1)
    cv2.putText(f,"Skaala", (2,20), cv2.FONT_HERSHEY_SIMPLEX, .5, (0,0,0), 2)
    cv2.imshow('Varviotsing',f)

##    cv2.imshow("thresh", thresh)
    

    if cv2.waitKey(25) == 27:
        break

cv2.destroyAllWindows()
c.release()
