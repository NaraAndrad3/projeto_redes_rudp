from checksum import (
    gera_checksum,
    verifica_checksum
)

from packet import Packet, ACK

payload = b"Teste de pacote R-UDP"

packet = Packet(sequence_number=1, payload=payload)
packet_bytes = packet.to_bytes()
received_packet = Packet.from_bytes(packet_bytes)

print(received_packet.sequence_number)
print(received_packet.payload)
print(received_packet.payload == payload)

ack = ACK(ack_number=1)
ack_bytes = ack.to_bytes()
received_ack = ACK.from_bytes(ack_bytes)

print(received_ack.ack_number)