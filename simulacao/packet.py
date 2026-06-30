from dataclasses import dataclass


PACKET_TYPE_DATA = "DATA"
PACKET_TYPE_ACK = "ACK"


@dataclass
class Packet:
    """
    Representa um pacote lógico dentro da simulação.

    Diferente da Fase 1, aqui não precisamos converter o pacote para bytes,
    pois não estamos usando sockets reais. O pacote é apenas uma entidade
    que circula entre emissor, rede simulada e receptor.
    """

    packet_type: str
    sequence_number: int
    size_bytes: int
    created_at: float


def create_data_packet(sequence_number: int, size_bytes: int, current_time: float) -> Packet:
    """
    Cria um pacote de dados.

    Args:
        sequence_number: número de sequência do pacote.
        size_bytes: tamanho do pacote em bytes.
        current_time: tempo atual da simulação.

    Returns:
        Packet: pacote de dados.
    """

    return Packet(
        packet_type=PACKET_TYPE_DATA,
        sequence_number=sequence_number,
        size_bytes=size_bytes,
        created_at=current_time
    )


def create_ack_packet(sequence_number: int, current_time: float) -> Packet:
    """
    Cria um pacote ACK.

    No Go-Back-N, o ACK é cumulativo. Portanto, o número de sequência
    representa o último pacote recebido corretamente pelo receptor.

    Args:
        sequence_number: número de sequência confirmado.
        current_time: tempo atual da simulação.

    Returns:
        Packet: pacote ACK.
    """

    return Packet(
        packet_type=PACKET_TYPE_ACK,
        sequence_number=sequence_number,
        size_bytes=40,
        created_at=current_time
    )