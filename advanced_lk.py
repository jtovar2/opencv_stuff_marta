#!/usr/bin/env python

'''
Lucas-Kanade tracker
====================

Lucas-Kanade sparse optical flow demo. Uses goodFeaturesToTrack
for track initialization and back-tracking for match verification
between frames.

Usage
-----
lk_track.py [<video_source>]


Keys
----
ESC - exit
'''

# Python 2/3 compatibility
from __future__ import print_function

import numpy as np
import cv2
from time import clock, sleep
from common import anorm2, draw_str
from picamera.array import PiRGBArray
from picamera import PiCamera

lk_params = dict( winSize  = (15, 15),maxLevel = 2, criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

feature_params = dict( maxCorners = 500,qualityLevel = 0.3,minDistance = 7,blockSize = 7 )

class App:
	def __init__(self):
		self.track_len = 10
		self.detect_interval = 5
		self.tracks = []
		self.frame_idx = 0

	def run(self):
		#Camera Setup 
		camera = PiCamera()
		camera.resolution = (640,480)
		camera.framerate = 32
		rawCapture = PiRGBArray(camera, size=(640,480))
		#Warm up time
		sleep(0.1)

		while True:
			#Get picture
			camera.capture(rawCapture, format='bgr')
			frame = rawCapture.array
			frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			vis = frame.copy()

			if len(self.tracks) > 0:
				img0, img1 = self.prev_gray, frame_gray
				p0 = np.float32([tr[-1] for tr in self.tracks]).reshape(-1, 1, 2)
				p1, st, err = cv2.calcOpticalFlowPyrLK(img0, img1, p0, None, **lk_params)
				p0r, st, err = cv2.calcOpticalFlowPyrLK(img1, img0, p1, None, **lk_params)
				d = abs(p0-p0r).reshape(-1, 2).max(-1)
				good = d < 1
				new_tracks = []
				
				for tr, (x, y), good_flag in zip(self.tracks, p1.reshape(-1, 2), good):
					if not good_flag:
						continue
					tr.append((x, y))
					if len(tr) > self.track_len:
						del tr[0]
					new_tracks.append(tr)
					cv2.circle(vis, (x, y), 2, (0, 255, 0), -1)
				
				self.tracks = new_tracks
				cv2.polylines(vis, [np.int32(tr) for tr in self.tracks], False, (0, 255, 0))
				draw_str(vis, (20, 20), 'track count: %d' % len(self.tracks))

			if self.frame_idx % self.detect_interval == 0:
				mask = np.zeros_like(frame_gray)
				mask[:] = 255
				for x, y in [np.int32(tr[-1]) for tr in self.tracks]:
					cv2.circle(mask, (x, y), 5, 0, -1)
				p = cv2.goodFeaturesToTrack(frame_gray, mask = mask, **feature_params)
				if p is not None:
					for x, y in np.float32(p).reshape(-1, 2):
						self.tracks.append([(x, y)])


			self.frame_idx += 1
			self.prev_gray = frame_gray
			cv2.imshow('lk_track', vis)
			rawCapture.truncate(0)

			ch = cv2.waitKey(1)
			if ch == 27:
				break

def main():
	import sys
	print(__doc__)

	App().run()
	cv2.destroyAllWindows()

if __name__ == '__main__':
	main()
		
