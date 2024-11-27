import numpy as np
import os
from typing import Union

folder_path = "data"


def file_read(name: str) -> np.ndarray:
    """
    Lê um arquivo .npy contendo um array de números. Se o arquivo não for encontrado, um array vazio é retornado.

    @param name: O nome do arquivo a ser lido.
    @return: Um array NumPy contendo os dados lidos do arquivo, ou um array vazio se o arquivo não for encontrado ou houver erro ao carregar.
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder created at {folder_path}")

    file_path = os.path.join(folder_path, name)

    try:
        # Carregar o array de números do arquivo .npy
        data = np.load(file_path)
        print(f"Numeros lidos do arquivo: {data}")

    except FileNotFoundError:
        print("Arquivo não encontrado. Criando o arquivo e pedindo números.")
        data = np.array([])

    except ValueError:
        print(f"Erro ao carregar os dados de {file_path}. O formato pode estar incorreto.")
        data = np.array([])

    return data


def file_write(name: str, data: Union[np.ndarray, list]) -> None:
    """
    Salva os dados em um arquivo .npy. Se a pasta não existir, ela será criada.

    @param name: O nome do arquivo onde os dados serão salvos.
    @param data: Os dados a serem salvos, que podem ser um array NumPy ou uma lista.
    @return: None
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder created at {folder_path}")

    file_path = os.path.join(folder_path, name)

    # Salvar os dados como um arquivo .npy (formato binário eficiente)
    np.save(file_path, np.array(data))
    print(f"Os números foram salvos em '{name}'.")
