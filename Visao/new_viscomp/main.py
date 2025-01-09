#!/usr/bin/env python3

import time
import cv2 as cv
import numpy as np
from src.viscomp import VisComp
from src.video import Video

# Video constructor arguments
CAMERA_ID = '../testes/new/output.avi'
CAP_WIDTH = 800
CAP_HEIGHT = 600
CAP_FPS = 30
WAITKEY_DELAY = 40  # ms


def main():
    video = Video(CAMERA_ID, CAP_WIDTH, CAP_HEIGHT, CAP_FPS)

    window_name = "frame"
    cv.namedWindow(window_name)

    video.update_frame()

    viscomp = VisComp(video.frame, WAITKEY_DELAY)

    while True:
        begin = time.time()

        video.update_frame()
        poses = viscomp.find_poses(video.frame, video.frame_hsv)
        print(f"poses = {poses}")

        key = video.show_frame()

        if key == ord('q'):
            break

        end = time.time()
        elapsed_time = end - begin
        print(f'tempo da iteração: {elapsed_time:.6f} seg')

    cv.destroyWindow(window_name)


if __name__ == '__main__':
    main()
