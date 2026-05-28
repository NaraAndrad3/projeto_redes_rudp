import os
import socket
from src.common.config import OUTPUT_DIR, SERVER_HOST, SERVER_PORT_TCP, BUFFER_SIZE, OUTPUT_DIR




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
    
    
    output_file = os.path.join(OUTPUT_DIR, "received_file_tcp.txt")
    
    with open(output_file, "wb") as f:
        while True:
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                break
            f.write(data)
    
    print("[TCP SERVER] Arquivo recebido com sucesso.")
    
    client_socket.close()
    server_socket.close()
    
if __name__ == "__main__":
    start_tcp_server()
    
    