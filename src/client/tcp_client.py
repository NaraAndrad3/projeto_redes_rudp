import os
import socket
import time

from src.common.config import (
    SERVER_DOCKER_NAME,
    SERVER_PORT_TCP,
    CHUNK_SIZE,
    INPUT_DIR
)


def start_tcp_client(filename: str):
    """
    Inicializa o cliente TCP e envia um arquivo. O cliente se conecta ao servidor usando o nome do container e a porta TCP definida
    nas configurações. O arquivo é lido em blocos (chunks) de tamanho definido por CHUNK_SIZE e enviado ao servidor usando o método
    sendall() do socket TCP.,
    """

    client_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )
    # Conectar ao servidor usando o nome do container e a porta TCP definida nas configurações
    client_socket.connect(
        (SERVER_DOCKER_NAME, SERVER_PORT_TCP)
    )

    filepath = os.path.join(INPUT_DIR, filename)
    # Medir o tempo de envio do arquivo para calcular o throughput
    start_time = time.time()

    total_bytes_sent = 0
    # Abrir o arquivo para leitura em modo binário e enviar em blocos (chunks) de tamanho definido por CHUNK_SIZE
    with open(filepath, "rb") as file:

        while True:
            chunk = file.read(CHUNK_SIZE)

            if not chunk:
                break

            client_socket.sendall(chunk)

            total_bytes_sent += len(chunk)
    # Medir o tempo de envio do arquivo para calcular o throughput
    end_time = time.time()

    elapsed_time = end_time - start_time

    throughput = total_bytes_sent / elapsed_time

    print(f"[TCP CLIENT] Arquivo enviado com sucesso.")
    print(f"[TCP CLIENT] Bytes enviados: {total_bytes_sent}")
    print(f"[TCP CLIENT] Tempo total: {elapsed_time:.4f} s")
    print(f"[TCP CLIENT] Throughput: {throughput:.2f} B/s")

    client_socket.close()

if __name__ == "__main__":
    start_tcp_client("test.txt")