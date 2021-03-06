# USAGE
# python track.py --video video/sample.mov

# import the necessary packages
import numpy as np
import argparse
import cv2
import scipy.ndimage as nd
import os
import glob
import time


def main():
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video",
                    help="path to the (optional) video file")
    ap.add_argument("-im", "--images",
                    help="path to the images folder")
    args = vars(ap.parse_args())

    # load argument and take action
    if not args.get("video", False) and not args.get("images", False):
        camera = cv2.VideoCapture(0)
        _if_camera(camera)
    elif not args.get("video", False) and args.get("images", True):
        frames_path = os.path.join(args["images"], "*.png")
        _if_images(frames_path)
    else:
        camera = cv2.VideoCapture(args["video"])
        _if_camera(camera)


def _if_images(frames_path):
    """If list of images
    """
    # read images
    frames_paths = [p for p in glob.glob(frames_path)]
    frames = np.array([nd.imread(p) for p in frames_paths])

    # start dilatation, erosion and mass label
    bdilation = nd.morphology.binary_dilation
    berosion = nd.morphology.binary_erosion
    meas_label = nd.measurements.label

    # for frame in frames:
    #     frame = np.square(frame) * 255.
    #     frame = frames / frame.max()

    # compute background using mean of im
    background = frames.mean(axis=3).mean(axis=0)

    for frame in frames:
        # cv2.imshow("frame", background)
        stop = rat_detector(grabbed=True,
                            frame=frame,
                            background=background,
                            bdilation=bdilation,
                            berosion=berosion,
                            meas_label=meas_label)

        time.sleep(1. / 15)


def _if_camera(camera):
    # start dilatation, erosion and mass label
    bdilation = nd.morphology.binary_dilation
    berosion = nd.morphology.binary_erosion
    meas_label = nd.measurements.label

    # grab background
    (grabbed, background) = camera.read()
    background = background.mean(axis=2)

    while True:
        # grab the current frame
        (grabbed, frame) = camera.read()
        stop = rat_detector(grabbed=grabbed,
                            frame=frame,
                            background=background,
                            bdilation=bdilation,
                            berosion=berosion,
                            meas_label=meas_label)
        if stop:
            break
    camera.release()
    cv2.destroyAllWindows()


def rat_detector(frame, background,
                 bdilation, berosion, meas_label, grabbed=True):
    """This function detects rat within img"""

    # set binarizing threshold value
    th = 15

    # compute gray_scale
    frame_mean = frame.mean(axis=2)

    # compute difference
    diff = ((frame_mean - background) > th) * 1.

    # set size threshold for blobs size
    sz_thr = th + 5
    diff = bdilation(berosion(np.abs(diff),
                     iterations=2), iterations=20) * 1.

    # label blobs
    labs = meas_label(diff)

    # reset diff
    diff[:] = 0

    # just candidate blobs to diff
    rats = 0
    for lab in range(1, labs[1] + 1):
        if 1. * (labs[0] == lab).sum() > sz_thr:
            rats += 1
            diff += (labs[0] == lab) * 1.
            cnt = ((labs[0] == lab) * 255).astype(np.uint8)
            contours, hierarchy = cv2.findContours(cnt, 1, 2)
            cnt = contours[-1]

            # enclosing rectangle - not used
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(frame, (x, y), (x + w, y + h),
                          (0, 255, 0), 1)

    # check to see if we have reached the end of the video
    if not grabbed:
        return True

    # display number of rats
    cv2.putText(frame, "Rats in Scene: {}".format(rats), (10, 20),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    cv2.imshow("frame", frame)
    # cv2.imshow("diff", diff)

    # if the 'q' key is pressed, stop the loop
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        return True

if __name__ == "__main__":
    main()
