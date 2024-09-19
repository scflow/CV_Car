import cv2
import numpy as np


data = np.load('./undistort/camera_calibration.npz')
mtx = data['mtx']
dist = data['dist']

def undistort(img):
    dst = cv2.undistort(img, mtx, dist, None, mtx)
    return dst
