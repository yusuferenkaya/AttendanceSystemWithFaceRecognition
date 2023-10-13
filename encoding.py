import face_recognition
import numpy as np
import cv2

# Load the image
image_path = "known_people\Eren.jpg"
image = cv2.imread(image_path)

# Find the face locations and encodings
face_locations = face_recognition.face_locations(image)
face_encodings = face_recognition.face_encodings(image, face_locations)

# Save the face encodings to a numpy array file
np.save("face_encodings.npy", np.asarray(face_encodings))

