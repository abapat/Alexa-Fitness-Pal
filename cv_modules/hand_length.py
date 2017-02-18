import cv2
import numpy as np

cFlag_ = False
def mClick(event, x, y, flags, param):
    global cFlag_
    if event == cv2.EVENT_LBUTTONDOWN or event == cv2.EVENT_LBUTTONUP or event == cv2.EVENT_MOUSEMOVE:
        cFlag_ = True


video_capture = cv2.VideoCapture(0)

while not cFlag_:
    ret, frame = video_capture.read()

    kernel = np.ones((20, 20), np.uint8)
    erosed_frame = cv2.erode(frame,kernel,iterations = 1)

    gray = cv2.cvtColor(erosed_frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)


    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

    if lines is not None:
        for rho, theta in lines[0]:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * (a))
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * (a))

            cv2.line(erosed_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

    cv2.namedWindow('Video')
    cv2.setMouseCallback('Video', mClick)
    cv2.imshow('Video', erosed_frame)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()