#python drowniness_yawn.py --webcam webcam_index

from scipy.spatial import distance as dist
try:
    from imutils.video import VideoStream
except Exception:
    # Fallback simple VideoStream wrapper using cv2.VideoCapture when imutils.video isn't available
    class VideoStream:
        def __init__(self, src=0, usePiCamera=False):
            if usePiCamera:
                raise NotImplementedError("PiCamera is not supported in fallback VideoStream")
            import cv2
            self.stream = cv2.VideoCapture(src)
        def start(self):
            # match imutils' VideoStream.start() by returning self
            return self
        def read(self):
            ret, frame = self.stream.read()
            return frame
        def stop(self):
            self.stream.release()

from imutils import face_utils
from threading import Thread
import numpy as np
import argparse
import imutils
import time
import dlib
import cv2
import playsound
import os


def sound_alarm(path):
    global alarm_status
    global alarm_status2
    global saying

    while alarm_status:
        print('call')
        playsound.playsound(path)
    if alarm_status2:
        print('call')
        saying = True
        playsound.playsound(path)
        saying = False

def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])

    C = dist.euclidean(eye[0], eye[3])

    ear = (A + B) / (2.0 * C)

    return ear

def final_ear(shape):
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

    leftEye = shape[lStart:lEnd]
    rightEye = shape[rStart:rEnd]

    leftEAR = eye_aspect_ratio(leftEye)
    rightEAR = eye_aspect_ratio(rightEye)

    ear = (leftEAR + rightEAR) / 2.0
    return (ear, leftEye, rightEye)

def lip_distance(shape):
    top_lip = shape[50:53]
    top_lip = np.concatenate((top_lip, shape[61:64]))

    low_lip = shape[56:59]
    low_lip = np.concatenate((low_lip, shape[65:68]))

    top_mean = np.mean(top_lip, axis=0)
    low_mean = np.mean(low_lip, axis=0)

    distance = abs(top_mean[1] - low_mean[1])
    return distance


ap = argparse.ArgumentParser()
ap.add_argument("-w", "--webcam", type=int, default=0,
                help="index of webcam on system")
ap.add_argument("-a", "--alarm", type=str, default="Alert.wav", help="path alarm .WAV file")
args = vars(ap.parse_args())

EYE_AR_THRESH = 0.3
EYE_AR_CONSEC_FRAMES = 30
YAWN_THRESH = 20
alarm_status = False
alarm_status2 = False
saying = False
COUNTER = 0

RUN_APP = True

# Coordinates for the on-screen Quit button (adjusted for 450px width)
BTN_X1, BTN_Y1 = 350, 10
BTN_X2, BTN_Y2 = 440, 40

def mouse_callback(event, x, y, flags, param):
    """Mouse callback to handle clicks on the video window buttons.

    If the user clicks the Quit button, set RUN_APP to False to stop the loop.
    """
    global RUN_APP
    if event == cv2.EVENT_LBUTTONDOWN:
        bx1, by1, bx2, by2 = param
        if bx1 <= x <= bx2 and by1 <= y <= by2:
            RUN_APP = False
print("-> Loading the predictor and detector...")
#detector = dlib.get_frontal_face_detector()
detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")    #Faster but less accurate
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')


# Create display window and set mouse callback for button clicks
print("-> Starting Video Stream")
cv2.namedWindow("Frame")
cv2.setMouseCallback("Frame", mouse_callback, (BTN_X1, BTN_Y1, BTN_X2, BTN_Y2))
vs = VideoStream(src=args["webcam"]).start()
#vs= VideoStream(usePiCamera=True).start()       //For Raspberry Pi
time.sleep(1.0)

while RUN_APP:

    frame = vs.read()
    if frame is None:
        print("Error: Could not read frame from webcam")
        break
    frame = imutils.resize(frame, width=450)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #rects = detector(gray, 0)
    rects = detector.detectMultiScale(gray, scaleFactor=1.1,
		minNeighbors=5, minSize=(30, 30),
		flags=cv2.CASCADE_SCALE_IMAGE)

    #for rect in rects:
    for (x, y, w, h) in rects:
        rect = dlib.rectangle(int(x), int(y), int(x + w),int(y + h))

        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        eye = final_ear(shape)
        ear = eye[0]
        leftEye = eye [1]
        rightEye = eye[2]

        distance = lip_distance(shape)

        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

        lip = shape[48:60]
        cv2.drawContours(frame, [lip], -1, (0, 255, 0), 1)

        if ear < EYE_AR_THRESH:
            COUNTER += 1

            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                if alarm_status == False:
                    alarm_status = True
                    if args["alarm"] != "":
                        t = Thread(target=sound_alarm,
                                   args=(args["alarm"],))
                    t.daemon = True
                    t.start()

                cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        else:
            COUNTER = 0
            alarm_status = False

        if (distance > YAWN_THRESH):
                cv2.putText(frame, "Yawn Alert", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                if alarm_status2 == False and saying == False:
                    alarm_status2 = True
                    if args["alarm"] != "":
                        t = Thread(target=sound_alarm,
                                   args=(args["alarm"],))
                    t.daemon = True
                    t.start()
        else:
            alarm_status2 = False

        cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, "YAWN: {:.2f}".format(distance), (300, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)


    # Draw Quit button (red filled rectangle with white text)
    cv2.rectangle(frame, (BTN_X1, BTN_Y1), (BTN_X2, BTN_Y2), (0, 0, 255), -1)
    cv2.putText(frame, "Quit", (BTN_X1 + 18, BTN_Y2 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (255, 255, 255), 2)
    cv2.putText(frame, "Click Quit or press 'q' to exit", (10, 430), cv2.FONT_HERSHEY_SIMPLEX,
                0.45, (200, 200, 200), 1)

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        RUN_APP = False
        break

cv2.destroyAllWindows()
vs.stop()
