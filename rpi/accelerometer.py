#!/usr/bin/python
import smbus
import math
import time # Power management registers
import RPi.GPIO as GPIO
import socket

power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c
LED_PIN = 18
BUTTON = 19
PUSHUP_X = 20

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_PIN,GPIO.OUT)

bus = smbus.SMBus(1)# or bus = smbus.SMBus(1) for Revision 2 boards
address = 0x68# This is the address value read via the i2cdetect command# Now wake the 6050 up as it starts in sleep mode
bus.write_byte_data(address, power_mgmt_1, 0)

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
            GPIO.output(LED_PIN,GPIO.HIGH)
            time.sleep(0.1)
            raw_data = getRawData()
            log(raw_data, raw)
            scaled_data = getAverageData()
            log(scaled_data, scaled)
            printData(scaled_data)
            time.sleep(0.5)
            state = 1
        else:
            GPIO.output(LED_PIN,GPIO.LOW)

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
    x_rot = [-90] #Max negative
    cont = 1
    while cont:
        GPIO.output(LED_PIN,GPIO.HIGH)
        data = getAverageData()
        x = data[7]

        if bool_down:
            #going down
            if x >= x_rot[-1]:
                x_rot.append(x)
            else:
                bool_down = False
                x_rot.append(x) #peak
        else:
            #going up
            if x < x_rot[-1]:
                x_rot.append(x)
            else:
                cont = False

    GPIO.output(LED_PIN,GPIO.LOW)
    return x_rot[1:] #dont include max neg

def isPushup(data):
    diff = max(data) - min(data)
    print("DATA: %s\nDIFF: %s\n\n" % (data, diff))
    if diff < PUSHUP_X:
        return False

    return True

def main():
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

if __name__ == '__main__':
    logData()
