# USAGE
# python track.py --video video/sample.mov

# import the necessary packages
import numpy as np
import argparse
import cv2
import time

# initialize the current frame of the video, along with the list of
# ROI points along with whether or not this is input mode
frame = None
roiPts = []
inputMode = False

def selectROI(event, x, y, flags, param):
	# grab the reference to the current frame, list of ROI
	# points and whether or not it is ROI selection mode
	global frame, roiPts, inputMode

	# if we are in ROI selection mode, the mouse was clicked,
	# and we do not already have four points, then update the
	# list of ROI points with the (x, y) location of the click
	# and draw the circle
	if inputMode and event == cv2.EVENT_LBUTTONDOWN and len(roiPts) < 4:
		roiPts.append((x, y))
		cv2.circle(frame, (x, y), 4, (0, 255, 0), 2)
		cv2.imshow("frame", frame)

def main():
	# construct the argument parse and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-v", "--video",
		help = "path to the (optional) video file")
	args = vars(ap.parse_args())

	# grab the reference to the current frame, list of ROI
	# points and whether or not it is ROI selection mode
	global frame, roiPts, inputMode

	# if the video path was not supplied, grab the reference to the
	# camera
	if not args.get("video", False):
		camera = cv2.VideoCapture(0)

	# otherwise, load the video
	else:
		camera = cv2.VideoCapture(args["video"])

	# setup the mouse callback
	cv2.namedWindow("frame")
	cv2.setMouseCallback("frame", selectROI)

	# initialize the termination criteria for cam shift, indicating
	# a maximum of ten iterations or movement by a least one pixel
	# along with the bounding box of the ROI
	termination = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)
	roiBox = None

	flag = True
	count = 0
	f1 = False
	f2 = False
	In = False
	Out = False
	pop = 0
	stepi = 0
	stepo = 0
	# keep looping over the frames
	while True:
		# grab the current frame
		(grabbed, frame) = camera.read()
		if flag:
			p_frame = frame
			diff = p_frame.mean(axis=2) - frame.mean(axis=2)
			flag = False

		if True:
			diff = p_frame.mean(axis=2) - frame.mean(axis=2)
			diff = (diff > 70.) * 1.

			sm1 = 0
			sm1 += diff[:5,:].sum()
			sm1 += diff[-5:,:].sum()
			sm1 += diff[:,:5].sum()
			sm1 += diff[:,-5:].sum()
			f1 = sm1>10
			sm2 = 0
			sm2 += diff[5:10,5:-5].sum()
			sm2 += diff[-10:-5,5:-5].sum()
			sm2 += diff[5:-5,5:10].sum()
			sm2 += diff[5:-5,-10:-5].sum()
			f2 = sm2>10

			if (not f1) and (not f2) and (stepi==0):
				In,Out,stepi = False,False,1
			if f1 and (not f2) and (stepi==1):
				In,Out,stepi = True,False,2
			if f1 and f2 and (stepi==2):
				In,Out,stepi = True,False,3
			if (not f1) and f2 and (stepi==3):
				In,Out,stepi = True,False,4
			if (not f1) and (not f2) and (stepi==4):
				In,Out,stepi = False,False,5
				pop+=1
				print '************** RAT IN **************'
				stepi = 0

			# if (not f1) and (not f2) and (stepo==0):
			# 	In,Out,stepo = False,False,1
			# if f1 and (not f2) and (stepo==1):
			# 	In,Out,stepo = True,False,2
			# if f1 and f2 and (stepo==2):
			# 	In,Out,stepo = True,False,3
			# if (not f1) and f2 and (stepo==3):
			# 	In,Out,stepo = True,False,4
			# if (not f1) and (not f2) and (stepo==4):
			# 	In,Out,stepo = False,False,5
			# 	pop+=1
			# 	print '************** RAT IN **************'
			# 	stepo = 0




		# check to see if we have reached the end of the
		# video
		if not grabbed:
			break

		# if the see if the ROI has been computed
		if roiBox is not None:
			# convert the current frame to the HSV color space
			# and perform mean shift
			hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
			backProj = cv2.calcBackProject([hsv], [0], roiHist, [0, 180], 1)

			# apply cam shift to the back projection, convert the
			# points to a bounding box, and then draw them
			(r, roiBox) = cv2.CamShift(backProj, roiBox, termination)
			pts = np.int0(cv2.cv.BoxPoints(r))
			cv2.polylines(frame, [pts], True, (0, 255, 0), 2)

		# show the frame and record if the user presses a key
		cv2.imshow("frame", diff)
		key = cv2.waitKey(1) & 0xFF

		# handle if the 'i' key is pressed, then go into ROI
		# selection mode
		if key == ord("i") and len(roiPts) < 4:
			# indicate that we are in input mode and clone the
			# frame
			inputMode = True
			orig = frame.copy()

			# keep looping until 4 reference ROI points have
			# been selected; press any key to exit ROI selction
			# mode once 4 points have been selected
			while len(roiPts) < 4:
				cv2.imshow("frame", frame)
				cv2.waitKey(0)

			# determine the top-left and bottom-right points
			roiPts = np.array(roiPts)
			s = roiPts.sum(axis = 1)
			tl = roiPts[np.argmin(s)]
			br = roiPts[np.argmax(s)]

			# grab the ROI for the bounding box and convert it
			# to the HSV color space
			roi = orig[tl[1]:br[1], tl[0]:br[0]]
			roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
			#roi = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB)

			# compute a HSV histogram for the ROI and store the
			# bounding box
			roiHist = cv2.calcHist([roi], [0], None, [16], [0, 180])
			roiHist = cv2.normalize(roiHist, roiHist, 0, 255, cv2.NORM_MINMAX)
			roiBox = (tl[0], tl[1], br[0], br[1])

		# if the 'q' key is pressed, stop the loop
		elif key == ord("q"):
			break

		p_frame = frame

	# cleanup the camera and close any open windows
	camera.release()
	cv2.destroyAllWindows()

if __name__ == "__main__":
	main()