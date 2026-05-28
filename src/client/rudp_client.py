import os, socket, time
from src.common.config import SERVER_DOCKER_NAME, SERVER_PORT_UDP, BUFFER_SIZE, CHUNK_SIZE, TIMEOUT, MAX_RETRIES, INPUT_DIR, TIMEOUT, WINDOW_SIZE
from src.common.packet import Packet, ACK, PACKET_TYPE_DATA

def create_packets(file_path: str):
    
    """ Lê um arquivo e o divide em pacotes de acordo com o tamanho definido por CHUNK_SIZE. 
    Cada pacote é criado com um número de sequência, o payload do chunk e um checksum para verificação de integridade.

    Returns:
        list[Packet]: Uma lista de objetos Packet prontos para serem enviados pela rede.
    """
    
    packets = [] # Lista para armazenar os pacotes criados
    sequence_number = 0
    with open(file_path, "rb") as file:
        while True:
            chunk = file.read(CHUNK_SIZE) # Lê um chunk do arquivo com o tamanho definido por CHUNK_SIZE
            if not chunk:
                break
            packet = Packet(packet_type=PACKET_TYPE_DATA, sequence_number=sequence_number, payload=chunk) # Cria um pacote usando o construtor da classe Packet, que calcula automaticamente o checksum e o tamanho do payload
            packets.append(packet) # Adiciona o pacote criado à lista de pacotes
            sequence_number += 1 # Incrementa o número de sequência para o próximo pacote
    return packets

def start_udp_client(filename: str):
    file_path = os.path.join(INPUT_DIR, filename)
    packets = create_packets(file_path)
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(TIMEOUT)
    
    server_address = (SERVER_DOCKER_NAME, SERVER_PORT_UDP)
    
    base = 0
    next_seq_num = 0
    retries = 0
    total_retries = 0
    
    start_time = time.time()
    
    while base < len(packets):
        while next_seq_num < base + WINDOW_SIZE and next_seq_num < len(packets):
            client_socket.sendto(packets[next_seq_num].to_bytes(), server_address)
            
            print(f"[R-UDP CLIENT] Pacote {packets[next_seq_num].sequence_number} enviado.")
            next_seq_num += 1
        
        try:
            ack_data, _ = client_socket.recvfrom(1024)
            ack = ACK.from_bytes(ack_data)
            
            print(f"[R-UDP CLIENT] ACK {ack.ack_number} recebido.")
            
            if ack.ack_number >= base:
                base = ack.ack_number + 1
                retries = 0
                
        except socket.timeout:
            print("[R-UDP CLIENT] Timeout. Retransmitindo pacotes...")

            retries += 1
     
            if retries > MAX_RETRIES:
                print("[R-UDP CLIENT] Número máximo de tentativas atingido. Encerrando conexão.")
                break
            
            print(f"[R-UDP CLIENT] Retransmitindo pacotes a partir do número de sequência {base}...")
            total_retries += next_seq_num - base
            next_seq_num = base
            
    client_socket.sendto(b'END', server_address)
    end_time = time.time()
    elapsed_time = end_time - start_time
    total_bytes_sent = os.path.getsize(file_path)
    throughput = total_bytes_sent / elapsed_time

        
    print("[R-UDP CLIENT] Transmissão finalizada.")
    print(f"[R-UDP CLIENT] Arquivo: {filename}")
    print(f"[R-UDP CLIENT] Bytes úteis enviados: {total_bytes_sent}")
    print(f"[R-UDP CLIENT] Tempo total: {elapsed_time:.4f} s")
    print(f"[R-UDP CLIENT] Throughput útil: {throughput:.2f} B/s")
    print(f"[R-UDP CLIENT] Retransmissões: {total_retries}")

    client_socket.close()

if __name__ == "__main__":

    start_udp_client('test.txt')