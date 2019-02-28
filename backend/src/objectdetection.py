#!/opt/intel/intelpython2/bin/python
import numpy as np
import sys
sys.path.append('/usr/local/lib/python3.6/dist-packages')
sys.path.append('../lib/Yolo')
sys.path.append('../lib')
import tensorflow as tf

from yolo_model import YOLO
import cv2
from matplotlib import pyplot as plt
import time
import os, sys
import argparse
"""
parser = argparse.ArgumentParser(description='Sample program for YOLO inference in TensroFlow')
parser.add_argument('--v2',action='store_true', default=False, help='Type of the yolo mode Tiny or V2')
parser.add_argument('--par',action='store_true', default=False, help='Enable parallel session with INTER/INTRA TensorFlow threads')
parser.add_argument('--image',action='store', default='sample/dog.jpg', help='Select image for object detection')

args = parser.parse_args()

#select the checkpoint
if not args.v2:
    path="../lib/utils/ckpt/tiny_yolo"
    _type = 'TINY_VOC'
else:
    path="../lib/utils/ckpt/yolov2"
    _type = 'V2_VOC'

"""

#Helper function to draw boxes deduced from the feature map
def draw_boxes(img,box_preds):
    a = 'person'
    b = 'car'
    batch_addr = box_preds['batch_addr']
    boxes =box_preds['boxes']
    indices = box_preds['indices']
    class_names = box_preds['class_names']
    count = 0
    boxes = [boxes[i] for i in indices]
    class_names = [class_names[i] for i in indices]
    for i,b in enumerate(boxes):
        idx  = batch_addr[i]
        left = int(max(0,b[0]))
        bot  = int(max(0,b[1]))
        right= int(min(415,b[2]))
        top  = int(min(415,b[3]))
        cv2.rectangle(img[idx],(left,bot),(right,top),(0,255,255),2)
        class_name = class_names[i].decode('utf-8')
#        cv2.putText(img[idx], class_names[i].decode('utf-8'), (int(left), int(bot)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2);
        cv2.putText(img[idx], class_name, (int(left), int(bot)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2);
        if a == class_name:
            print("object_detection.py:draw_boxes():person detected")
            count += 1
        #elif b == class_name:
              #print("objectdetection.py:draw_boxes():vehicle detected")
        else:
            print("object_detection.py:draw_boxes:not person or vehicle - class_name:",class_name)
           #print("vehicle is there\n")
           #print("Initializing vehicle detection\n")
           #os.system("python Main.py")
           #print("plate Recognition Done\n")
           #os.system("python mail.py")
    print("object_detection.py:draw_boxes():total persons detected ", count)
    return class_names


def object_detection(input_frame):
    #TensorFlow graph and Session
    parser = argparse.ArgumentParser(description='Sample program for YOLO inference in TensroFlow')
    parser.add_argument('--v2',action='store_true', default=False, help='Type of the yolo mode Tiny or V2')
    parser.add_argument('--par',action='store_true', default=False, help='Enable parallel session with INTER/INTRA TensorFlow threads')
    parser.add_argument('--image',action='store', default='sample/dog.jpg', help='Select image for object detection')

    args = parser.parse_args()

    #select the checkpoint
    if not args.v2:
        path="../lib/utils/ckpt/tiny_yolo"
        _type = 'TINY_VOC'
    else:
        path="../lib/utils/ckpt/yolov2"
        _type = 'V2_VOC'

    with tf.Graph().as_default():

        batch = 1
        img_in = tf.placeholder(tf.float32,[None,416,416,3])
        clf = YOLO(img_in,yolotype=_type)
        saver = tf.train.Saver()

        #read and preprocess the image
        #cap = cv2.VideoCapture("http://admin:YWRtaW4=@192.168.1.7:8080/stream/getvideo")
        #cap = cv2.VideoCapture('http://admin:YWRtaW4=@192.168.1.2:8080/stream/getvideo')
        #select the session Type
        #if not args.par:
        if True:
            sess_type = tf.Session()
        else:
            sess_type = tf.Session(config=tf.ConfigProto(inter_op_parallelism_threads=int(os.environ['NUM_INTER_THREADS']),
                                                    intra_op_parallelism_threads=int(os.environ['NUM_INTRA_THREADS'])))
        with sess_type as sess:
            saver.restore(sess, path)
            t0 = time.time()
            #ret,img=cap.read()
            #assert ret,'error reading webcam'
            img = input_frame
            img2=[cv2.resize(img,(416,416))]*batch
            image = [im*0.003921569 for im in img2]
            box_preds=sess.run(clf.preds,{img_in: image})
            t1 = time.time()
            ftime = 1/(t1-t0)
            print("object_detection.py:object_detection():Frame rate : %f fps"  % ftime)
            class_names = draw_boxes(img2,box_preds)
            #cv2.imshow('frame',img2[0])
            res=cv2.resize(img2[0],(2*416,2*416), interpolation = cv2.INTER_CUBIC)
            #cv2.imwrite('/home/preeti/Downloads/YOLO-Object-Detection-master/face-recognition-opencv/examples/frames.jpg',res)          #writing the frame generated
            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #    break
            sess.close()
    return class_names,img2[0]
            


