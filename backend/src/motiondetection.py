import sys
import numpy as np
import cv2
import imutils
from imutils import contours
import datetime
import time
import css_common


def motion_detection(camera):
    print("motiondetection.py:motion_detection:processing camera_id",camera['camera_id'])
    return_value=False
    fgbg = cv2.createBackgroundSubtractorMOG2()
    frame = [[]]
    camera_handle = camera['handle']
    while (camera_handle.isOpened()):
        (grabbed, frame) = camera_handle.read()
        text = " "
        if not grabbed:
            break

        frame = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)

        fgmask = fgbg.apply(gray)
        thresh = cv2.erode(fgmask, None, iterations=2)
        (_,cnts,hierarchy) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for (i,c) in enumerate(cnts):
            if cv2.contourArea(c) < 300:
                continue

            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(fgmask, (x,y), (x+w,y+h), (0,255,0), 2)
            cv2.putText(fgmask, "#{}".format(i + 1), (x, y - 15),
            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)        
            text = "Motion detected"
            return_value = True
        #if (text =="Motion detected"):
            
            #playsound.playsound('/home/preeti/Downloads/YOLO-Object-Detection-master/1.mp3', True)
#        cv2.putText(fgmask, "{}". format(text), (10,20),
#                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
        cv2.putText(frame, "{}". format(text), (10,20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)

        cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35,(0,0,255), 1)

    #cv2.imshow('frame',frame)
    #cv2.imshow('gray', gray)
    #    cv2.imshow('fgmask', fgmask)

    #if cv2.waitKey(1) & 0xFF == ord('q'):
        camera['video_out_handle'].write(frame)
        break
    camera['handle'].release()
    return return_value,frame
#cap.release()
#cv2.destroyAllWindows()
