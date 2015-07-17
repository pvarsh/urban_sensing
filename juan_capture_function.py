def streaming_function(samples):
    stream = io.BytesIO()
    for i in range(samples):
        yield stream
        stream.seek(0)
        # Do something with stream
        stream.truncate(0)
        stream.seek(0)

def get_data(samples):
    # Fix Camera Parameters #
    with picamera.PiCamera() as camera:
        camera.led = False
        camera.resolution = (1024, 768)
        camera.iso = 200
        camera.framerate = 10
        time.sleep(2)
        camera.shutter_speed = camera.exposure_speed
        camera.exposure_mode = 'off'
        g = camera.awb_gains
        camera.awb_mode = 'off'
        camera.awb_gains = g

        # Record Data #
        camera.capture_sequence(
            streaming_function(samples),
            'jpeg', use_video_port=True)
