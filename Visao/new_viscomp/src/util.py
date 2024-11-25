#!/usr/bin/env python3

import numpy as np
import os

folder_path = "data"


def file_read(name):
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


def file_write(name, data):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder created at {folder_path}")

    file_path = os.path.join(folder_path, name)

    # Salvar os dados como um arquivo .npy (formato binário eficiente)
    np.save(file_path, np.array(data))
    print(f"Os números foram salvos em '{name}'.")


def main():
    # Certifique-se de que o diretório existe
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file_data = file_read('test.npy')

    if file_data.size == 0:  # Verifica se o arquivo está vazio ou não existe
        data = []

        while True:
            try:
                num = input("Digite um número (ou 'sair' para finalizar): ")
                if num.lower() == 'sair':
                    break
                num = float(num)
                data.append(num)

            except ValueError:
                print("Por favor, digite um número válido.")

        file_write('test.npy', data)


if __name__ == '__main__':
    main()
