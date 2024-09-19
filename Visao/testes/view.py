import cv2 as cv

cap = cv.VideoCapture('output.avi')

while(True):
    _,frame = cap.read()
    cv.imshow('', frame)
    cv.waitKey(int(1000/30))