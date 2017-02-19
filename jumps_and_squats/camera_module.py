import cv2
import math
import time
from picamera.array import PiRGBArray
from picamera import PiCamera
import smbus
import RPi.GPIO as GPIO
import socket
import requests
import detect_jumps
import detect_squats


DEVICE_ID = 2
DEVICE_NAME = "IOT Device 2" #hardcode
SERVER = "http://hack-it-cewit.herokuapp.com"
REGISTER_URL = "/api/iot/device"
DATA_URL = "/api/iot/user"
IP = "104.236.238.240"
PORT = 5800
BUTTON = 19

power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c

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

def registerDevice():
    data = {'user_id': DEVICE_NAME, 'device_id': DEVICE_ID, 'is_active': 1}
    r = requests.post(SERVER + REGISTER_URL, params=data)
    if r.status_code != 200:
        print("Error %d: %s" % (r.status_code, r.reason))

def sendData(excercise, rating, improvements):
    if improvements:
        data = {'excercise': excercise, 'rating': rating, 'improvements': improvements, 'device_id': DEVICE_ID}
    else:
        data = {'excercise': excercise, 'rating': rating, 'device_id': deviceID}
    r = requests.post(SERVER + DATA_URL, params=data)
    if r.status_code != 200:
        print("Error %d: %s" % (r.status_code, r.reason))


def waitForButton():
    while GPIO.input(BUTTON) == True:
        time.sleep(0.1)

def main():
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect((IP,PORT))
    #wait for pub to know which workout to do
    waitForButton()
    while True:
        bit = sock.recv(1)
        if bit == "1":
            res = detect_squats.get_movements()
            print(res)


if __name__ == '__main__':
    main()