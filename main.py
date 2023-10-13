import numpy as np
import cv2
import face_recognition
import os
import datetime
import mysql.connector
import pyttsx3
def LoadEncodings(dir):
    faces=os.listdir(dir)
    images_known = []
    for x in faces:
        images_known.append(dir+"/"+x)
    known_face_encodings = []
    known_face_names = []
    for x in images_known:
        known_image = face_recognition.load_image_file(x)
        known_face_encoding = face_recognition.face_encodings(known_image,model="large")[0]
        known_face_encodings.append(known_face_encoding)
        known_face_names.append(os.path.basename(x))

    return known_face_encodings,known_face_names



def WebcamFaceRecognition(encodings_path):
    video_capture = cv2.VideoCapture(0)
    known_face_encodings, known_face_names = LoadEncodings(encodings_path)

    engine = pyttsx3.init()

    while True:
        ret, frame = video_capture.read()
        face_locations = face_recognition.face_locations(frame, model="cnn")
        face_encodings = face_recognition.face_encodings(frame, face_locations, model="large")
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                ct = datetime.datetime.now()
                name_with_extension = known_face_names[best_match_index]
                name = os.path.splitext(name_with_extension)[0]

                # Check if entry already exists for the day
                mydb = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="1234",
                    database="facerecognition"
                )
                mycursor = mydb.cursor()
                sql = "SELECT * FROM log WHERE DATE(date) = %s"
                val = (ct.date(), )
                mycursor.execute(sql, val)
                results = mycursor.fetchall()
                name_exists = False
                for result in results:
                    if os.path.splitext(result[1])[0] == name:
                        name_exists = True
                        break
                if not name_exists:
                    # Insert new entry if name is unique for the day
                    sql = "INSERT INTO log (name, date) VALUES (%s, %s)"
                    val = (name, ct)
                    mycursor.execute(sql, val)
                    mydb.commit()

                    # Convert name to speech
                    engine.say(f"Hello {name}!")
                    engine.runAndWait()

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()






WebcamFaceRecognition("known_people")

