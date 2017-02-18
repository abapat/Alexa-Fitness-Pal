import numpy as np
import cv2
import time


i = 0
fname = "posImages/IMG_00"
time.sleep(5)

cap = cv2.VideoCapture(0)

while(i<50):
    i+=1
    # Capture frame-by-frame
    ret, frame = cap.read()
    # Display the resulting frame
    cv2.imshow('Video', frame)
    cv2.imwrite(fname + str(i) + ".jpg", frame)
    if cv2.waitKey(1) & 0xFF == ord('q') or i > 100:
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()