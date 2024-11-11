#!/usr/bin/env python3

import cv2 as cv
# import numpy as np
from src.video import Video
from src.color import Color
from src.calibration import calibrate
from src.robot import Robot
from src.ball import Ball

# Video constructor arguments
CAMERA_ID = '../testes/new/output.avi'
CAP_WIDTH = 800
CAP_HEIGHT = 600
CAP_FPS = 30
WAITKEY_DELAY = 40  # ms

# Calibration constructor arguments
XY_POINTS = [(0, 0), (-1190, 800), (1190, 800), (1190, -800), (-1190, -800)]


def main():
    video = Video(CAMERA_ID, CAP_WIDTH, CAP_HEIGHT, CAP_FPS)

    window_name = "frame"
    cv.namedWindow(window_name)

    video.update_frame()

    cte = calibrate(XY_POINTS, video.frame_enhanced, WAITKEY_DELAY)

    orange = Color('laranja', min_area=50, hs_tolerance=(5, 75))
    orange.select(video.frame_enhanced, WAITKEY_DELAY)

    # green = Color('verde')
    # green.select(video.frame_enhanced, WAITKEY_DELAY)

    # pink = Color('rosa', min_area=5)
    # pink.select(video.frame_enhanced, WAITKEY_DELAY)

    # robot = Robot('A', green, pink, cte)
    ball = Ball(orange, cte)

    while True:
        video.update_frame()

        # robot.find_pose(video.frame, video.frame_hsv)
        ball.find_pose(video.frame, video.frame_hsv)

        key = video.show_frame()

        if key == ord('q'):
            break


if __name__ == '__main__':
    main()
