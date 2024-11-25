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


def create_objects(frame_enhanced):
    cte = calibrate(XY_POINTS, frame_enhanced, WAITKEY_DELAY)

    orange = Color('laranja', min_area=5, hs_tolerance=(5, 75))
    if orange.is_hsv_empty():
        orange.select(frame_enhanced, WAITKEY_DELAY)

    green = Color('verde', min_area=10)
    if green.is_hsv_empty():
        green.select(frame_enhanced, WAITKEY_DELAY)

    blue = Color('azul', min_area=10)
    if blue.is_hsv_empty():
        blue.select(frame_enhanced, WAITKEY_DELAY)

    pink = Color('rosa', min_area=1, hs_tolerance=(10, 65))
    if pink.is_hsv_empty():
        pink.select(frame_enhanced, WAITKEY_DELAY)

    yellow = Color('amarelo', min_area=1, hs_tolerance=(5, 65))
    if yellow.is_hsv_empty():
        yellow.select(frame_enhanced, WAITKEY_DELAY)

    robot_aa = Robot('AA', blue, yellow, cte)
    robot_ar = Robot('AR', blue, pink, cte)
    robot_va = Robot('VA', green, yellow, cte)
    robot_vr = Robot('VR', green, pink, cte)
    ball = Ball(orange, cte)

    return robot_aa, robot_ar, robot_va, robot_vr, ball


def viscomp(robot_aa, robot_ar, robot_va, robot_vr, ball, frame, frame_hsv):
        poses = []

        poses.append(robot_aa.find_pose(frame, frame_hsv))
        poses.append(robot_ar.find_pose(frame, frame_hsv))
        poses.append(robot_va.find_pose(frame, frame_hsv))
        poses.append(robot_vr.find_pose(frame, frame_hsv))
        poses.append(ball.find_pose(frame, frame_hsv))

        return poses


def main():
    video = Video(CAMERA_ID, CAP_WIDTH, CAP_HEIGHT, CAP_FPS)

    window_name = "frame"
    cv.namedWindow(window_name)

    video.update_frame()

    robot_aa, robot_ar, robot_va, robot_vr, ball = create_objects(video.frame_enhanced)

    while True:
        # begin = time.time()

        video.update_frame()
        poses = viscomp(robot_aa, robot_ar, robot_va, robot_vr, ball, video.frame, video.frame_hsv)
        print(f"poses = {poses}")

        key = video.show_frame()

        if key == ord('q'):
            break

        # end = time.time()
        # elapsed_time = end - begin
        # print(f'tempo da iteração: {elapsed_time:.6f} seg')


if __name__ == '__main__':
    main()
