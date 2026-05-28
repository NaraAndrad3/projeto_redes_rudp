import struct

from src.common.checksum import gera_checksum, verifica_checksum


PACKET_TYPE_DATA = 1
PACKET_TYPE_METADATA = 2
PACKET_TYPE_END = 3

HEADER_FORMAT = "!BI32sI"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

ACK_FORMAT = "!i"
ACK_SIZE = struct.calcsize(ACK_FORMAT)


class Packet:
    def __init__(self, packet_type: int, sequence_number: int, payload: bytes):
        self.packet_type = packet_type
        self.sequence_number = sequence_number
        self.payload = payload
        self.checksum = gera_checksum(payload)
        self.payload_size = len(payload)

    def to_bytes(self) -> bytes:
        header = struct.pack(
            HEADER_FORMAT,
            self.packet_type,
            self.sequence_number,
            self.checksum,
            self.payload_size
        )

        return header + self.payload

    @classmethod
    def from_bytes(cls, packet_bytes: bytes):
        header = packet_bytes[:HEADER_SIZE]
        payload = packet_bytes[HEADER_SIZE:]

        packet_type, sequence_number, received_checksum, payload_size = struct.unpack(
            HEADER_FORMAT,
            header
        )

        payload = payload[:payload_size]

        if not verifica_checksum(payload, received_checksum):
            raise ValueError("Checksum inválido: pacote corrompido.")

        packet = cls(
            packet_type=packet_type,
            sequence_number=sequence_number,
            payload=payload
        )

        packet.checksum = received_checksum
        packet.payload_size = payload_size

        return packet


class ACK:
    def __init__(self, ack_number: int):
        self.ack_number = ack_number

    def to_bytes(self) -> bytes:
        return struct.pack(ACK_FORMAT, self.ack_number)

    @classmethod
    def from_bytes(cls, ack_bytes: bytes):
        ack_number = struct.unpack(
            ACK_FORMAT,
            ack_bytes[:ACK_SIZE]
        )[0]

        return cls(ack_number)