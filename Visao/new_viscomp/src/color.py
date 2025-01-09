import cv2 as cv
import numpy as np
from src.util import file_read, file_write
from typing import List, Tuple, Optional, Union


class Color:
    def __init__(
        self,
        name: str,
        min_area: int = 100,
        hs_tolerance: Tuple[int, int] = (10, 75)
    ) -> None:
        """
        Inicializa o objeto Color, que representa uma cor que pode ser selecionada e utilizada 
        para segmentação em imagens, com base em valores HSV.

        @param name: Nome da cor, usado para gerar os arquivos de calibração (lower/upper HSV).
        @param min_area: Área mínima do contorno para considerar o centroid da cor como válido.
        @param hs_tolerance: Tupla de tolerância para o valor de hue (h) e saturation (s) no espaço HSV.
        """
        self.name: str = name
        self.min_area: int = min_area
        self.hs_tolerance: Tuple[int, int] = hs_tolerance
        self.lower_hsv_file: str = f'{self.name}_lower_hsv.npy'
        self.upper_hsv_file: str = f'{self.name}_upper_hsv.npy'

        # Lê os valores de lower e upper HSV de arquivos ou inicializa com None
        self.lower_hsv: np.ndarray = file_read(self.lower_hsv_file)
        self.upper_hsv: np.ndarray = file_read(self.upper_hsv_file)

        self.uv: Optional[Tuple[int, int], List[Tuple[int, int]]] = None  # Coordenadas UV ou lista de centroides

    def is_hsv_empty(self) -> bool:
        """
        Verifica se os limites de HSV (lower e upper) estão vazios.

        @return: Retorna True se os limites de HSV não estão definidos, False caso contrário.
        """
        return not (self.lower_hsv.any() and self.upper_hsv.any())

    def select(self, frame: np.ndarray, waitKey_delay: int) -> None:
        """
        Permite ao usuário selecionar a cor na imagem clicando na região desejada. 
        A cor é então convertida para o espaço HSV e os limites lower/upper HSV são calculados.

        @param frame: Imagem do frame a ser exibida para o usuário.
        @param waitKey_delay: Delay de espera entre os quadros para interação do usuário.
        """
        select_window_name = f"Clique na cor desejada para '{self.name}'"
        cv.namedWindow(select_window_name)

        try:
            while not self.lower_hsv.any() and not self.upper_hsv.any():
                cv.imshow(select_window_name, frame)
                cv.setMouseCallback(select_window_name, self.__click_event, param=frame)
                key = cv.waitKey(waitKey_delay)
                if key == ord('q'):
                    break
        finally:
            cv.destroyWindow(select_window_name)

        # Converte para HSV e aplica a máscara
        frame_hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        mask = cv.inRange(frame_hsv, self.lower_hsv, self.upper_hsv)
        frame_hsv_masked = cv.bitwise_and(frame_hsv, frame_hsv, mask=mask)
        res = cv.cvtColor(frame_hsv_masked, cv.COLOR_HSV2BGR)

        # Exibe a imagem isolada
        isolation_window_name = "Isolamento da cor selecionada"
        cv.imshow(isolation_window_name, res)
        cv.waitKey(0)
        cv.destroyWindow(isolation_window_name)

        # Salva os limites de HSV para uso futuro
        file_write(self.lower_hsv_file, self.lower_hsv)
        file_write(self.upper_hsv_file, self.upper_hsv)

    def __click_event(self, event: int, x: int, y: int, flags: int, param: np.ndarray) -> None:
        """
        Função de callback chamada quando o usuário clica na imagem. Usada para selecionar a cor desejada.

        @param event: Tipo de evento (ex.: clique do mouse).
        @param x: Coordenada X do clique.
        @param y: Coordenada Y do clique.
        @param flags: Flags do evento do mouse.
        @param param: Imagem do frame, passada como parâmetro para o callback.
        """
        if event != cv.EVENT_LBUTTONDOWN:
            return

        clicked_color = param[y, x]

        # Converte a cor clicada de BGR para HSV
        hsv_color = cv.cvtColor(np.uint8([[clicked_color]]), cv.COLOR_BGR2HSV)[0][0]

        # Define os limites de hue e saturation com base no valor clicado
        lower_h = int(hsv_color[0]) - self.hs_tolerance[0]
        lower_s = int(hsv_color[1]) - self.hs_tolerance[1]
        self.lower_hsv = np.array([
            np.clip(lower_h, 0, 179),
            np.clip(lower_s, 0, 255),
            20
        ])

        upper_h = int(hsv_color[0]) + self.hs_tolerance[0]
        upper_s = int(hsv_color[1]) + self.hs_tolerance[1]
        self.upper_hsv = np.array([
            np.clip(upper_h, 0, 179),
            np.clip(upper_s, 0, 255),
            255
        ])

    def find_centroid(
        self,
        img_hsv: np.ndarray,
        multi_centroids: bool = False
    ) -> Union[Tuple[int, int], List[Tuple[int, int]]]:
        """
        Encontra o(s) centro(s)ide(s) da cor no espaço HSV, baseado nos limites de HSV definidos.

        @param img_hsv: Imagem já convertida para o espaço de cor HSV.
        @param multi_centroids: Se True, retorna todos os centroides encontrados; 
                                Se False, retorna apenas o primeiro centroide encontrado.

        @return: Retorna uma tupla com as coordenadas UV do centroide ou uma lista de centroides, 
                ou None caso nenhum centroide válido seja encontrado.
        """
        mask = cv.inRange(img_hsv, self.lower_hsv, self.upper_hsv)
        contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        if multi_centroids:
            self.uv = []
        else:
            self.uv = None

        for contour in contours:
            area = cv.contourArea(contour)

            if area < self.min_area:
                continue

            M = cv.moments(contour)

            if M["m00"] == 0:
                continue

            uv = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            if multi_centroids:
                self.uv.append(uv)
            else:
                self.uv = uv
                break

        return self.uv
