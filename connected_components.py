#!/usr/bin/env python
"""
setup of connected components with OpenCV (also possible with scikit-image)
"""
import cv2


def main():

    B = setupblob(params)

    for i, img in enumerate(imgs):
        motion = process(img)
        keypoints = B.detect(motion)


def setupblob(param: dict):
    """
    setup connected components "blob detection"
    """
    B = cv2.SimpleBlobDetector_Params()
    B.filterByArea = True
    B.filterByColor = False
    B.filterByCircularity = False
    B.filterByInertia = False
    B.filterByConvexity = False

    B.minDistBetweenBlobs = param['mindist']
    B.minArea = param['minarea']
    B.maxArea = param['maxarea']

    return cv2.SimpleBlobDetector_create(B)
