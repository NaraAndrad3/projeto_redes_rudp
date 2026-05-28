import os, socket
from src.common.config import SERVER_HOST, SERVER_PORT_UDP, BUFFER_SIZE, OUTPUT_DIR
from src.common.packet import Packet, ACK


def start_udp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT_UDP))
    
    print(f"[R-UDP SERVER] Escutando na porta {SERVER_PORT_UDP}...")
    
    expected_sequence_number = 0
    last_ack_number = -1
    
    output_file_path = os.path.join(OUTPUT_DIR, "received_file_udp.txt")
    
    with open(output_file_path, "wb") as file:
        while True: 
            packet_data, client_address = server_socket.recvfrom(BUFFER_SIZE)
            if not packet_data == b'END':
                print("[R-UDP SERVER] Fim da transmissão recebido.")
                break
            try:
                packet = Packet.from_bytes(packet_data)
                if packet.sequence_number == expected_sequence_number:
                    file.write(packet.payload)
                    last_ack_number = packet.sequence_number
                    expected_sequence_number += 1
                    print(
                        f"[R-UDP SERVER] Pacote {packet.sequence_number} recebido corretamente."
                    )
                else:
                    print(
                        f"[R-UDP SERVER] Pacote fora de ordem. "
                        f"Esperado: {expected_sequence_number}, "
                        f"Recebido: {packet.sequence_number}"
                    )
                ack = ACK(last_ack_number)
                server_socket.sendto(ack.to_bytes(), client_address)
            except ValueError:
                print("[R-UDP SERVER] Pacote corrompido descartado.")
                
                ack = ACK(last_ack_number)
                server_socket.sendto(ack.to_bytes(), client_address)
    
    server_socket.close()
    print("[R-UDP SERVER] Arquivo salvo com sucesso.")

if __name__ == "__main__":
    start_udp_server()
                    
                
    
    

