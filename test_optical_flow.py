import numpy as np
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import time

#cap = cv2.VideoCapture('slow.flv')
#Setup camera
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640,480))

time.sleep(0.1)

# params for ShiTomasi corner detection
feature_params = dict( maxCorners = 100,
                       qualityLevel = 0.3,
                       minDistance = 7,
                       blockSize = 7 )
# Parameters for lucas kanade optical flow
lk_params = dict( winSize  = (15,15),
                  maxLevel = 2,
                  criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
# Create some random colors
color = np.random.randint(0,255,(100,3))
# Take first frame and find corners in it
camera.capture(rawCapture, format='bgr')
old_frame = rawCapture.array
old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
p0 = cv2.goodFeaturesToTrack(old_gray, mask = None, **feature_params)
# Create a mask image for drawing purposes
mask = np.zeros_like(old_frame)
rawCapture.truncate(0)
for frame in camera.capture_continuous(rawCapture, format='bgr',
use_video_port = True):
    #ret,frame = cap.read()
    image = frame.array
    frame_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # calculate optical flow
    p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)
    # Select good points
    print p1
    print "this was the old points"
    print '**********************************************'
    good_new = p1[st==1]
    good_old = p0[st==1]
    print good_new
    print "this was the new points"
    print '******************************************'
    # draw the tracks
    for i,(new,old) in enumerate(zip(good_new,good_old)):
        a,b = new.ravel()
        c,d = old.ravel()
        mask = cv2.line(mask, (a,b),(c,d), color[i].tolist(), 2)
        frame = cv2.circle(image,(a,b),5,color[i].tolist(),-1)
    img = cv2.add(image,mask)
    cv2.imshow('frame',img)
    k = cv2.waitKey(1) & 0xFF
    rawCapture.truncate(0)
    if k == ord("q"):
        break
    # Now update the previous frame and previous points
    old_gray = frame_gray.copy()
    p0 = good_new.reshape(-1,1,2)
cv2.destroyAll
