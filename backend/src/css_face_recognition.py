# USAGE
# python recognize_faces_image.py --encodings encodings.pickle --image examples/example_01.png 

# import the necessary packages
import face_recognition
import argparse
import pickle
import cv2
import datetime

def css_face_recognition(data,frame):

	# construct the argument parser and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-e", "--encodings", required=True,
		help="path to serialized db of facial encodings")
	ap.add_argument("-i", "--image", required=True,
		help="path to input image")
	ap.add_argument("-d", "--detection-method", type=str, default="cnn",
	help="face detection model to use: either `hog` or `cnn`")
	#args = vars(ap.parse_args())


	# load the input image and convert it from BGR to RGB
	image = frame
	rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

	# detect the (x, y)-coordinates of the bounding boxes corresponding
	# to each face in the input image, then compute the facial embeddings
	# for each face
	print("css_face_recognition.py: image being processed is...")
	#cv2.imshow("css_face_recognition",image)
	#cv2.waitKey(1)
	#boxes = face_recognition.face_locations(rgb,model=args["detection_method"])
	
	boxes = face_recognition.face_locations(rgb,model="hog")
#	for box in boxes:
	#	print("css_face_recognition.py:box",box)
	#inp = input("enter something")
	encodings = face_recognition.face_encodings(rgb, boxes)

	# initialize the list of names for each face detected
	names = []
	faces_detected = False
	# loop over the facial embeddings
	for encoding in encodings:
		# attempt to match each face in the input image to our known
		# encodings
		matches = face_recognition.compare_faces(data["encodings"],
			encoding)
		name = "Unknown"
		#print("css_face_recognition.py:matches:",matches)
		# check to see if we have found a match
		if True in matches:
			# find the indexes of all matched faces then initialize a
			# dictionary to count the total number of times each face
			# was matched
			matchedIdxs = [i for (i, b) in enumerate(matches) if b]
			counts = {}

			# loop over the matched indexes and maintain a count for
			# each recognized face face
			for i in matchedIdxs:
				name = data["names"][i]
				counts[name] = counts.get(name, 0) + 1

			# determine the recognized face with the largest number of
			# votes (note: in the event of an unlikely tie Python will
			# select first entry in the dictionary)
			name = max(counts, key=counts.get)
			names.append(name)
	
		# update the list of names
		print("css_face_recognition.py:name:",name)

	print("css_face_recognition.py: recognized faces:")
	# loop over the recognized faces
	for ((top, right, bottom, left), name) in zip(boxes, names):
		# draw the predicted face name on the image
		cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
		y = top - 15 if top - 15 > 15 else top + 15
		cv2.putText(image, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
			0.75, (0, 255, 0), 2)
	if len(names)>0:
           faces_detected = True
	# show the output image
	#cv2.imshow("Image", image)
	out_file_name ="../../common/images/face_detection/"+ str(datetime.datetime.now())+".jpg" 
	#cv2.imwrite(out_file_name, image)
#	cv2.waitKey(0)
	return faces_detected,names,image