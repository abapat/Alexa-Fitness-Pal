import numpy as np
import cv2
import time
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
fgbg = cv2.createBackgroundSubtractorMOG2()
i = 0
fname = "negImages/IMG_00"
wfname = "cropImages/IMG_00"
for i in range(10, 100):
    img = cv2.imread(fname + str(i) + ".jpg",0)
    fgmask = fgbg.apply(img)
    fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)
    cv2.imwrite(wfname + str(i) + ".jpg", fgmask[100:800,0:700])
    # cv2.imshow('Image', fgmask[100:800,0:700])
    # cv2.waitKey()