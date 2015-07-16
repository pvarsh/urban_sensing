import time

import picamera
import RPi.GPIO as GPIO


# set some constants
LED_PIN = 4
BUTTON_PIN = 18
NUM_IMAGES = 6
FRAME_RATE = 2
RESOLUTION = (1024, 768)

def cleanup_and_raise(exc):
    print("\nCleaning up GPIO")
    GPIO.cleanup()
    raise exc

def main_():
    GPIO.setmode(GPIO.BCM)
    
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(LED_PIN, GPIO.OUT)
    
    prev_input_state = GPIO.input(BUTTON_PIN)
    while True:
        input_state = GPIO.input(BUTTON_PIN)
        if input_state != prev_input_state:
            print("Button pressed")
            if input_state == 1:
                GPIO.output(LED_PIN, True)
            else:
                GPIO.output(LED_PIN, False)
            prev_input_state = input_state
        time.sleep(0.05)

def setup_GPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(LED_PIN, GPIO.OUT)

def main():
    
    setup_GPIO()
   
    while True:
        
        GPIO.wait_for_edge(BUTTON_PIN, GPIO.BOTH)
        now = time.time()
        now_str = datetime.datetime.fromtimestamp(now).strftime('%Y%m%d_%H%M%S')

        img_filenames = (
            'img_{}_{:02d}.png'.format(now_str, i) for i in range(NUM_IMAGES)
            )            

        img_filepaths = (
            os.path.join('/home/pi/projects/rats', fn) for fn in img_filenames
            )

        with picamera.PiCamera() as camera:
            camera.resolution = RESOLUTION 
            camera.framerate = FRAME_RATE
            GPIO.output(LED_PIN, True)
            camera.capture_sequence(img_filepaths)
            GPIO.output(LED_PIN, False)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt, exc:
        cleanup_and_raise(exc)
    except Exception, exc:
        cleanup_and_raise(exc)
    
    # clean up on normal exit
    print("\nCleaning up GPIO")
    GPIO.cleanup()

