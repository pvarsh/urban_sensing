import io
import math
import weight

import requests
import picamera
from set_stepper import *


def outputs(samples, steps, item_attributes, url):
    global start
    url_item = url + '/ecan/upload/'
    url_bg = url + '/ecan/upload-back_ground/'

    # Take photo of background #
    cont = 'n'
    print 'Prepare for back_ground capture'
    while cont != '1':
        cont = raw_input("ready? [1] ")
        if cont != '1':
            cont = 'n'

    # Start Camara Streaming #
    stream = io.BytesIO()
    for i in range(samples + 4):
        yield stream
        stream.seek(0)
        if i == 0:
            my_file_bg = stream
            data_bg = {'ecan': '1'}
            files_bg = {'im': my_file_bg}
            r = requests.post(url_bg, data=data_bg, files=files_bg)
            if r.json()['result'] == 'valid':
                bg_pk = r.json()['id']
                print r.json()['result'], 'back_ground id: ', r.json()['id']
            else:
                print 'Operation not completed'

            # Place Item and upload data #
            print 'Place item'
            cont = 'n'
            while cont != '1':
                cont = raw_input("ready? [1] ")
                if cont == '1':
                    item_attributes['weight'] = weight.get()
                if cont != '1':
                    cont = 'n'
            start = time.time()
        elif i > 3:
            my_file = stream
            item_attributes['bg'] = bg_pk
            item_attributes['ecan'] = '1'
            data_item = item_attributes
            files_item = {'im': my_file}
            r = requests.post(
                url_item, data=data_item, files=files_item)
            print r.text
            forward(20, steps)
        stream.truncate(0)
        stream.seek(0)


def get_data(samples, item_attributes, url):

    # Fix Camera Parameters #
    with picamera.PiCamera() as camera:
        camera.led = False
        global start
        start = 0
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
        steps = int(math.ceil(512. / samples))
        camera.capture_sequence(
            outputs(samples, steps, item_attributes, url),
            'jpeg', use_video_port=True)
        finish = time.time()
        print'Captured %s' % samples + ' images in %.2fs' % (finish - start)
    return 'done'


def get_preview(url):

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
        camera.capture('sample.jpg')
        data = {'ecan': '1'}
        files = {'im': open('sample.jpg', 'rb')}
        url_preview = url + '/ecan/upload-sample/'
        r = requests.post(url_preview, data=data, files=files)
        print r.text
    return 'done'


def predict(url):
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
        camera.capture('sample.jpg')
        data = {'ecan': '1'}
        files = {'im': open('sample.jpg', 'rb')}
        url_preview = url + '/ecan/predict/'
        r = requests.post(url_preview, data=data, files=files)
        print r.text
    return 'done'
