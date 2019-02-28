import sys                                                                                                                                                     
import numpy as np                                                                                                                                             
import cv2                                                                                                                                                     
import imutils                                                                                                                                                 
from imutils import contours                                                                                                                                   
import datetime                                                                                                                                                
import time                                                                                                                                                    
import json                                                                                                                                                    
import pickle                                                                                                                                                  
import requests
import logging

css_config = json.dumps({})  #empty json config object
camera_config = json.dumps({})

# This function write video writes the frame to the video file and if the max size is reached updates the file handle to new one
def write_to_video(camera,frame):
      logging.debug("camera id:"+str(camera['camera_id']))
      #if file size + frame size > max size close existing file and open new file 
      # ie call update_output_video(camera)
      camera['video_out_handle'].write(frame)
#end of function write_to_video 

# this function opens the new out put video file after (usually called after specific size is reached) 
def update_output_video_file(camera):
      logging.debug("camera id:"+str(camera['camera_id']))
      camera['video_out_file_index'] = camera['video_out_file_index'] + 1
      if camera['video_out_file_index'] > 5 :
         camera['video_out_file_index'] = 0
      #release old handle
      camera['video_out_handle'].release()
      # post the completed file name to front end queue
      post_data = {}
      post_data['camera_id'] = camera['camera_id']
#      post_data['current_file_name'] = camera["current_video_file_name"]
      post_data['current_file_name'] = "../../common/videos/invideos/video.mp4" 
      post_url = css_config["front_end_base_url"]+str(camera["camera_id"])
      post_response = requests.post(post_url,json=post_data)
      # build new file name string. Logic is "camera"+<camera_id>+<video_out_file_index>+<file extension eg:mp4>   
      video_out_put_file_name  = "../../common/videos/outvideos/"+"camera"+str(camera['camera_id']) + "-"+str(camera['video_out_file_index'])+".mp4"
#      video_out_put_file_name  = "../../common/videos/outvideos/"+"camera"+str(camera['camera_id']) + "-"+str(camera['video_out_file_index'])+".avi"
      camera["current_video_file_name"] = video_out_put_file_name
      fourcc = cv2.VideoWriter_fourcc(*'X264') 
#      camera['video_out_handle'] = cv2.VideoWriter(video_out_put_file_name,fourcc, 20.0, (640,480))  
      camera['video_out_handle'] = cv2.VideoWriter(video_out_put_file_name,fourcc, 20.0, (500,375))  
#end if function update_output_video

#This functions reads the config from json file css.config and stores the values in the global config variablle
def read_config(config_file_name):
      logging.debug("config file name:"+config_file )                                                                          
      with open(config_file_name) as f:                                                                        
            css_config = json.load(f)                                                                          
#end of readConfig                                                                                             
                                                                                                               
#This function loadCamera("camera config file") reads the camera from json file/DB and loads the required parameters for the camera and initializes the streams
def load_camera(camera_config_file = ""):                                                                                                                      
      global camera_config  
      logging.debug("camera_config_file name: "+ camera_config_file)                                                                                                                                   
      #print("css_common.py:load_camera(): camera_config_file name: ",camera_config_file)                                                                             
      if camera_config_file !="":                                                                                                                              
            with open(camera_config_file) as f:                                                                                                                
                  camera_config = json.load(f)                                                                                                                 
            print("css_common.py:load_camera():camera_config :",camera_config)                                                                                       
      else:                                                                                                                                                    
            print("css_common.py:laodCamera(): Invalid camera config file")             
      index = 0                                                                   
      fourcc = cv2.VideoWriter_fourcc(*'H264')                                    
#      fourcc = cv2.VideoWriter_fourcc(*'MP4V')                                    
#      fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G') 
      for camera in camera_config:                                      
            #print("css_common.py:laodCamera(): camera loaded:",camera)  
            logging.debug("camera loaded: "+ str(camera))         
            camera_url = camera['url']                                  
            cap = cv2.VideoCapture(camera_url)                          
            camera['handle']=cap
            camera['video_out_file_index'] = 0
            video_out_put_file_name  = "../../common/videos/outvideos/"+"camera"+str(camera['camera_id']) + "-"+str(camera['video_out_file_index'])+".mp4"
#            video_out_put_file_name  = "../../common/videos/outvideos/"+"camera"+str(camera['camera_id']) + "-"+str(camera['video_out_file_index'])+".avi"
#            video_out_handle = cv2.VideoWriter(video_out_put_file_name,fourcc, 20.0, (640,480)) 
            video_out_handle = cv2.VideoWriter(video_out_put_file_name,fourcc, 20.0, (500,375),True) 
            camera['current_video_file_name'] = video_out_put_file_name
            camera['video_out_handle'] = video_out_handle 
#end of loadCamera()                  

#This function loads the css configuration from json file/db
def load_css_config(config_file = ""):
      global css_config
      logging.debug("css config file: "+ config_file) 
      #print("css_common.py:load_css_config():config file:",config_file)
      if config_file !="":                                                                                                                              
            with open(config_file) as f:                                                                                                                
                  css_config = json.load(f)                                                                                                                 
            #print("css_common.py:load_camera():css_config :",css_config)                                                                                       
      else:                                                                                                                                                    
            print("css_common.py:laodCamera(): Invalid camera config file")
            logging.debug("Invalide camera config file: "+ config_file)              
     
    
def initialize(): 
      logging.debug("Initializing...")                                                                                                                                              
      load_css_config("../config/css_config.json") #populate application level configs                                                                                      
      load_camera("../config/css_camera_config.json")  # Load camera for processing                                                                                      
                                                                                                                                                               
#end of initialize      

#postevent(event) posts the event to the server for further action
#event is a json object with below structure
#  event {
#            'event_id': <event_id>,
#            'event_name': "text of event name",
#            'message': "test of event description",
#            'event_originator':"orignator of the event",
#           'event_destination':"destination for the event",
#           'camera_id':'camera id which has generated the event'
#        }

def postEvent(event,camera): 
      logging.debug("Initializing...")
      if ( camera == NULL ):
          logging.debug("Camera is null")
          return
      logging.debug("Post event:camera id:" + str(camera['camera_id']))
      #build the post 
      post_data = {}
      post_data['EventNotificationDateTime'] = str(datetime.datetime.now().isoformat())
      post_data['EventId']= event['EventId']
      headers = {'content-type': 'application/json'}
      post_url = css_config['server_base_url']+event['CameraId']+"EventNotifications"
      post_data['message'] = event['message']
      post_response = requests.post(url,data=json.dumps(post_data),headers=headers)
      logging.debug("Post response:"+ post_response)
                                                                                            
                                                                                                                                                               
#end of initialize      
