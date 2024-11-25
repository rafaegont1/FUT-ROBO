import cv2 as cv
from src.robot import Robot
from src.ball import Ball
from src.calibration import calibrate
from src.color import Color

# Calibration constructor arguments
XY_POINTS = [(0, 0), (-1190, 800), (1190, 800), (1190, -800), (-1190, -800)]


class VisComp:
    def __init__(self, frame_enhanced, waitKey_delay):
        cte = calibrate(XY_POINTS, frame_enhanced, waitKey_delay)

        orange = Color('laranja', min_area=5, hs_tolerance=(5, 75))
        if orange.is_hsv_empty():
            orange.select(frame_enhanced, waitKey_delay)

        green = Color('verde', min_area=10)
        if green.is_hsv_empty():
            green.select(frame_enhanced, waitKey_delay)

        blue = Color('azul', min_area=10)
        if blue.is_hsv_empty():
            blue.select(frame_enhanced, waitKey_delay)

        pink = Color('rosa', min_area=1, hs_tolerance=(10, 65))
        if pink.is_hsv_empty():
            pink.select(frame_enhanced, waitKey_delay)

        yellow = Color('amarelo', min_area=1, hs_tolerance=(5, 65))
        if yellow.is_hsv_empty():
            yellow.select(frame_enhanced, waitKey_delay)

        self.robot_aa = Robot('AA', blue, yellow, cte)
        self.robot_ar = Robot('AR', blue, pink, cte)
        self.robot_va = Robot('VA', green, yellow, cte)
        self.robot_vr = Robot('VR', green, pink, cte)
        self.ball = Ball(orange, cte)

    def find_poses(self, frame, frame_hsv):
        poses = []

        poses.append(self.robot_aa.find_pose(frame, frame_hsv))
        poses.append(self.robot_ar.find_pose(frame, frame_hsv))
        poses.append(self.robot_va.find_pose(frame, frame_hsv))
        poses.append(self.robot_vr.find_pose(frame, frame_hsv))
        poses.append(self.ball.find_pose(frame, frame_hsv))

        return poses
