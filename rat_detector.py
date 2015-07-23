from datetime import datetime
from multiprocessing import Process, Pipe
import os
import time

import cv2
import numpy as np
import requests
import scipy.ndimage as nd
import picamera
import picamera.array


class RatDetector():
    """A rat detector based on RPi image capture and analysis"""

    def __init__(self):
        # Camera parameters
        self.resolution = (600, 400)
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

    def _process_images(self, conn, api_conn):
        print "Initializing image processor..."
        count = 0
        bdilation = nd.morphology.binary_dilation
        berosion = nd.morphology.binary_erosion
        meas_label = nd.measurements.label

        while True:
            # initialize and update background
            frame = conn.recv()
            if count == 0:
                background = frame.mean(axis=2)
            else:
                background += frame.mean(axis=2)
                background /= 2
            # Set binarizing threshold value
            th = 15
            # Compute gray scale image
            frame_mean = frame.mean(axis=2)
            # Compute difference
            diff = ((frame_mean - background) > th) * 1.
            # Set size threshold for blobs size
            sz_thr = th + 5
            diff = bdilation(
                berosion(
                    np.abs(diff),
                    iterations=2), 
                iterations=20) * 1.0
            # Label blobs
            labs = meas_label(diff)
            # Reset diff
            diff[:] = 0
            # Just candidate blobs to diff
            rats = 0
            for lab in range(1, labs[1] + 1):
                if 1. * (labs[0] == lab).sum() > sz_thr:
                    rats += 1
                    diff += (labs[0] == lab) * 1.0
                    cnt = ((labs[0] == lab) * 255).astype(np.uint8)
                    contours, hierarchy = cv2.findContours(cnt, 1, 2)
                    cnt = contours[-1]
                    # enclosing rectangle - not used
                    x, y, w, h = cv2.boundingRect(cnt)
                    cv2.rectangle(
                        frame, 
                        (x, y), 
                        (x + w, y + h), 
                        (0, 255, 0), 
                        1)

            print "[{0}] Processing item {1}".format(
                datetime.now(), rats)

            count += 1
            if (count % 300) == 0:
                api_conn.send(count)

    def _upload_data(self, conn):
        print "Initializing data uploader..."
        url = 'https://data.sparkfun.com/input/{0}'.format(self.public_key)
        headers = {
            'Content-type': 'application/x-www-form-urlencoded',
            'Phant-Private-Key': self.private_key}
        while True:
            count = conn.recv()
            data = {
                'count': count,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            requests.post(url, headers=headers, data=data)

    def run(self):
        try:
            print "Initializing image pipeline..."
            # Define a one-way data pipe
            recv_conn, send_conn = Pipe(duplex=False)
            recv_api, send_api = Pipe(duplex=False)
            # Define the processes
            image_generator = Process(
                target=self._stream_images,
                args=(send_conn,))
            image_processor = Process(
                target=self._process_images,
                args=(recv_conn, send_api))
            data_uploader = Process(
                target=self._upload_data,
                args=(recv_api,))
            # Start the processes
            image_generator.start()
            image_processor.start()
            data_uploader.start()
        except:
            print "Killing image pipeline..."
            # End the processes
            image_generator.join()
            image_processor.join()
            data_uploader.join()
            return


if __name__ == '__main__':
    print "Beginning run of RatDetector..."
    rat_detector = RatDetector()
    rat_detector.run()
