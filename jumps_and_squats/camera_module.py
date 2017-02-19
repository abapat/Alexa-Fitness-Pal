import cv2
import math
import time
from picamera.array import PiRGBArray
from picamera import PiCamera
import smbus
import RPi.GPIO as GPIO
import socket
import requests

from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

import detect_jumps
import detect_squats

pnconfig = PNConfiguration()

pnconfig.subscribe_key = 'sub-c-889dd4f6-f67a-11e6-bb94-0619f8945a4f'

pubnub = PubNub(pnconfig)



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


def my_publish_callback(envelope, status):
    # Check whether request successfully completed or not
    if not status.is_error():
        pass  # Message successfully published to specified channel.
    else:
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
            # Connect event. You can do stuff like publish, and know you'll get it.
            # Or just use the connected event to confirm you are subscribed for
            # UI / internal notifications, etc
            pubnub.publish().channel("Channel-3ckelhgj1").message("hello!!").async(my_publish_callback)
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
        if workout == "squats":
            # waitForButton()
            nSquats = detect_squats.get_movements()
            print(nSquats)
            if nSquats:
                sendData("squats", getRating(nSquats), nSquats)
        elif workout == "jumping jacks":
            # waitForButton()
            nJumps = detect_jumps.get_movements()
            print(nJumps)
            if nJumps:
                sendData("jumping jacks", getRating(nJumps), nJumps)
        else:
            print "push ups"


def getRating(num):
    if num > 10:
        return 0.7
    else:
        return 0.4



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
        data = {'excercise': excercise, 'rating': rating, 'device_id': DEVICE_ID}
    r = requests.post(SERVER + DATA_URL, params=data)
    if r.status_code != 200:
        print("Error %d: %s" % (r.status_code, r.reason))


def waitForButton():
    while GPIO.input(BUTTON) == True:
        time.sleep(0.1)

def main():
    pubnub.add_listener(MySubscribeCallback())
    pubnub.subscribe().channels('Channel-3ckelhgj1').execute()


if __name__ == '__main__':
    main()
