import os
import socket
from src.common.config import OUTPUT_DIR, SERVER_HOST, SERVER_PORT_TCP, BUFFER_SIZE, OUTPUT_DIR
import struct

def receive_exact(socket_connection, size: int):
    data = b""
    
    while len(data) < size:
        packet = socket_connection.recv(size - len(data))
        if not packet:
            raise ConnectionError("Conexão fechada pelo cliente antes de receber todos os dados.")
        data += packet

    return data


def start_tcp_server():
    """ 
    Inicia o servidor TCP para receber arquivos do cliente. 
    """
    # Criar o socket TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT_TCP))
    server_socket.listen(1)
    
    print(f"[TCP SERVER] Escutando na porta {SERVER_PORT_TCP}...")
    client_socket, client_address = server_socket.accept()
    print(f"[TCP SERVER] Conexão recebida de {client_address}")
    
    header_format = '!IIQ'
    header_size = struct.calcsize(header_format)
    header = receive_exact(client_socket, header_size)
    
    filename_size, auth_size, file_size = struct.unpack(header_format, header)
    
    filename = receive_exact(client_socket, filename_size).decode('utf-8')
    custom_auth = receive_exact(client_socket, auth_size).decode('utf-8')
    
    print(f"[TCP SERVER] Arquivo: {filename}")
    print(f"[TCP SERVER] Tamanho esperado: {file_size} bytes")
    print(f"[TCP SERVER] X-Custom-Auth: {custom_auth}")

    output_file = os.path.join(OUTPUT_DIR, f"received_tcp_{filename}")
    
    total_received = 0
    
    with open(output_file, "wb") as file:
        while total_received < file_size:
            data = client_socket.recv(BUFFER_SIZE)

            if not data:
                break

            file.write(data)
            total_received += len(data)

    print("[TCP SERVER] Arquivo recebido com sucesso.")
    print(f"[TCP SERVER] Bytes recebidos: {total_received}")

    client_socket.close()
    server_socket.close()
    
if __name__ == "__main__":
    start_tcp_server()
    
    