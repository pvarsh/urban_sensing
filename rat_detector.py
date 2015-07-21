from datetime import datetime
from multiprocessing import Process, Pipe
import os
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
        # self.public_key = os.getenv('SPARKFUN_PUBLIC_KEY')
        # self.private_key = os.getenv('SPARKFUN_PRIVATE_KEY')

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
        # Once stream ends, kill processing
        print "Killing image generator..."
        conn.send(False)
        conn.close()

    def _process_images(self, conn):
        print "Initializing image processor..."
        count = 0
        image = True
        while image:
            image = conn.recv()
            count += 1
            print "Processing item {0}, with dimensions: {1}".format(
                count, image.shape)
        
        print "Killing image processor..."
        conn.close()
        return

    # def _upload data(self, conn):
    #     url = 'http://data.sparkfun.com/input/{0}?private_key={1}&count={2}&timestamp={3}'.format(
    #         self.public_key, 
    #         self.private_key,
    #         count,
    #         datetime.now())

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
