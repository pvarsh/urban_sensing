import time

import RPi.GPIO as GPIO


# set some constants
LED_PIN = 4
BUTTON_PIN = 18

def cleanup_and_raise(exc):
    print("\nCleaning up GPIO")
    GPIO.cleanup()
    raise exc

def main():
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


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt, exc:
        cleanup_and_raise(exc)
    except Exception, exc:
        cleanup_and_raise(exc)

