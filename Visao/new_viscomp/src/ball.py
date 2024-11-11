import cv2 as cv
from src.color import Color
from src.calibration import uv_to_xy

class Ball:
    def __init__(self, color, cte):
        self.color = color
        self.pose = {'x': None, 'y': None}
        self.cte = cte

    def find_pose(self, frame, frame_hsv):
        self.color.find_centroid(frame_hsv)

        if self.color.uv is None:
            print('Ball not found')
            return

        rx, ry = uv_to_xy(self.color.uv, self.cte)

        cv.circle(frame, self.color.uv, 3, (255, 0, 0), -1)
        # text = f"ball (u,v) = {self.color.uv}"
        text = f"ball (x,y) = {rx},{ry}"
        cv.putText(frame, text, self.color.uv, cv.FONT_HERSHEY_PLAIN, 1, (255, 255, 0), 1)
