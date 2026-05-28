import os, socket, time, json
from src.common.config import SERVER_HOST, SERVER_PORT_UDP, BUFFER_SIZE, OUTPUT_DIR, CUSTOM_AUTH
from src.common.packet import Packet, ACK, PACKET_TYPE_DATA, PACKET_TYPE_METADATA, PACKET_TYPE_END



def start_udp_server():
    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    server_socket.bind(
        (SERVER_HOST, SERVER_PORT_UDP)
    )

    print(f"[R-UDP SERVER] Escutando na porta {SERVER_PORT_UDP}...")

    expected_sequence_number = 0
    last_ack_number = -1
    output_file = None
    output_file_path = None
    expected_file_size = 0
    total_received = 0

    while True:
        packet_data, client_address = server_socket.recvfrom(65535)

        try:
            packet = Packet.from_bytes(packet_data)

            if packet.packet_type == PACKET_TYPE_METADATA:
                metadata = json.loads(
                    packet.payload.decode("utf-8")
                )

                filename = metadata["filename"]
                expected_file_size = metadata["file_size"]
                custom_auth = metadata["custom_auth"]

                output_file_path = os.path.join(
                    OUTPUT_DIR,
                    f"received_rudp_{filename}"
                )

                output_file = open(output_file_path, "wb")

                print("[R-UDP SERVER] Metadados recebidos.")
                print(f"[R-UDP SERVER] Arquivo: {filename}")
                print(f"[R-UDP SERVER] Tamanho esperado: {expected_file_size} bytes")
                print(f"[R-UDP SERVER] X-Custom-Auth: {custom_auth}")

                ack = ACK(-1)
                server_socket.sendto(
                    ack.to_bytes(),
                    client_address
                )

            elif packet.packet_type == PACKET_TYPE_DATA:
                if output_file is None:
                    print("[R-UDP SERVER] Dados recebidos antes dos metadados.")
                    continue

                if packet.sequence_number == expected_sequence_number:
                    output_file.write(packet.payload)

                    total_received += len(packet.payload)
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
                server_socket.sendto(
                    ack.to_bytes(),
                    client_address
                )

            elif packet.packet_type == PACKET_TYPE_END:
                print("[R-UDP SERVER] Fim da transmissão recebido.")
                break

        except ValueError as error:
            print(f"[R-UDP SERVER] Erro ao processar pacote: {error}")

            ack = ACK(last_ack_number)
            server_socket.sendto(
                ack.to_bytes(),
                client_address
            )

    if output_file is not None:
        output_file.close()

    print("[R-UDP SERVER] Arquivo salvo com sucesso.")
    print(f"[R-UDP SERVER] Caminho: {output_file_path}")
    print(f"[R-UDP SERVER] Bytes recebidos: {total_received}")
    print(f"[R-UDP SERVER] Bytes esperados: {expected_file_size}")

    server_socket.close()


if __name__ == "__main__":
    start_udp_server()