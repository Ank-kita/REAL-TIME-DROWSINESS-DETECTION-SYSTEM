#python drowsiness_yawn_nolibdlib.py --webcam webcam_index
# Alternative implementation without dlib dependency, using OpenCV cascade classifiers

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

from threading import Thread
import numpy as np
import argparse
import imutils
import time
import cv2
import playsound
import os


def sound_alarm(path):
    global alarm_status
    global alarm_status2
    global saying

    while alarm_status:
        print('Alarm: Drowsiness Detected!')
        try:
            playsound.playsound(path)
        except Exception as e:
            print(f"Could not play sound: {e}")
    if alarm_status2:
        print('Alarm: Yawn Detected!')
        saying = True
        try:
            playsound.playsound(path)
        except Exception as e:
            print(f"Could not play sound: {e}")
        saying = False

def eye_aspect_ratio(eye):
    """Calculate eye aspect ratio"""
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    
    ear = (A + B) / (2.0 * C)
    return ear

def get_eye_contour(left_eye, right_eye):
    """Get convex hulls for eyes"""
    leftEyeHull = cv2.convexHull(left_eye)
    rightEyeHull = cv2.convexHull(right_eye)
    return leftEyeHull, rightEyeHull

def detect_eyes_simple(gray, x, y, w, h):
    """Detect eyes in a face region using cascade classifier"""
    roi_gray = gray[y:y+h, x:x+w]
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=5, minSize=(15, 15))
    
    # If eyes are detected, estimate eye landmarks for EAR calculation
    eye_landmarks = []
    if len(eyes) >= 2:
        # Sort eyes by x position (left to right)
        eyes_sorted = sorted(eyes, key=lambda e: e[0])
        for eye in eyes_sorted[:2]:  # Take first two eyes
            ex, ey, ew, eh = eye
            # Create approximate 6-point landmarks for EAR calculation
            points = np.array([
                [ex, ey + eh // 2],  # left
                [ex + ew // 4, ey],  # top-left
                [ex + 3 * ew // 4, ey],  # top-right
                [ex + ew, ey + eh // 2],  # right
                [ex + 3 * ew // 4, ey + eh],  # bottom-right
                [ex + ew // 4, ey + eh]  # bottom-left
            ], dtype=np.int32)
            eye_landmarks.append(points)
    
    return eye_landmarks

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
print("-> Loading the detector...")
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

print("-> Starting Video Stream")
cv2.namedWindow("Frame")
cv2.setMouseCallback("Frame", mouse_callback, (BTN_X1, BTN_Y1, BTN_X2, BTN_Y2))
vs = VideoStream(src=args["webcam"]).start()
time.sleep(1.0)

frame_count = 0

while RUN_APP:
    frame = vs.read()
    if frame is None:
        print("Error: Could not read frame from webcam")
        break
    
    frame = imutils.resize(frame, width=450)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1,
                                         minNeighbors=5, minSize=(30, 30),
                                         flags=cv2.CASCADE_SCALE_IMAGE)

    for (x, y, w, h) in faces:
        # Draw face rectangle
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]
        
        # Detect eyes in the face
        eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=5, minSize=(15, 15))
        
        # Simple drowsiness detection based on detected eyes
        if len(eyes) < 2:
            # Eyes not detected - likely closing or drowsy
            COUNTER += 1
            
            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                if alarm_status == False:
                    alarm_status = True
                    if args["alarm"] != "":
                        t = Thread(target=sound_alarm, args=(args["alarm"],))
                        t.daemon = True
                        t.start()
                cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            COUNTER = 0
            alarm_status = False
            
            # Draw eye rectangles
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
            
            cv2.putText(frame, f"Eyes Detected: {len(eyes)}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Simple yawn detection based on mouth opening (height difference)
        mouth_roi = roi_gray[3*h//4:h, :]
        mouth_height = mouth_roi.shape[0]
        mouth_width = mouth_roi.shape[1]
        
        # Check for open mouth (bright pixels in mouth region)
        _, thresh = cv2.threshold(mouth_roi, 127, 255, cv2.THRESH_BINARY)
        bright_pixels = np.sum(thresh > 200)
        mouth_open_ratio = bright_pixels / (mouth_height * mouth_width)
        
        if mouth_open_ratio > YAWN_THRESH / 100:  # Adjusted threshold
            cv2.putText(frame, "Yawn Alert", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            if alarm_status2 == False and saying == False:
                alarm_status2 = True
                if args["alarm"] != "":
                    t = Thread(target=sound_alarm, args=(args["alarm"],))
                    t.daemon = True
                    t.start()
        else:
            alarm_status2 = False

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
    
    frame_count += 1
    if frame_count % 30 == 0:
        print(f"Processed {frame_count} frames...")

cv2.destroyAllWindows()
vs.stop()
print("Application closed successfully!")
