import cv2
import math
from picamera.array import PiRGBArray
from picamera import PiCamera
import time

cFlag_ = False
def mClick(event, x, y, flags, param):
    global cFlag_
    if event == cv2.EVENT_LBUTTONDOWN or event == cv2.EVENT_LBUTTONUP or event == cv2.EVENT_MOUSEMOVE:
        cFlag_ = True


cascPath = 'haarcascade_frontalface_default.xml'
faceCascade = cv2.CascadeClassifier(cascPath)

accumulator = [0,0]
movement_up = 0
movement_down = 0

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

# allow the camera to warmup
time.sleep(0.1)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        # flags=cv2.CASCADE_SCALE_IMAGE
    )

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 225, 225), 2)

        new_x = (x+w)/2
        new_y = (y+w)/2

        movement_x = new_x - accumulator[0]
        movement_y = accumulator[1] - new_y

        if(movement_y > 5):
            cv2.putText(frame, "You are moving face upwards", (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            if(movement_y > 50):
                cv2.putText(frame, "Aren't you moving too fast ?", (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        elif(movement_y < -5):
            cv2.putText(frame, "You are moving face downwards", (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            if (movement_y < -50):
                cv2.putText(frame, "Aren't you moving too fast ?", (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        else:
            cv2.putText(frame, "You are stable", (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        movement = math.sqrt(math.pow(movement_x,2) + math.pow(movement_y,2))

        accumulator = [(x+w)/2, (y+w)/2]


    cv2.namedWindow('Video')
    cv2.setMouseCallback('Video', mClick)
    cv2.imshow('Video', frame)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()