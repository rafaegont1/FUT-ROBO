#Importando as bibliotecas:
import cv2 as cv
import numpy as np

#Função para printar os pontos clicados:
def callback(event, x, y, flags, param):
    if event == cv.EVENT_LBUTTONDOWN:
        imagem = cv.cvtColor(param, cv.COLOR_BGR2HSV)
        hsv = imagem[y,x]
        print(f'\t Pixel: ({x}, {y}) \t HSV: ({hsv[0]}, {hsv[1]}, {hsv[2]}) \t')

#Abertura das imagens:       
frame1 = cv.imread('frame1.png')
frame2 = cv.imread('frame2.png')
frame3 = cv.imread('frame3.png')
frame4 = cv.imread('frame4.png')

#Concatenando as quatro imagens em uma só:
#frame = np.vstack([np.hstack([frame1, frame2]), np.hstack([frame3, frame4])])
frame = frame1

# #Redimentsionando o frame:
# frame = cv.resize(frame, (0,0), fx=0.6, fy=0.6)

# #Mostrando a imagem:
# cv.imshow('Imagem original', frame)
# cv.waitKey()

# #Equalização de histograma na imagem:
# h,s,v = cv.split(cv.cvtColor(frame, cv.COLOR_BGR2HSV))
# veq = cv.equalizeHist(v)
# hsveq = cv.merge([h,s,veq])
# frame = cv.cvtColor(hsveq, cv.COLOR_HSV2BGR)

#Mostrando a imagem:
cv.imshow('Imagem Equalizada', frame)
cv.setMouseCallback('Imagem Equalizada', callback, param=frame)
cv.waitKey()