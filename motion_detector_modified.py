# USAGE
# python motion_detector.py
# python motion_detector.py --video videos/example_01.mp4

# import the necessary packages
import argparse
import datetime
import imutils
import time
import cv2

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument(
    "-a", "--min-area", type=int, default=200, help="minimum area size")
args = vars(ap.parse_args())

# if the video argument is None, then we are reading from webcam
if args.get("video", None) is None:
    camera = cv2.VideoCapture(0)
    time.sleep(0.25)

# otherwise, we are reading from a video file
else:
    camera = cv2.VideoCapture(args["video"])

# initialize the average frame, last
# uploaded timestamp, and frame motion counter
avg = None
motionCounter = 0
lastUploaded = datetime.datetime.now()
firstFrame = None

# loop over the frames of the video
while True:
    # grab the current frame and initialize the occupied/unoccupied
    # text
    (grabbed, frame) = camera.read()
    timestamp = datetime.datetime.now()
    text = "Unoccupied"
    text_abs = "Unoccupied"

    # if the frame could not be grabbed, then we have reached the end
    # of the video
    if not grabbed:
        break

    # resize the frame, convert it to grayscale, and blur it
    frame = imutils.resize(frame, width=500)
    #************** for first frame as ref *****************
    frame_abs = imutils.resize(frame, width=500)
    #*****************************************************************

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # if the average frame is None, initialize it
    if avg is None:
        print "[INFO] starting background model..."
        avg = gray.copy().astype("float")
        continue

    #************** for first frame as ref *****************
    # if the first frame is None, initialize it
    if firstFrame is None:
        firstFrame = gray
        continue
    #*****************************************************************

    # accumulate the weighted average between the current frame and
    # previous frames, then compute the difference between the current
    # frame and running average
    cv2.accumulateWeighted(gray, avg, 0.5)
    frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
    #************** for first frame as ref *****************
    frameDelta_abs = cv2.absdiff(firstFrame, gray)
    thresh_abs = cv2.threshold(frameDelta_abs, 25, 255, cv2.THRESH_BINARY)[1]

    # threshold the delta image, dilate the thresholded image to fill
    # in holes, then find contours on thresholded image
    thresh = cv2.threshold(frameDelta, 5, 255,
        cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    #************** for first frame as ref *****************
    thresh_abs = cv2.dilate(thresh_abs, None, iterations=2)
    (cnts_abs, _) = cv2.findContours(thresh_abs.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    #*****************************************************************

    # loop over the contours
    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < args["min_area"]:
            continue

        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        text = "Occupied"

    # draw the text and timestamp on the frame
    cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # check to see if the room is occupied
    if text == "Occupied":
        # increment the motion counter
        motionCounter += 1

        # check to see if the number of frames with consistent motion is
        # high enough
        if motionCounter >= 8:
            # update the last uploaded timestamp and reset the motion
            # counter
            lastUploaded = timestamp
            motionCounter = 0

    # otherwise, the room is not occupied
    else:
        motionCounter = 0

    #************** for first frame as ref *****************************
    for cabs in cnts_abs:
        # if the contour is too small, ignore it
        if cv2.contourArea(cabs) < args["min_area"]:
            continue

        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(cabs)
        cv2.rectangle(frame_abs, (x, y), (x + w, y + h), (0, 255, 0), 2)
        text = "Occupied"

    # draw the text and timestamp on the frame
    cv2.putText(frame_abs, "Room Status: {}".format(text), (10, 20),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    #*****************************************************************

    # show the frame and record if the user presses a key
    cv2.imshow("Average frame", frame)
    cv2.imshow("Absolute frame", frame_abs)
    # cv2.imshow("Thresh", thresh)
    # cv2.imshow("Thresh", thresh_abs)
    # cv2.imshow("Frame Delta", frameDelta)
    # cv2.imshow("Frame Delta", frameDelta_abs)
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key is pressed, break from the lop
    if key == ord("q"):
        break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
