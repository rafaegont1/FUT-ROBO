import cv2 as cv

class Video:
    def __init__(self, id, width, height, fps, window_name='frame', waitKey_delay=40):
        self.cap = cv.VideoCapture(id)

        self.cap.set(cv.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv.CAP_PROP_AUDIO_SAMPLES_PER_SECOND, fps)

        if not self.cap.isOpened():
            raise RuntimeError("Não foi possível abrir a câmera.")

        self.frame = None
        self.frame_enhanced = None
        self.frame_hsv = None

        self.window_name = window_name
        self.waitKey_delay = waitKey_delay

        cv.namedWindow(window_name)

    def __del__(self):
        self.cap.release()
        cv.destroyWindow(self.window_name)

    def update_frame(self):
        ret, self.frame = self.cap.read()

        if not ret:
            # raise RuntimeError("Falha ao capturar o frame da câmera.")

            # HACK: reiniciar o vídeo quando ele chega ao fim
            cap.set(cv.CAP_PROP_POS_FRAMES, 0)  # rascunho
            print('Rewinding video...')  # rascunho
            return  # rascunho

        self.frame_enhanced = self.__enhance_contrast()
        self.frame_hsv = cv.cvtColor(self.frame_enhanced, cv.COLOR_BGR2HSV)

    def show_frame(self):
        cv.imshow(self.window_name, self.frame)
        key = cv.waitKey(self.waitKey_delay)

        return key

    def __enhance_contrast(self, ksize=5):
        '''
        @brief: Aumenta o contraste e aplica desfoque à imagem.

        @param frame: imagem a ser melhorada
        @param ksize: tamanho do kernel para a suavização
        @return: a imagem com contraste aumentado e suavizada.
        '''
        # Converte para o espaço de cores LAB
        lab = cv.cvtColor(self.frame, cv.COLOR_BGR2LAB)

        # Divide os canais L, A, B
        l, a, b = cv.split(lab)

        # Aplica CLAHE no canal L
        clahe = cv.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)

        # Une os canais L ajustado, A e B
        limg = cv.merge((cl, a, b))

        # Converte de volta para BGR
        frame_enhanced = cv.cvtColor(limg, cv.COLOR_LAB2BGR)

        # Aplica suavização usando desfoque Gaussiano
        blurred_frame = cv.GaussianBlur(frame_enhanced, (ksize, ksize), 0)

        return blurred_frame
