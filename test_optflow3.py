import numpy as np
import cv2
import math
import random
import
cap = cv2.VideoCapture('simul.MOV')
# params for ShiTomasi corner detection
feature_params = dict( maxCorners = 500,
                       qualityLevel = 0.01,
                       minDistance = 80,
                       blockSize = 10 )
# Parameters for lucas kanade optical flow
lk_params = dict( winSize  = (30,30),
                  maxLevel = 2,
                  criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
# Create some random colors
color = np.random.randint(0,255,(100,3))
# Take first frame and find corners in it
ret, old_frame = cap.read()
old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
p0 = cv2.goodFeaturesToTrack(old_gray, mask = None, **feature_params)
print p0
# Create a mask image for drawing purposes
mask = np.zeros_like(old_frame)

count_things_exited_on_left = 0
last_exit_on_right = 0
count_things_exited_on_right = 0
last_exit_on_left = 0
count_things_exited_on_top = 0
last_exit_on_top = 0
count_things_exited_on_bottom = 0
last_exit_on_bottom = 0

avg_distance = 0

while(1):
    ret,frame = cap.read()
    width = cap.get(3)
    height = cap.get(4)
    print "width is " + str(width)
    print "height is " + str(height)
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    new_pts = cv2.goodFeaturesToTrack(frame_gray, mask=None, **feature_params)
    # calculate optical flow
    tuple_new_pts = new_pts.shape
    tuple_p0 = p0.shape
    #print st
    print "Points being Tracked"
    print p0
    p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)
    # Select good points
    good_new = p1[st==1]
    good_old = p0[st==1]
    points_to_remove = []
    points_to_keep = []
    # draw the tracks
    if good_old.shape[0] != 0:
        for i,(new,old) in enumerate(zip(good_new,good_old)):
            a,b = new.ravel()
            c,d = old.ravel()
            if int(a) == int(c) and int(b) == int(d):
                points_to_remove.append(i)
            else:
                points_to_keep.append(i)
                mask = cv2.line(mask, (a,b),(c,d), color[i].tolist(), 2)
                frame = cv2.circle(frame,(a,b),5,color[i].tolist(),-1)




        '''if len(points_to_remove) > .7*good_new.shape[0]:
            print "no new points no no"

            p0 = cv2.goodFeaturesToTrack(frame_gray, mask = None, **feature_params)
            cv2.imshow('frame', frame)
            print "looking for new points"
            continue
        else:'''


        frame = cv2.circle(frame, (int(width),0), 10, color[0].tolist(), -1)
        frame = cv2.circle(frame, (int(width), int(height)), 10, color[0].tolist(), -1)
        frame = cv2.circle(frame, (0, int(height)), 10, color[0].tolist(), -1)
        frame = cv2.circle(frame, (0,0), 10, color[0].tolist(), -1)
        img = cv2.add(frame,mask)
        cv2.imshow('frame',img)
        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break
        # Now update the previous frame and previous points
        old_gray = frame_gray.copy()
        for point in new_pts:
            x = point[0][0]
            y = point[0][1]
            if (width - x) == 1:
                count_things_exited_on_right += 1
                print "exit on the right " + str(count_things_exited_on_right)
            elif x ==  1:
                count_things_exited_on_left += 1
                print "exit on the left " + str(count_things_exited_on_left)
            if (height - y) == 1:
                count_things_exited_on_top += 1
                print "exit on the top " + str(count_things_exited_on_top)
            elif y == 1:
                count_things_exited_on_bottom += 1
                print "exit on the bottom " + str(count_things_exited_on_bottom)
            print "we on point"

        print "wayymeent"
        print "wayyment"
        good_new = np.delete(good_new, points_to_remove, axis=0)
    else:
        cv2.imshow('frame', frame)

    if good_new.shape[0] == 0:
         p0 = cv2.goodFeaturesToTrack(frame_gray, mask = None, **feature_params)

    else:
        p0 = good_new.reshape(-1,1,2)

cv2.destroyAllWindows()
cap.release()
