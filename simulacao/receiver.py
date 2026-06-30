from simulacao.packet import (
    PACKET_TYPE_DATA,
    create_ack_packet
)


class Receiver:
    """
    Representa o receptor R-UDP na simulação.

    O receptor implementa o comportamento do Go-Back-N:
    - aceita apenas pacotes em ordem;
    - descarta pacotes fora de ordem;
    - envia ACK cumulativo para o último pacote recebido corretamente.
    """

    def __init__(self, env, network, metrics):
        self.env = env
        self.network = network
        self.metrics = metrics

        self.expected_sequence_number = 0
        self.last_ack_number = -1

        self.received_packets = 0
        self.received_bytes = 0

    def receive(self, packet):
        """
        Recebe um pacote DATA entregue pela rede simulada.
        """

        if packet.packet_type != PACKET_TYPE_DATA:
            return

        if packet.sequence_number == self.expected_sequence_number:
            self.received_packets += 1
            self.received_bytes += packet.size_bytes

            self.last_ack_number = packet.sequence_number
            self.expected_sequence_number += 1

        # Mesmo que o pacote esteja fora de ordem, o ACK enviado é cumulativo.
        ack = create_ack_packet(
            sequence_number=self.last_ack_number,
            current_time=self.env.now
        )

        self.metrics.register_ack_sent(
            ack.size_bytes
        )

        self.network.send_ack(ack)

    def is_complete(self, total_packets: int) -> bool:
        """
        Verifica se todos os pacotes esperados foram recebidos.
        """

        return self.received_packets >= total_packets