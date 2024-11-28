#!/usr/bin/env python3

import time
import cv2 as cv
import numpy as np
from src.viscomp import VisComp
from src.video import Video

# Video constructor arguments
CAMERA_ID = 1
CAP_WIDTH = 1280
CAP_HEIGHT = 720
CAP_FPS = 15
WAITKEY_DELAY = 40  # ms


video = Video(CAMERA_ID, CAP_WIDTH, CAP_HEIGHT, CAP_FPS)

window_name = "frame"
cv.namedWindow(window_name)

video.update_frame()

viscomp = VisComp(video.frame_enhanced, WAITKEY_DELAY)