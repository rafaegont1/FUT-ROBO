#!/usr/bin/env python3

import time
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
    if orange.is_hsv_empty():
        orange.select(video.frame_enhanced, WAITKEY_DELAY)

    green = Color('verde')
    if green.is_hsv_empty():
        green.select(video.frame_enhanced, WAITKEY_DELAY)

    blue = Color('azul')
    if blue.is_hsv_empty():
        blue.select(video.frame_enhanced, WAITKEY_DELAY)

    pink = Color('rosa', min_area=5)
    if pink.is_hsv_empty():
        pink.select(video.frame_enhanced, WAITKEY_DELAY)

    yellow = Color('amarelo', min_area=5)
    if yellow.is_hsv_empty():
        yellow.select(video.frame_enhanced, WAITKEY_DELAY)

    robot_a1 = Robot('A1', green, pink, cte)
    robot_a2 = Robot('A2', green, yellow, cte)
    robot_b1 = Robot('B1', blue, pink, cte)
    robot_b2 = Robot('B2', blue, yellow, cte)
    ball = Ball(orange, cte)

    while True:
        begin = time.time()

        video.update_frame()

        robot_a1.find_pose(video.frame, video.frame_hsv)
        robot_a2.find_pose(video.frame, video.frame_hsv)
        robot_b1.find_pose(video.frame, video.frame_hsv)
        robot_b2.find_pose(video.frame, video.frame_hsv)
        ball.find_pose(video.frame, video.frame_hsv)

        key = video.show_frame()

        if key == ord('q'):
            break

        end = time.time()
        elapsed_time = end - begin
        print(f'tempo da iteração: {elapsed_time:.6f} seg')


if __name__ == '__main__':
    main()
