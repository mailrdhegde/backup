import sys
import numpy as np
import cv2
import imutils
from imutils import contours
import datetime
import time
import os
import json
from objectdetection import object_detection
from css_face_recognition import css_face_recognition
#from NumberPlateDetection import NumberPlateDetection
import pickle
import css_common
import logging

logging.basicConfig(
    filename="./test.log",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(filename)s:%(lineno)s:%(funcName)s:%(message)s"
    )

def process_camera(camera):
      global camera_handles,camera_config
      logging.debug("processing camera: "+str(camera['camera_id']))
      #load encoded faces for face recognition
      encoded_faces_file = open("../models/encodings.pickle","rb")
      data = pickle.loads(encoded_faces_file.read(),encoding="latin-1")
      # below are used to limit the number of frames processed per camera when not run in parallel, remove once parallel processes are creared for each camera
      frames_to_process = int(camera['frame_rate'] * 20) # at least 30 seconds with 20 fps
      frames_processed = 0

      frames_to_skip = int(camera['frame_rate']/ 2)
      frames_skipped = 0
# below block is just for demo to write face detection to another file for display
 
      if (camera['motion_detection_enabled']== "TRUE"):
          logging.debug("for camera id:"+str(camera['camera_id'])+" motion detection "+str(camera['motion_detection_enabled']))
          motion_detected = False
          fgbg = cv2.createBackgroundSubtractorMOG2() 
########  This loop has the core motion detection logic
          #while (camera['handle'].isOpened() and (frames_processed <= frames_to_process)):                                                    
          while (camera['handle'].isOpened()):   
              (grabbed, frame) = camera['handle'].read()                                          
              #if(camera['camera_id'] == 4):
              #  cv2.imshow("camera4",frame)
              #  cv2.waitKey(1)               
              text = " "                                                                                      
              if not grabbed:                                                                                 
                   # no frames so break the loop
                  print("not able to read frames from camera :",camera['camera_id'])
                  logging.debug("not able to read frames from camera :"+str(camera['camera_id']))
                  break                                                                                       
               # resize for proper out put
              frame = cv2.resize (frame,(500,500),interpolation=cv2.INTER_AREA)                                                                                  
              frames_processed = frames_processed +1
              logging.debug("processing camera :"+str(camera['camera_id'])+" processed "+str(frames_processed)+" of "+str(frames_to_process))
              if (frames_processed > frames_to_process):
                 #css_common.update_output_video_file(camera)
                 frames_processed = 0
                 break
              if (frames_skipped <= frames_to_skip ):
                 frames_skipped = frames_skipped + 1
                 css_common.write_to_video(camera,camera['video_out_handle'],frame)
                 css_common.write_to_video(camera,camera['face_recognition_handle'],frame)    
                 continue
              else:
                 frames_skipped = 0

              
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
                  motion_detected = True                                                                         
              cv2.putText(frame, "{}". format(text), (10,20),                                                 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)                                        
#                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)                                        
                                                                                                        
              cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),                  
                         (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35,(0,0,255), 1)                 
              if motion_detected == False:                                                                                     
                     # no motion detected in this frame so just write this
                 css_common.write_to_video(camera,camera['video_out_handle'],frame)
                 css_common.write_to_video(camera,camera['face_recognition_handle'],frame)    

              else:
                  #motion detected so run face detection
                 logging.debug("camera id:"+str(camera['camera_id'])+"motion_detected:"+str(motion_detected))
############# end of motion detection logic
 
                 person_detected,person_names,face_detection_frame = css_face_recognition(data,frame) 
                 
                 css_common.write_to_video(camera,camera['video_out_handle'],frame)
                 css_common.write_to_video(camera,camera['face_recognition_handle'],face_detection_frame)    

      #end of loop
      else:
       # motion detection not enabled capture image and write without changes 
         logging.debug("motion detection not enabled for camera id:"+ str(camera['camera_id']))
         while (camera['handle'].isOpened()  and (frames_processed <= frames_to_process) ):                                                    
            (grabbed, frame) = camera['handle'].read()                                          
            if not grabbed:
               break
            frames_processed = frames_processed + 1
            logging.debug("processing  camera id:"+str(camera['camera_id'])+" frame "+str(frames_processed)+" of "+str(frames_to_process))

            css_common.write_to_video(camera,camera['video_out_handle'],frame)
            css_common.write_to_video(camera,camera['face_recognition_handle'],frame)                                                         

            if (frames_processed > frames_to_process):
               frames_processed = 0;
               break
                #css_common.update_output_video_file(camera)
                #done with camera close the out put file and input file
 # in either case of motion detection enabled or not close the file handle
#        ( once it is based on size remove this from here as it will be taken care in write_to_video itslef)  
          #done with camera close the file handle
      logging.debug("Closing camera "+ str(camera['camera_id']))
      camera['handle'].release()    
      camera['video_out_handle'].release()
      camera['face_recognition_handle'].release()
      #face_recognition_handle.release()
      # increment indices to create new file
      #css_common.update_output_video_file(camera)
               
      
#end of processCamera
            
def Main():
      #read and initialize application config variable and load camera
      css_common.initialize()
 #     while True:
 #        for camera  in css_common.camera_config: 
 #            process_camera(camera)
      for camera  in css_common.camera_config: 
             process_camera(camera)


if __name__ == "__main__":
      Main()
