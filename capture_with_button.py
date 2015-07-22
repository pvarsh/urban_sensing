import datetime
import os
import time

import picamera
from RPi import GPIO


# set some constants
LED_PIN = 4
BUTTON_PIN = 18
NUM_IMAGES = 120
FRAME_RATE = 15
RESOLUTION = (800, 600)

def cleanup_and_raise(exc):
    print("\nCleaning up GPIO")
    GPIO.cleanup()
    raise exc

def setup_GPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(LED_PIN, GPIO.OUT)

def main():
    
    setup_GPIO()
   
    while True:
       
        # wait for button press
        GPIO.wait_for_edge(BUTTON_PIN, GPIO.BOTH)
        
        # get time for time signatures. another way to do that would be with
        # {counter} and {timestamp} formats
        # see http://picamera.readthedocs.org/en/release-1.6/api.html#picamera.PiCamera.capture_continuous
        now = time.time()
        now_str = datetime.datetime.fromtimestamp(now).strftime('%Y%m%d_%H%M%S')
        print("Files will have this timestamp: {}".format(now_str)) 
        # set filepaths to save captured images to
        img_filenames = [
            'img_{}_{:02d}.png'.format(now_str, i) for i in range(NUM_IMAGES)
            ]

        img_filepaths = [
            os.path.join('/home/pi/projects/rats/img', fn) for fn in img_filenames
            ]

        # capture and save images
        with picamera.PiCamera() as camera:
            camera.resolution = RESOLUTION 
            camera.framerate = FRAME_RATE
            GPIO.output(LED_PIN, True)
            camera.capture_sequence(img_filepaths, use_video_port=True)
            GPIO.output(LED_PIN, False)

if __name__ == "__main__":
    try:
        main()

    # somehow this code does not catch exceptions
    # I think it worked before I added GPIO.wait_for_edge() in main()
    except KeyboardInterrupt, exc:
        cleanup_and_raise(exc)
    except Exception, exc:
        cleanup_and_raise(exc)
    
    # clean up on normal exit
    print("\nCleaning up GPIO")
    GPIO.cleanup()

