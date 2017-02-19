import cv2
import math
import time
from picamera.array import PiRGBArray
from picamera import PiCamera


def get_movements():
    # allow the camera to warmup
    time.sleep(3)

    numJumps = 0
    frnd_cnt = 0

    ustop = 0

    cascPath = 'haarcascade_frontalface_default.xml'
    faceCascade = cv2.CascadeClassifier(cascPath)

    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 32
    rawCapture = PiRGBArray(camera, size=(640, 480))

    accumulator = [0,0]
    movement_dir = 0

    t_end = time.time() + 30

    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

        frame = frame.array

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            # flags=cv2.CASCADE_SCALE_IMAGE
        )

        if faces is not None:
            # for (x, y, w, h) in faces:
            # cv2.putText(frame, str(len(faces)), (100, 50),
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            # cv2.putText(frame, str(numJumps), (500, 50),
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            if len(faces) > 1:
                frnd_cnt += 1
                # if(frnd_cnt > 5):
                #     cv2.putText(frame, "Can you ask your friend to move out ?", (100, 50),
                #                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            else:
                frnd_cnt -= 1
                try:
                    (x, y, w, h) = faces[0]
                    # cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 225, 225), 2)

                    # new_x = (x+w)/2
                    new_y = (y+w)/2

                    # movement_x = new_x - accumulator[0]
                    movement_y = accumulator[1] - new_y

                    if(movement_y > 5):
                        # cv2.putText(frame, "You are moving face upwards", (10, 20),
                        #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                        if(movement_y > 10):
                            ustop = 0
                            # cv2.putText(frame, "Aren't you moving too fast ?", (10, 50),
                            #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                            if(movement_dir == 0):
                                numJumps += 1
                            movement_dir = 1
                    elif(movement_y < -5):
                        # cv2.putText(frame, "You are moving face downwards", (10, 20),
                        #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                        if (movement_y < -10):
                            ustop = 0
                            # cv2.putText(frame, "Aren't you moving too fast ?", (10, 50),
                            #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                            if (movement_dir == 1):
                                numJumps += 1
                            movement_dir = 0
                    else:
                        ustop += 1
                        # cv2.putText(frame, "You are stable", (10, 20),
                        #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                    # movement = math.sqrt(math.pow(movement_x,2) + math.pow(movement_y,2))

                    accumulator = [(x+w)/2, (y+w)/2]
                except:
                    pass

        # cv2.namedWindow('Video')
        # cv2.imshow('Video', frame)

        if time.time() > t_end or ustop > 10:
            break

    cv2.destroyAllWindows()
    return numSquats
