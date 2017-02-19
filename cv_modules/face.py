import cv2
import sys
import scipy
import sklearn

cFlag_ = False
def mClick(event, x, y, flags, param):
    global cFlag_
    if event == cv2.EVENT_LBUTTONDOWN or event == cv2.EVENT_LBUTTONUP or event == cv2.EVENT_MOUSEMOVE:
        cFlag_ = True


cascPath = 'haarcascade_frontalface_default.xml'
faceCascade = cv2.CascadeClassifier(cascPath)

video_capture = cv2.VideoCapture(0)

while not cFlag_:
    ret, frame = video_capture.read()

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

    cv2.namedWindow('Video')
    cv2.setMouseCallback('Video', mClick)
    cv2.imshow('Video', frame)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
