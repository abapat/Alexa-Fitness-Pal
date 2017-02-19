#!/usr/bin/python

import smbus
import math
import time # Power management registers

import RPi.GPIO as GPIO
import socket
import requests
import detect_pushup
import logging
import json
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

logging.basicConfig()
pnconfig = PNConfiguration()

pnconfig.subscribe_key = "sub-c-889dd4f6-f67a-11e6-bb94-0619f8945a4f"
pnconfig.publish_key = "pub-c-ffbcc603-c1c8-4168-a8c0-4c060d6ee36a"
pubnub = PubNub(pnconfig)

power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c
BUTTON = 19
PUSHUP_X = 20
PUSHUP_COUNT = 0
PORT = 5800

RED = 17
GREEN = 18
BLUE = 27
FREQ = 100 #pwm
COLORS = {'off':[0,0,0], 'red':[100,0,0], 'blue':[0,0,100], 'green':[0,50,0], 'yellow':[100,100,0], 'purple':[50,0,50]}

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RED, GPIO.OUT)
GPIO.setup(GREEN, GPIO.OUT)
GPIO.setup(BLUE ,GPIO.OUT)

DEVICE_ID = 1
DEVICE_NAME = "IOT DEVICE 1" #hardcode
SERVER = "https://hack-it-cewit.herokuapp.com"
REGISTER_URL = "/api/iot/device"
DATA_URL = "/api/iot/user"
IP = "104.236.238.240"

bus = smbus.SMBus(1)# or bus = smbus.SMBus(1) for Revision 2 boards
address = 0x68# This is the address value read via the i2cdetect command# Now wake the 6050 up as it starts in sleep mode
bus.write_byte_data(address, power_mgmt_1, 0)

def my_publish_callback(envelope, status):
    # Check whether request successfully completed or not
    if not status.is_error():
        pass  # Message successfully published to specified channel.
    else:
        print("Error: some error occured when publishing message")
        pass  # Handle message publish error. Check 'category' property to find out possible issue
        # because of which request did fail.
        # Request can be resent using: [status retry];

class MySubscribeCallback(SubscribeCallback):
    def presence(self, pubnub, presence):
        pass  # handle incoming presence data

    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            pass  # This event happens when radio / connectivity is lost

        elif status.category == PNStatusCategory.PNConnectedCategory:
            pass
            # Connect event. You can do stuff like publish, and know you'll get it.
            # Or just use the connected event to confirm you are subscribed for
            # UI / internal notifications, etc

        elif status.category == PNStatusCategory.PNReconnectedCategory:
            pass
            # Happens as part of our regular operation. This event happens when
            # radio / connectivity is lost, then regained.
        elif status.category == PNStatusCategory.PNDecryptionErrorCategory:
            pass
            # Handle message decryption error. Probably client configured to
            # encrypt messages and on live data feed it received plain text.

    def message(self, pubnub, message):
        workout = message.message['text']
        if workout == "push ups":
            color("orange")
            waitForButton()
            res = analyzePushups()
            print(res)
            if res:
                sendData("push ups", getRating(res), str(len(res)))
                pubnub.publish().channel("Channel-3ckelhgj1").message("done").async(my_publish_callback)
        elif workout == "squats":
            print("squats")
        else:
            print("jumping jacks")

def registerDevice():
    data = {'user_id': DEVICE_NAME, 'device_id': DEVICE_ID, 'is_active': 1}
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
    r = requests.post(SERVER + REGISTER_URL, json=data, headers=headers)
    if r.status_code != 200:
        print("Error %d: %s" % (r.status_code, r.reason))

def sendData(excercise, rating, improvements):
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
    if improvements:
        payload = {'exercise': excercise, 'rating': rating, 'improvements': improvements, 'device_id': DEVICE_ID}
    else:
        payload = {'exercise': excercise, 'rating': rating, 'device_id': DEVICE_ID}
    r = requests.post(SERVER + DATA_URL, json=payload,headers=headers )
    if r.status_code != 200:
        print("Error %d: %s" % (r.status_code, r.reason))

def getKey():
    with open("keys", "r") as f:
        key = f.read()
    return key

def setupLed():
    global RED
    global GREEN
    global BLUE
    RED = GPIO.PWM(RED, FREQ)
    RED.start(0)
    GREEN = GPIO.PWM(GREEN, FREQ)
    GREEN.start(0)
    BLUE = GPIO.PWM(BLUE, FREQ)
    BLUE.start(0)

def c(r,g,b):
    global RED
    global GREEN
    global BLUE
    RED.ChangeDutyCycle(r)
    GREEN.ChangeDutyCycle(g)
    BLUE.ChangeDutyCycle(b)

def color(c):
    global RED
    global GREEN
    global BLUE
    tup = [100, 100, 100]
    if c in COLORS:
        tup = COLORS[c]

    RED.ChangeDutyCycle(tup[0])
    GREEN.ChangeDutyCycle(tup[1])
    BLUE.ChangeDutyCycle(tup[2])

def read_byte(adr):
    return bus.read_byte_data(address, adr)

def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr + 1)
    val = (high << 8) + low
    return val

def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def dist(a, b):
    return math.sqrt((a * a) + (b * b))

def get_y_rotation(x, y, z):
    radians = math.atan2(x, dist(y, z))
    return -math.degrees(radians)

def get_x_rotation(x, y, z):
    radians = math.atan2(y, dist(x, z))
    return math.degrees(radians)

def getRawData():
    gyro_xout = read_word_2c(0x43)
    gyro_yout = read_word_2c(0x45)
    gyro_zout = read_word_2c(0x47)
    accel_xout = read_word_2c(0x3b)
    accel_yout = read_word_2c(0x3d)
    accel_zout = read_word_2c(0x3f)
    x = get_x_rotation(accel_xout, accel_yout, accel_zout)
    y = get_y_rotation(accel_xout, accel_yout, accel_zout)
    return (gyro_xout, gyro_yout, gyro_zout, accel_xout, accel_yout, accel_zout, x, y)

def getScaledData():
    gyrox = read_word_2c(0x43) / 131
    gyroy = read_word_2c(0x45) / 131
    gyroz = read_word_2c(0x47) / 131
    accelx = read_word_2c(0x3b) / 16384.0
    accely = read_word_2c(0x3d) / 16384.0
    accelz = read_word_2c(0x3f) / 16384.0
    x = get_x_rotation(accelx, accely, accelz)
    y = get_y_rotation(accelx, accely, accelz)
    return (gyrox, gyroy, gyroz, accelx, accely, accelz, x, y)

def printData(tup):
    print "gyro_xout : ", tup[0]
    print "gyro_yout : ", tup[1]
    print "gyro_zout : ", tup[2]
    print "accel_xout: ", tup[3]
    print "accel_yout: ", tup[4]
    print "accel_zout: ", tup[5]
    print "x rotation: ", tup[6]
    print "y rotation: ", tup[7]
    print("\n")

def log(tup, f):
    s = "%s,%s,%s,%s,%s,%s,%s,%s\n" % (str(tup[0]), str(tup[1]), str(tup[2]), str(tup[3]), str(tup[4]), str(tup[5]), str(tup[6]), str(tup[7]))
    print(s)
    f.write(s)

def logData():
    scaled = open("scaled_data", "w")
    raw = open("raw_data.txt", "w")
    state = 0
    while True:
        input_state = GPIO.input(BUTTON)
        if input_state == False:
            state += 1
            state = state % 2 #flip bit
            print("Pressed, state=%d" % state)
            time.sleep(0.2)

        if state == 1:
            color("purple")
            time.sleep(0.1)
            raw_data = getRawData()
            log(raw_data, raw)
            scaled_data = getAverageData()
            log(scaled_data, scaled)
            printData(scaled_data)
            time.sleep(0.5)
            state = 1
        else:
            color("off")

def getAverageData(n=5,sleep=0.05):
    arr = []
    for i in range(0,n):
        arr.append(getScaledData())
        time.sleep(sleep)

    ans = []
    for i in range(0,8):
        s = 0
        for val in arr:
            s += val[i]
        avg = float(s) / float(len(arr))
        ans.append(avg)
    return ans

def pushup():
    #avg = getAverageData()
    #print("Average: " + str(avg))
    bool_down = True
    x_rot = [(0,0,0,0,0,0,0,-90)] #Max negative
    cont = 1
    while cont:
        data = getAverageData()
        x = data[7]

        if bool_down:
            #going down
            if x >= x_rot[-1][7]:
                x_rot.append(data)
            else:
                bool_down = False
                x_rot.append(data) #peak
        else:
            #going up
            if x < x_rot[-1][7]:
                x_rot.append(data)
            else:
                cont = False

    return x_rot[1:] #dont include max neg

def isPushup(data):
    MIN = data[0][7]
    MAX = data[0][7]
    for d in data:
        if d[7] < MIN:
            MIN = d[7]
        if d[7] > MAX:
            MAX = d[7]

    diff = MAX - MIN
    print("DIFF: %s" % diff)

    if diff < PUSHUP_X:
        color("red")
        return False
    elif diff > PUSHUP_X and diff < PUSHUP_X + 10:
        color("yellow")
    else:
        color("green")

    return True

def relay():
    s = socket.socket()
    s.connect(("172.30.0.219",12345))
    while GPIO.input(BUTTON) == True:
        time.sleep(0.1)
    while True:
        if isPushup(pushup()):
            s.send("1")
        else:
            s.send("0")
        #input_state = GPIO.input(BUTTON)
        #if input_state == False:
        #    print(pushup())

def waitForButton():
    while GPIO.input(BUTTON) == True:
        time.sleep(0.1)

def analyzePushups():
    color("off")
    arr = []
    errCount = 3
    color("blue")
    while errCount > 0:
        data = pushup()
        if isPushup(data):
            arr += data
            errCount = 3
        else:
            errCount -= 1

    color("off")
    if len(arr) < 5:
        return None
    return detect_pushup.detect_pushup(arr)

def colorTest():
    for x in range(0,2):
        for y in range(0,2):
            for z in range(0,2):
                for i in range(0,101):
                    c((x*i),(y*i),(z*i))
                    time.sleep(0.02)

def getRating(res):
    avg = 0.0
    for val in res:
        avg += val
    avg = avg / float(len(res))

    if avg > 1:
        return 1.0
    return avg

def main():
    setupLed()

    sendData("squats", 0.89, "5")

    #pubnub.add_listener(MySubscribeCallback())
    #pubnub.subscribe().channels('Channel-3ckelhgj1').execute()

if __name__ == '__main__':
    main()
