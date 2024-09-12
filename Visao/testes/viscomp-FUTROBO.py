import cv2
import numpy as np
import time
#import requests
#import simplejson
#import math
#import paho.mqtt.client as mqtt

def coef_calc(uv_points, xy_points):
    #Montando a matriz A:
    uvarray = np.array(uv_points)
    uvec = uvarray[:,0][:, np.newaxis]
    vvec = uvarray[:,1][:, np.newaxis]
    A = np.block([np.ones((len(uv_points),1)), uvarray, (uvec**2), (vvec**2)])

    #Montando as matrizes B:
    Bx = np.array(xy_points)[:,0][:, np.newaxis]
    By = np.array(xy_points)[:,1][:, np.newaxis]

    #Calculando a pseudo-inversa:
    A_ = np.linalg.inv(A.T@A)@A.T

    #Calculando os coeficientes:
    alpha = (A_@Bx).T
    beta = (A_@By).T

    return alpha[0], beta[0]

def uv_to_xy(uv, consts):
    coefs = np.vstack([consts[0], consts[1]])
    imag = np.hstack((np.ones(1), np.array(uv), np.array(uv[0]**2), np.array(uv[1]**2)))[:, np.newaxis]
    out = (coefs@imag).T
    return np.array(out[0].round(0), dtype=np.int_).tolist()

#Xr offset (distância entre o centro do landmark, até o eixo de rotação do robô), em mm:
xoff = 100
# Vetor de Pontos na Imagem 
global points
points = []
#Constantes para transformação de coordenada:
global cte
#Pontos reais conhecidos no campo:
xy = [[0,0], [-1190,800], [1190,800], [1190,-800], [-1190,-800]]

# Variáveis globais para armazenar os limites da cor laranja
lower_orange = None
upper_orange = None
clicked_color1 = None

# Variáveis globais para armazenar os limites da cor Azul
lower_blue = None
upper_blue = None
clicked_color2 = None

#Variáveis globais para armazenar os limites da cor Verde
lower_green = None
upper_green = None
clicked_color3 = None

# Variáveis globais para armazenar os limites da cor Rosa
lower_pink = None
upper_pink = None
clicked_color4 = None

# Variáveis globais para armazenar os limites da cor Amarela

lower_yellow = None
upper_yellow = None
clicked_color5 = None

######################## Seleção dos Pontos no Campo ##########################

def click_points(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append([x, y])

        #print(f'\n({x}, {y})')

        # Fecha a janela de seleção de cor
        cv2.destroyWindow("Clique no ponto desejado para calibracao")

def select_points():
    cap = cv2.VideoCapture(5)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)  # Largura em pixels
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)  # Altura em pixels
    cap.set(cv2.CAP_PROP_AUDIO_SAMPLES_PER_SECOND, 30)  # Taxa de atualização

    if not cap.isOpened():
        print("Não foi possível abrir a câmera.")
        return False

    cv2.namedWindow("Clique no ponto desejado para calibracao")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Clique no ponto desejado para calibracao", frame)
        cv2.setMouseCallback("Clique no ponto desejado para calibracao", click_points, param=frame)

        # Se o usuário definiu a cor clicando, saia do loop
        if (len(points) == 5):
            print(points)
            break

        cv2.waitKey(0)

    cap.release()
    cv2.destroyAllWindows()
    global cte 
    cte = coef_calc(points, xy)

    return True


######################## Identificação Cor Amarela ##########################

def click_event1(event, x, y, flags, param):
    global lower_yellow, upper_yellow, clicked_color5

    if event == cv2.EVENT_LBUTTONDOWN:
        # 'param' é a imagem passada quando a função de callback é chamada
        image = param
        clicked_color5 = image[y, x]
        # Converte a cor clicada de BGR para HSV
        hsv_color = cv2.cvtColor(np.uint8([[clicked_color5]]), cv2.COLOR_BGR2HSV)[0][0]

        # Define os limites com uma tolerância ao redor da cor clicada
        tolerance = 20
        lower_yellow = np.array([(hsv_color[0] - tolerance), (hsv_color[1] - tolerance), (hsv_color[2] - tolerance)])
        upper_yellow = np.array([(hsv_color[0] + tolerance), (hsv_color[1] + tolerance), (hsv_color[2] + tolerance)])

        print(f"Limites definidos: lower_yellow={lower_yellow}, upper_yellow={upper_yellow}")

        # Fecha a janela de seleção de cor
        cv2.destroyWindow("Clique na cor desejada para 'amarelo'")

def select_yellow_color():
    
    cap = cv2.VideoCapture(5)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)  # Largura em pixels
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)  # Altura em pixels
    cap.set(cv2.CAP_PROP_AUDIO_SAMPLES_PER_SECOND, 30)  # Taxa de atualização

    if not cap.isOpened():
        print("Não foi possível abrir a câmera.")
        return False

    cv2.namedWindow("Clique na cor desejada para 'amarelo'")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Clique na cor desejada para 'amarelo'", frame)
        cv2.setMouseCallback("Clique na cor desejada para 'amarelo'", click_event1, param=frame)

        # Se o usuário definiu a cor clicando, saia do loop
        if lower_yellow is not None and upper_yellow is not None:
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    original_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(original_hsv, lower_yellow, upper_yellow)
    res = cv2.bitwise_and(original_hsv, original_hsv, mask=mask)
    res = cv2.cvtColor(res, cv2.COLOR_HSV2BGR)
    cv2.imshow("Isolamento da cor selecionada", res)

    return lower_yellow is not None and upper_yellow is not None

##################################### Identificação Cor Rosa #######################################

def click_event2(event, x, y, flags, param):
    global lower_pink, upper_pink, clicked_color4

    if event == cv2.EVENT_LBUTTONDOWN:
        # 'param' é a imagem passada quando a função de callback é chamada
        image = param
        clicked_color4 = image[y, x]
        # Converte a cor clicada de BGR para HSV
        hsv_color = cv2.cvtColor(np.uint8([[clicked_color4]]), cv2.COLOR_BGR2HSV)[0][0]

        # Define os limites com uma tolerância ao redor da cor clicada
        tolerance = 20
        lower_pink = np.array([(hsv_color[0] - tolerance), (hsv_color[1] - tolerance), (hsv_color[2] - tolerance)])
        upper_pink = np.array([(hsv_color[0] + tolerance), (hsv_color[1] + tolerance), (hsv_color[2] + tolerance)])

        print(f"Limites definidos: lower_pink={lower_pink}, upper_pink={upper_pink}")

        # Fecha a janela de seleção de cor
        cv2.destroyWindow("Clique na cor desejada para 'rosa'")

def select_pink_color():
    
    cap = cv2.VideoCapture(5)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)  # Largura em pixels
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)  # Altura em pixels
    cap.set(cv2.CAP_PROP_AUDIO_SAMPLES_PER_SECOND, 30)  # Taxa de atualização

    if not cap.isOpened():
        print("Não foi possível abrir a câmera.")
        return False

    cv2.namedWindow("Clique na cor desejada para 'rosa'")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Clique na cor desejada para 'rosa'", frame)
        cv2.setMouseCallback("Clique na cor desejada para 'rosa'", click_event2, param=frame)

        # Se o usuário definiu a cor clicando, saia do loop
        if lower_pink is not None and upper_pink is not None:
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    original_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(original_hsv, lower_pink, upper_pink)
    res = cv2.bitwise_and(original_hsv, original_hsv, mask=mask)
    res = cv2.cvtColor(res, cv2.COLOR_HSV2BGR)
    cv2.imshow("Isolamento da cor selecionada", res)

    return lower_pink is not None and upper_pink is not None

################################# Identificação cor verde #########################################

def click_event3(event, x, y, flags, param):
    global lower_green, upper_green, clicked_color3

    if event == cv2.EVENT_LBUTTONDOWN:
        # 'param' é a imagem passada quando a função de callback é chamada
        image = param
        clicked_color3 = image[y, x]
        # Converte a cor clicada de BGR para HSV
        hsv_color = cv2.cvtColor(np.uint8([[clicked_color3]]), cv2.COLOR_BGR2HSV)[0][0]

        # Define os limites com uma tolerância ao redor da cor clicada
        tolerance = 20
        lower_green = np.array([(hsv_color[0] - tolerance), (hsv_color[1] - tolerance), (hsv_color[2] - tolerance)])
        upper_green = np.array([(hsv_color[0] + tolerance), (hsv_color[1] + tolerance), (hsv_color[2] + tolerance)])

        print(f"Limites definidos: lower_green={lower_green}, upper_green={upper_green}")

        # Fecha a janela de seleção de cor
        cv2.destroyWindow("Clique na cor desejada para 'verde'")

def select_green_color():
    
    cap = cv2.VideoCapture(5)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)  # Largura em pixels
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)  # Altura em pixels
    cap.set(cv2.CAP_PROP_AUDIO_SAMPLES_PER_SECOND, 30)  # Taxa de atualização

    if not cap.isOpened():
        print("Não foi possível abrir a câmera.")
        return False

    cv2.namedWindow("Clique na cor desejada para 'verde'")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Clique na cor desejada para 'verde'", frame)
        cv2.setMouseCallback("Clique na cor desejada para 'verde'", click_event3, param=frame)

        # Se o usuário definiu a cor clicando, saia do loop
        if lower_green is not None and upper_green is not None:
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    original_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(original_hsv, lower_green, upper_green)
    res = cv2.bitwise_and(original_hsv, original_hsv, mask=mask)
    res = cv2.cvtColor(res, cv2.COLOR_HSV2BGR)
    cv2.imshow("Isolamento da cor selecionada", res)

    return lower_green is not None and upper_green is not None

########################### Identificação da Cor Azul ##################################

def click_event4(event, x, y, flags, param):
    global lower_blue, upper_blue, clicked_color2

    if event == cv2.EVENT_LBUTTONDOWN:
        # 'param' é a imagem passada quando a função de callback é chamada
        image = param
        clicked_color2 = image[y, x]
        # Converte a cor clicada de BGR para HSV
        hsv_color = cv2.cvtColor(np.uint8([[clicked_color2]]), cv2.COLOR_BGR2HSV)[0][0]

        # Define os limites com uma tolerância ao redor da cor clicada
        tolerance = 20
        lower_blue = np.array([(hsv_color[0] - tolerance), (hsv_color[1] - tolerance), (hsv_color[2] - tolerance)])
        upper_blue = np.array([(hsv_color[0] + tolerance), (hsv_color[1] + tolerance), (hsv_color[2] + tolerance)])

        print(f"Limites definidos: lower_blue={lower_blue}, upper_blue={upper_blue}")

        # Fecha a janela de seleção de cor
        cv2.destroyWindow("Clique na cor desejada para 'azul'")

def select_blue_color():
    
    cap = cv2.VideoCapture(5)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)  # Largura em pixels
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)  # Altura em pixels
    cap.set(cv2.CAP_PROP_AUDIO_SAMPLES_PER_SECOND, 30)  # Taxa de atualização

    if not cap.isOpened():
        print("Não foi possível abrir a câmera.")
        return False

    cv2.namedWindow("Clique na cor desejada para 'azul'")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Clique na cor desejada para 'azul'", frame)
        cv2.setMouseCallback("Clique na cor desejada para 'azul'", click_event4, param=frame)

        # Se o usuário definiu a cor clicando, saia do loop
        if lower_blue is not None and upper_blue is not None:
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    original_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(original_hsv, lower_blue, upper_blue)
    res = cv2.bitwise_and(original_hsv, original_hsv, mask=mask)
    res = cv2.cvtColor(res, cv2.COLOR_HSV2BGR)
    cv2.imshow("Isolamento da cor selecionada", res)

    return lower_blue is not None and upper_blue is not None

################################### Identificação da cor Laranja ###########################

def click_event(event, x, y, flags, param):
    global lower_orange, upper_orange, clicked_color1

    if event == cv2.EVENT_LBUTTONDOWN:
        # 'param' é a imagem passada quando a função de callback é chamada
        image = param
        clicked_color1 = image[y, x]
        # Converte a cor clicada de BGR para HSV
        hsv_color = cv2.cvtColor(np.uint8([[clicked_color1]]), cv2.COLOR_BGR2HSV)[0][0]

        # Define os limites com uma tolerância ao redor da cor clicada
        tolerance = 25
        lower_orange = np.array([(hsv_color[0] - tolerance), (hsv_color[1] - tolerance), (hsv_color[2] - tolerance)])
        upper_orange = np.array([(hsv_color[0] + tolerance), (hsv_color[1] + tolerance), (hsv_color[2] + tolerance)])

        print(f"Limites definidos: lower_orange={lower_orange}, upper_orange={upper_orange}")

        # Fecha a janela de seleção de cor
        cv2.destroyWindow("Clique na cor desejada para 'laranja'")

def select_orange_color():
    
    cap = cv2.VideoCapture(5)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)  # Largura em pixels
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)  # Altura em pixels
    cap.set(cv2.CAP_PROP_AUDIO_SAMPLES_PER_SECOND, 30)  # Taxa de atualização

    if not cap.isOpened():
        print("Não foi possível abrir a câmera.")
        return False

    cv2.namedWindow("Clique na cor desejada para 'laranja'")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Clique na cor desejada para 'laranja'", frame)
        cv2.setMouseCallback("Clique na cor desejada para 'laranja'", click_event, param=frame)

        # Se o usuário definiu a cor clicando, saia do loop
        if lower_orange is not None and upper_orange is not None:
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    original_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(original_hsv, lower_orange, upper_orange)
    res = cv2.bitwise_and(original_hsv, original_hsv, mask=mask)
    res = cv2.cvtColor(res, cv2.COLOR_HSV2BGR)
    cv2.imshow("Isolamento da cor selecionada", res)

    return lower_orange is not None and upper_orange is not None

########################################################################################################

def enhance_contrast(image):
    # Aumenta o contraste da imagem
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    enhanced_image = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    kernel_size = 5  # Tamanho do kernel para a suavização
    blurred_image = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
    return enhanced_image

def detect_colors_with_contours():
    cap = cv2.VideoCapture(5)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)  # Largura em pixels
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)  # Altura em pixels
    cap.set(cv2.CAP_PROP_AUDIO_SAMPLES_PER_SECOND, 30)  # Taxa de atualização

    if not cap.isOpened():
        print("Não foi possível abrir a câmera.")
        return

    
    display_interval = 0  # Intervalo de exibição em segundos
    last_display_time = 0
    while True:
        ret, frame = cap.read()
        print('\n\n---------------------------------------------------------------------------------------------------------\n\n')

        if ret:
            enhanced_frame = enhance_contrast(frame)
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Detecção de objetos azuis com círculo rosa ou amarelo

            # Mudar a cor principal do robô (Upper e Lower)
            #lower_blue = np.array([90, 100, 100])
            #upper_blue = np.array([130, 255, 255])
            if lower_blue is not None and upper_blue is not None:
                main_mask = cv2.inRange(hsv_frame, lower_blue, upper_blue)
                main_contours, _ = cv2.findContours(main_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                for contour in main_contours:
                    if cv2.contourArea(contour) > 100:
                        M = cv2.moments(contour)
                        if M["m00"] != 0:
                            cX = int(M["m10"] / M["m00"])
                            cY = int(M["m01"] / M["m00"])

                            # Detecção de círculo rosa ou amarelo dentro do objeto azul
                            roi = frame[max(0, cY - 15):min(frame.shape[0], cY + 15),
                                        max(0, cX - 15):min(frame.shape[1], cX + 15)]

                            if roi.size == 0:
                                continue

                            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

                            # Mudar o Upper e o Lower da cor do círculo (cor secundária 1)
                            #lower_pink = np.array([140, 50, 50])
                            #upper_pink = np.array([170, 255, 255])
                            secondary1_mask = cv2.inRange(hsv_roi, lower_pink, upper_pink)
                            secondary1_contours, _ = cv2.findContours(secondary1_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                            # Mudar o Upper e o Lower da cor do círculo (cor secundária 2)
                            #lower_yellow = np.array([20, 100, 100])
                            #upper_yellow = np.array([30, 255, 255])
                            secondary2_mask = cv2.inRange(hsv_roi, lower_yellow, upper_yellow)
                            secondary2_contours, _ = cv2.findContours(secondary2_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                            for secondary1_contour in secondary1_contours:
                                secondary1_moment = cv2.moments(secondary1_contour)
                                if secondary1_moment["m00"] != 0:
                                    secondary1_cX = int(secondary1_moment["m10"] / secondary1_moment["m00"])
                                    secondary1_cY = int(secondary1_moment["m01"] / secondary1_moment["m00"])

                                    secondary1_cX += max(0, cX - 15)
                                    secondary1_cY += max(0, cY - 15)

                                    # Objeto azul com círculo rosa
                                    #cv2.drawContours(frame, [contour], -1, (255, 0, 0), 2)
                                    #cv2.drawContours(frame, [secondary1_contour], -1, (0, 0, 255), 2)
                                    cv2.circle(frame, (cX, cY), 3, (0, 0, 255), -1)
                                    cv2.circle(frame, (secondary1_cX, secondary1_cY), 3, (0, 0, 255), -1)
                                    rx,ry = uv_to_xy((cX,cY), cte)
                                    theta = -np.degrees(np.arctan2((secondary1_cY-cY), (secondary1_cX-cX)))
                                    pose = [int(rx-(xoff*np.cos(np.radians(theta)))), int(ry+(xoff*np.sin(np.radians(theta)))), int(theta)]
                                    print(f'A-R: ({pose[0]}, {pose[1]}, {pose[2]})')
                                    # print(f"Objeto azul com círculo rosa: Objeto: ({cX}, {cY}), Círculo rosa: ({secondary1_cX}, {secondary1_cY})")

                                    # # Calculando a tangente do ângulo
                                    # x_inicio = cX
                                    # y_inicio = cY
                                    # x_fim = secondary1_cX
                                    # y_fim = secondary1_cY

                                    # # Calculando as diferenças entre as coordenadas para obter o vetor direção
                                    # delta_x = x_fim - x_inicio
                                    # delta_y = y_fim - y_inicio

                                    # # Calculando o ângulo em radianos usando a função atan2
                                    # angulo_radianos = math.atan2(delta_y, delta_x)

                                    # # Convertendo o ângulo para graus
                                    # angulo_graus = math.degrees(angulo_radianos)

                                    # # Calculando a tangente do ângulo
                                    # tangente_angulo = math.tan(angulo_radianos)

                                    # print(f"Ângulo do segmento de reta do robô azul com círculo rosa: {angulo_graus}")
                                    # print(f"A tangente desse ângulo é: {tangente_angulo}")

                            for secondary2_contour in secondary2_contours:
                                secondary2_moment = cv2.moments(secondary2_contour)
                                if secondary2_moment["m00"] != 0:
                                    secondary2_cX = int(secondary2_moment["m10"] / secondary2_moment["m00"])
                                    secondary2_cY = int(secondary2_moment["m01"] / secondary2_moment["m00"])

                                    secondary2_cX += max(0, cX - 15)
                                    secondary2_cY += max(0, cY - 15)

                                    # Objeto azul com círculo amarelo
                                    #cv2.drawContours(frame, [contour], -1, (255, 0, 0), 2)
                                    #cv2.drawContours(frame, [secondary2_contour], -1, (0, 255, 255), 2)
                                    cv2.circle(frame, (cX, cY), 3, (0, 0, 255), -1)
                                    cv2.circle(frame, (secondary2_cX, secondary2_cY), 3, (0, 0, 255), -1)
                                    rx,ry = uv_to_xy((cX,cY), cte)
                                    theta = -np.degrees(np.arctan2((secondary2_cY-cY), (secondary2_cX-cX)))
                                    pose = [int(rx-(xoff*np.cos(np.radians(theta)))), int(ry+(xoff*np.sin(np.radians(theta)))), int(theta)]
                                    print(f'A-A: ({pose[0]}, {pose[1]}, {pose[2]})')
                                    # print(f"Objeto azul com círculo amarelo: Objeto: ({cX}, {cY}), Círculo amarelo: ({secondary2_cX}, {secondary2_cY})")

                                    # # Calculando a tangente do ângulo
                                    # x_inicio = cX
                                    # y_inicio = cY
                                    # x_fim = secondary2_cX
                                    # y_fim = secondary2_cY

                                    # # Calculando as diferenças entre as coordenadas para obter o vetor direção
                                    # delta_x = x_fim - x_inicio
                                    # delta_y = y_fim - y_inicio

                                    # # Calculando o ângulo em radianos usando a função atan2
                                    # angulo_radianos = math.atan2(delta_y, delta_x)

                                    # # Convertendo o ângulo para graus
                                    # angulo_graus = math.degrees(angulo_radianos)

                                    # # Calculando a tangente do ângulo
                                    # tangente_angulo = math.tan(angulo_radianos)

                                    # print(f"Ângulo do segmento de reta do robô azul com círculo amarelo: {angulo_graus}")
                                    # print(f"A tangente desse ângulo é: {tangente_angulo}")
                            
            # Detecção de objetos verdes com círculo rosa ou amarelo

            # Mudar a cor principal do robô (Upper e Lower)
            #lower_green = np.array([30, 40, 20])
            #upper_green = np.array([90, 255, 255])
            
            if lower_green is not None and upper_green is not None:
                main2_mask = cv2.inRange(hsv_frame, lower_green, upper_green)
                main2_contours, _ = cv2.findContours(main2_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                for contour in main2_contours:
                    if cv2.contourArea(contour) > 100:
                        M = cv2.moments(contour)
                        if M["m00"] != 0:
                            cX = int(M["m10"] / M["m00"])
                            cY = int(M["m01"] / M["m00"])

                            # Detecção de círculo rosa ou amarelo dentro do objeto verde
                            roi = frame[max(0, cY - 15):min(enhanced_frame.shape[0], cY + 15),
                                        max(0, cX - 15):min(enhanced_frame.shape[1], cX + 15)]

                            if roi.size == 0:
                                continue

                            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

                            # Mudar o Upper e o Lower da cor do círculo (cor secundária 1)
                            #lower_pink = np.array([140, 50, 50])
                            #upper_pink = np.array([170, 255, 255])
                            secondary1_mask = cv2.inRange(hsv_roi, lower_pink, upper_pink)
                            secondary1_contours, _ = cv2.findContours(secondary1_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                            # Mudar o Upper e o Lower da cor do círculo (cor secundária 2)
                            #lower_yellow = np.array([20, 100, 100])
                            #upper_yellow = np.array([30, 255, 255])
                            secondary2_mask = cv2.inRange(hsv_roi, lower_yellow, upper_yellow)
                            secondary2_contours, _ = cv2.findContours(secondary2_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                            for secondary1_contour in secondary1_contours:
                                secondary1_moment = cv2.moments(secondary1_contour)
                                if secondary1_moment["m00"] != 0:
                                    secondary1_cX = int(secondary1_moment["m10"] / secondary1_moment["m00"])
                                    secondary1_cY = int(secondary1_moment["m01"] / secondary1_moment["m00"])

                                    # Coordenadas do centro do círculo em relação à imagem inteira
                                    secondary1_cX += max(0, cX - 15)
                                    secondary1_cY += max(0, cY - 15)

                                    # Objeto verde com círculo rosa
                                    #cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
                                    #cv2.drawContours(frame, [secondary1_contour], -1, (0, 0, 255), 2)
                                    cv2.circle(frame, (cX, cY), 3, (0, 0, 255), -1)
                                    cv2.circle(frame, (secondary1_cX, secondary1_cY), 3, (0, 0, 255), -1)
                                    rx,ry = uv_to_xy((cX,cY), cte)
                                    theta = -np.degrees(np.arctan2((secondary1_cY-cY), (secondary1_cX-cX)))
                                    pose = [int(rx-(xoff*np.cos(np.radians(theta)))), int(ry+(xoff*np.sin(np.radians(theta)))), int(theta)]
                                    print(f'V-R: ({pose[0]}, {pose[1]}, {pose[2]})')
                                    # print(f"Objeto verde com círculo rosa: Objeto: ({cX}, {cY}), Círculo rosa: ({secondary1_cX}, {secondary1_cY})")

                                    # #client.publish("cood(x):robo3", cX)
                                    # #client.publish("cood(y):robo3", cY)
                                    # #time.sleep(0.0001)

                                    # #data = str(cY)   # Dados para a coordenada "y" do retangulo do robo 1
                                    # #response = requests.post(esp32_central_url7, data)

                                    # #data = str(cX)  # Dados para a coordenada "x" do retangulo do robo 1
                                    # #response = requests.post(esp32_central_url8, data)

                                    # #####################################################
                                    # #Cálculo do arctg de orientação da reta

                                    # x_inicio = cX
                                    # y_inicio = cY
                                    # x_fim = secondary1_cX
                                    # y_fim = secondary1_cY

                                    # # Calculando as diferenças entre as coordenadas para obter o vetor direção
                                    # delta_x = x_fim - x_inicio
                                    # delta_y = y_fim - y_inicio

                                    # # Calculando o ângulo em radianos usando a função atan2
                                    # angulo_radianos = math.atan2(delta_y, delta_x)

                                    # # Convertendo o ângulo para graus
                                    # angulo_graus = math.degrees(angulo_radianos)

                                    # # Calculando a tangente do ângulo
                                    # tangente_angulo = math.tan(angulo_radianos)

                                    # print (f"Angulo do segmento de reta do robô verde com círculo rosa: {angulo_graus}")
                                    # print (f"A tangente desse ângulo é: {tangente_angulo}")

                                    #data = str(tangente_angulo)
                                    #response = requests.post(esp32_central_url9, data)
                                    #client.publish("rotacao:robo3", tangente_angulo)
                                    #time.sleep(0.0001)

                            for secondary2_contour in secondary2_contours:
                                secondary2_moment = cv2.moments(secondary2_contour)
                                if secondary2_moment["m00"] != 0:
                                    secondary2_cX = int(secondary2_moment["m10"] / secondary2_moment["m00"])
                                    secondary2_cY = int(secondary2_moment["m01"] / secondary2_moment["m00"])

                                    # Coordenadas do centro do círculo em relação à imagem inteira
                                    secondary2_cX += max(0, cX - 15)
                                    secondary2_cY += max(0, cY - 15)

                                    # Objeto verde com círculo amarelo
                                    #cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
                                    #cv2.drawContours(frame, [secondary2_contour], -1, (0, 255, 255), 2)
                                    cv2.circle(frame, (cX, cY), 3, (0, 0, 255), -1)
                                    cv2.circle(frame, (secondary2_cX, secondary2_cY), 3, (0, 0, 255), -1)
                                    rx,ry = uv_to_xy((cX,cY), cte)
                                    theta = -np.degrees(np.arctan2((secondary2_cY-cY), (secondary2_cX-cX)))
                                    pose = [int(rx-(xoff*np.cos(np.radians(theta)))), int(ry+(xoff*np.sin(np.radians(theta)))), int(theta)]
                                    print(f'V-A: ({pose[0]}, {pose[1]}, {pose[2]})')
                                    # print(f"Objeto verde com círculo amarelo: Objeto: ({cX}, {cY}), Círculo amarelo: ({secondary2_cX}, {secondary2_cY})")

                                    # #client.publish("cood(x):robo4", cX)
                                    # #client.publish("cood(y):robo4", cY)
                                    # #time.sleep(0.0001)

                                    # #data =  str(cY)   # Dados para a coordenada "y" do retangulo do robo 1
                                    # #response = requests.post(esp32_central_url10, data)

                                    # #data =  str(cX)  # Dados para a coordenada "x" do retangulo do robo 1
                                    # #response = requests.post(esp32_central_url11, data)

                                    # #####################################################
                                    # #Cálculo do arctg de orientação da reta

                                    # x_inicio = cX
                                    # y_inicio = cY
                                    # x_fim = secondary2_cX
                                    # y_fim = secondary2_cY

                                    # # Calculando as diferenças entre as coordenadas para obter o vetor direção
                                    # delta_x = x_fim - x_inicio
                                    # delta_y = y_fim - y_inicio

                                    # # Calculando o ângulo em radianos usando a função atan2
                                    # angulo_radianos = math.atan2(delta_y, delta_x)

                                    # # Convertendo o ângulo para graus
                                    # angulo_graus = math.degrees(angulo_radianos)

                                    # # Calculando a tangente do ângulo
                                    # tangente_angulo = math.tan(angulo_radianos)

                                    # print (f"Angulo do segmento de reta do robô verde com círculo amarelo: {angulo_graus}")
                                    # print (f"A tangente desse ângulo é: {tangente_angulo}")

                                    #data = str(tangente_angulo)
                                    #response = requests.post(esp32_central_url12, data)

                                    #client.publish("rotacao:robo4", tangente_angulo)
                                    #time.sleep(0.0001)

            if lower_orange is not None and upper_orange is not None:
                orange_mask = cv2.inRange(hsv_frame, lower_orange, upper_orange)
                orange_contours, _ = cv2.findContours(orange_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                for contour in orange_contours:
                    if cv2.contourArea(contour) > 100:
                        (x, y, w, h) = cv2.boundingRect(contour)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
                        for contour in orange_contours:
                            if cv2.contourArea(contour) > 100:
                                M = cv2.moments(contour)
                                if M["m00"] != 0:
                                    cX = int(M["m10"] / M["m00"])
                                    cY = int(M["m01"] / M["m00"])

                                    # Coordenadas do centro do círculo em relação à imagem inteira
                                    cv2.drawContours(frame, [contour], -1, (0, 165, 255), 2)  # Contorno laranja
                                    rx,ry = uv_to_xy((cX,cY), cte)
                                    print(f"Bola laranja: ({rx}, {ry})")

                                    #data =  str(cY)   # Dados para a coordenada "y" da bola
                                    #response = requests.post(esp32_central_url13, data)

                                    #data =  str(cX)  # Dados para a coordenada "x" da bola
                                    #response = requests.post(esp32_central_url14, data)

                                    #client.publish("cood(x):bola", cX)
                                    #client.publish("cood(y):bola", cY)
                                    #time.sleep(0.0001)

            cv2.imshow('frame', frame)

            time.sleep(display_interval)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

def main():
    if select_points() and select_orange_color() and select_blue_color() and select_green_color() and select_pink_color() and select_yellow_color():
        detect_colors_with_contours()
    else:
        print("Não foi possível definir a cor laranja. Fechando o programa.")

if __name__ == "__main__":
    main()
