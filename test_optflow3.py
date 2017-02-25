import numpy as np
import cv2
import math
import random
cap = cv2.VideoCapture('simul.MOV')
# params for ShiTomasi corner detection
feature_params = dict( maxCorners = 40,
                       qualityLevel = 0.1,
                       minDistance = 200,
                       blockSize = 30 )
# Parameters for lucas kanade optical flow
lk_params = dict( winSize  = (30,30),
                  maxLevel = 3,
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
count_things_exited_on_right = 0
count_things_exited_on_top = 0
count_things_exited_on_bottom = 0

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
    #p0 = np.concatenate((p0,new_pts), axis=0)
    print "Points being Tracked"
    print p0
    p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)
    # Select good points
    good_new = p1[st==1]
    good_old = p0[st==1]
    # draw the tracks
    count = 0
    total_distance = 0
    points_to_remove_list = list()
    if good_old.shape[0] != 0:
        for i,(new,old) in enumerate(zip(good_new,good_old)):
            a,b = new.ravel()
            c,d = old.ravel()
            count = count + 1
            distance = math.sqrt( (a-c)*(a-c) + (b-d)*(b-d))
            total_distance = distance + total_distance

            if avg_distance != 0 and distance < avg_distance*0.1:
                points_to_remove_list.append(i)
            mask = cv2.line(mask, (a,b),(c,d), color[i].tolist(), 2)
            frame = cv2.circle(frame,(a,b),5,color[i].tolist(),-1)

    frame = cv2.circle(frame, (int(width),0), 10, color[0].tolist(), -1)
    frame = cv2.circle(frame, (int(width), int(height)), 10, color[0].tolist(), -1)
    frame = cv2.circle(frame, (0, int(height)), 10, color[0].tolist(), -1)
    frame = cv2.circle(frame, (0,0), 10, color[0].tolist(), -1)
    avg_distance = total_distance/count
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
        if (width - x) < 10:
            print "exit on the right"
            count_things_exited_on_right =+ 1
        elif x< 10:
            print "exit on the left"
            count_things_exited_on_left =+ 1

        elif (height - y) < 10:
            print "exit on top"
            count_things_exited_on_top =+ 1
        elif y < 10:
            print "exit on bottom"
            count_things_exited_on_bottom =+ 1
        print "we on point"

    if len(points_to_remove_list) > 0:
        good_new = np.delete(arr=good_new, obj=points_to_remove_list, axis=0)
        rand_indexes_to_add = [random.uniform(0,new_pts.shape[0]) for _ in xrange(len(
            points_to_remove_list))]
        for index in rand_indexes_to_add:
            column_to_add = new_pts[int(index),0].reshape(1,2)
            good_new = np.concatenate((column_to_add, good_new), axis = 0)
    print "wayymeent"
    print "wayyment"
    p0 = good_new.reshape(-1,1,2)
cv2.destroyAllWindows()
cap.release()
