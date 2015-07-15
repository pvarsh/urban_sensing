#!/usr/bin/python

import datetime
import os
import time
import picamera


# set some constants
SLEEP_TIME = 0.5 # seconds 
NUM_IMAGES = 60
IMG_PATH = '/home/pi/projects/rats/img'

camera = picamera.PiCamera()

now = time.time()
now_str = datetime.datetime.fromtimestamp(now).strftime('%Y%m%d_%H%M%S')
print now_str

for idx in range(NUM_IMAGES):
    img_name = "{}_{:03d}.png".format(now_str, idx)
    img_path = os.path.join(IMG_PATH, img_name)
    camera.capture(img_path)
