import os, socket, time, json, sys
from src.common.config import SERVER_DOCKER_NAME, SERVER_PORT_UDP, CHUNK_SIZE, TIMEOUT, MAX_RETRIES, INPUT_DIR, TIMEOUT, WINDOW_SIZE, CUSTOM_AUTH
from src.common.packet import Packet, ACK, PACKET_TYPE_DATA, PACKET_TYPE_METADATA, PACKET_TYPE_END

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
    print(
    f"[R-UDP CLIENT] Total de pacotes: {len(packets)}"
    )
    
    metadata = {
    "filename": filename,
    "file_size": os.path.getsize(file_path),
    "custom_auth": CUSTOM_AUTH
}

    metadata_payload = json.dumps(metadata).encode("utf-8")

    metadata_packet = Packet(
        packet_type=PACKET_TYPE_METADATA,
        sequence_number=0,
        payload=metadata_payload
    )
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(TIMEOUT)
    
    server_address = (SERVER_DOCKER_NAME, SERVER_PORT_UDP)
    
    base = 0
    next_seq_num = 0
    retries = 0
    total_retries = 0
    
    start_time = time.time()
    
    metadata_ack_received = False

    while not metadata_ack_received:
        client_socket.sendto(
            metadata_packet.to_bytes(),
            server_address
        )

        print("[R-UDP CLIENT] Pacote de metadados enviado.")

        try:
            ack_data, _ = client_socket.recvfrom(1024)
            ack = ACK.from_bytes(ack_data)

            if ack.ack_number == -1:
                metadata_ack_received = True
                print("[R-UDP CLIENT] ACK de metadados recebido.")

        except socket.timeout:
            print("[R-UDP CLIENT] Timeout nos metadados. Reenviando...")
    
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
            
    end_packet = Packet(
    packet_type=PACKET_TYPE_END,
    sequence_number=base,
    payload=b""
)

    client_socket.sendto(
        end_packet.to_bytes(),
        server_address
    )
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

    if len(sys.argv) != 2:
        print(
            "Uso: python3 -m src.client.rudp_client <arquivo>"
        )
        sys.exit(1)

    start_udp_client(sys.argv[1])