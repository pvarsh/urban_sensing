from datetime import datetime
from multiprocessing import Process, Pipe
import os
import requests
import time

import picamera
import picamera.array

        
class RatDetector():
    """A rat detector based on RPi image capture and analysis"""

    def __init__(self):
        # Camera parameters
        self.resolution = (640, 480)
        self.framerate = 10
        # API parameters
        self.public_key = os.getenv('SPARKFUN_PUBLIC_KEY')
        self.private_key = os.getenv('SPARKFUN_PRIVATE_KEY')

    def _stream_images(self, conn):
        print "Initializing image generator..."
        # Open camera and array stream
        with picamera.PiCamera() as camera:
            # Set camera parameters
            camera.resolution = self.resolution
            camera.framerate = self.framerate
            with picamera.array.PiRGBArray(camera) as stream:
                # Allow camera to warm up
                "Camera warming up..."
                time.sleep(2.0)
                # Begin a continuous stream of pictures
                "Capturing images..."
                for frame in camera.capture_continuous(
                    stream, format='bgr', use_video_port=True):
                    # Pipe out the array
                    conn.send(frame.array)
                    # Empty buffer for next image
                    stream.truncate(0)

    def _process_images(self, conn):
        print "Initializing image processor..."
        count = 0
        while True:
            image = conn.recv()
            count += 1
            print "[{0}] Processing item {1}, with dimensions: {2}".format(
                datetime.now(), count, image.shape)

            if (count % 10) == 0:
                self._upload_data(0)

    def _upload_data(self, count):
        url = 'https://data.sparkfun.com/input/{0}'.format(self.public_key)
        headers = {
            'Content-type': 'application/x-www-form-urlencoded',
            'Phant-Private-Key': self.private_key}
        data = {
            'count': count,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        requests.post(url, headers=headers, data=data)

    def run(self):
        try:
            print "Initializing image pipeline..."
            # Define a one-way data pipe
            recv_conn, send_conn = Pipe(duplex=False)
            # Define the two processes
            image_generator = Process(
                target=self._stream_images, 
                args=(send_conn,))
            image_processor = Process(
                target=self._process_images, 
                args=(recv_conn,))
            # Start the two processes
            image_generator.start()
            image_processor.start()
        except:
            print "Killing image pipeline..."
            # End the two processes
            image_generator.join()
            image_processor.join()
            return


if __name__ == '__main__':
    print "Beginning run of RatDetector..."
    rat_detector = RatDetector()
    rat_detector.run()
