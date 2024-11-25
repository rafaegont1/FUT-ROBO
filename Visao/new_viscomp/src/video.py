import cv2 as cv
import numpy as np

class Video:
    def __init__(
        self, 
        id: int, 
        width: int, 
        height: int, 
        fps: float, 
        window_name: str = "frame", 
        waitKey_delay: int = 40
    ) -> None:
        """
        Inicializa a captura de vídeo a partir de uma câmera ou arquivo de vídeo.

        @param id: ID da câmera ou caminho para o arquivo de vídeo.
        @param width: Largura do frame de vídeo.
        @param height: Altura do frame de vídeo.
        @param fps: Taxa de quadros por segundo.
        @param window_name: Nome da janela para exibição do vídeo (opcional).
        @param waitKey_delay: Atraso para a função `cv.waitKey` (opcional).
        """
        self.cap = cv.VideoCapture(id)

        self.cap.set(cv.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv.CAP_PROP_FPS, fps)  # Corrigido para CAP_PROP_FPS

        if not self.cap.isOpened():
            raise RuntimeError("Não foi possível abrir a câmera.")

        self.frame: np.ndarray = None
        self.frame_enhanced: np.ndarray = None
        self.frame_hsv: np.ndarray = None

        self.window_name: str = window_name
        self.waitKey_delay: int = waitKey_delay

        cv.namedWindow(window_name)

    def __del__(self) -> None:
        """
        Libera a captura de vídeo e destrói a janela de exibição.

        @return: None
        """
        self.cap.release()
        cv.destroyWindow(self.window_name)

    def update_frame(self) -> None:
        """
        Atualiza o frame atual do vídeo. Realiza a leitura do próximo frame
        e aplica o processamento de aumento de contraste e conversão para HSV.

        @return: None
        """
        ret, self.frame = self.cap.read()

        if not ret:
            # HACK: reiniciar o vídeo quando ele chega ao fim
            self.cap.set(cv.CAP_PROP_POS_FRAMES, 0)  # rascunho
            print("Rewinding video...")  # rascunho
            return  # rascunho

        self.frame_enhanced = self.__enhance_contrast()
        self.frame_hsv = cv.cvtColor(self.frame_enhanced, cv.COLOR_BGR2HSV)

    def show_frame(self) -> int:
        """
        Exibe o frame atual em uma janela.

        @return: Código da tecla pressionada (se houver).
        """
        cv.imshow(self.window_name, self.frame)
        key: int = cv.waitKey(self.waitKey_delay)

        return key

    def __enhance_contrast(self, ksize: int = 5) -> np.ndarray:
        """
        Aumenta o contraste e aplica desfoque à imagem.

        @param ksize: Tamanho do kernel para a suavização (default é 5).
        @return: A imagem com contraste aumentado e suavizada.
        """
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
