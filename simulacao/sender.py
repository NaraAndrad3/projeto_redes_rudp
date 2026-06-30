import math

from simulation.packet import create_data_packet
from simulation.config import (
    CHUNK_SIZE_BYTES,
    WINDOW_SIZE,
    TIMEOUT,
    MAX_RETRIES
)


class Sender:
    """
    Representa o emissor R-UDP na simulação.

    Implementa:
    - janela deslizante Go-Back-N;
    - envio de pacotes;
    - recebimento de ACKs cumulativos;
    - timeout;
    - retransmissão a partir da base da janela.
    """

    def __init__(self, env, network, metrics, file_size_bytes: int):
        self.env = env
        self.network = network
        self.metrics = metrics
        self.file_size_bytes = file_size_bytes

        self.total_packets = math.ceil(
            file_size_bytes / CHUNK_SIZE_BYTES
        )

        self.base = 0
        self.next_seq_num = 0
        self.retries = 0

        self.acked_until = -1
        self.send_times = {}

        self.finished = False

    def run(self):
        """
        Processo principal do emissor.

        Executa o envio dos pacotes usando Go-Back-N.
        """

        self.metrics.start_time = self.env.now

        while self.base < self.total_packets:
            self._send_window()

            current_base = self.base

            yield self.env.timeout(TIMEOUT)

            if self.base == current_base:
                self.retries += 1

                if self.retries > MAX_RETRIES:
                    print("[SIM] Número máximo de tentativas atingido.")
                    break

                self._retransmit_from_base()
            else:
                self.retries = 0

        self.metrics.end_time = self.env.now
        self.finished = True

    def _send_window(self):
        """
        Envia novos pacotes enquanto houver espaço na janela.
        """

        while (
            self.next_seq_num < self.base + WINDOW_SIZE
            and self.next_seq_num < self.total_packets
        ):
            packet_size = self._packet_size(
                self.next_seq_num
            )

            packet = create_data_packet(
                sequence_number=self.next_seq_num,
                size_bytes=packet_size,
                current_time=self.env.now
            )

            self.metrics.register_original_packet(
                packet.size_bytes
            )

            self.send_times[packet.sequence_number] = self.env.now

            self.network.send_data(packet)

            self.next_seq_num += 1

    def _retransmit_from_base(self):
        """
        Retransmite todos os pacotes pendentes a partir da base da janela.

        Este é o comportamento característico do Go-Back-N.
        """

        self.next_seq_num = self.base

        while (
            self.next_seq_num < self.base + WINDOW_SIZE
            and self.next_seq_num < self.total_packets
        ):
            packet_size = self._packet_size(
                self.next_seq_num
            )

            packet = create_data_packet(
                sequence_number=self.next_seq_num,
                size_bytes=packet_size,
                current_time=self.env.now
            )

            self.metrics.register_retransmission(
                packet.size_bytes
            )

            self.send_times[packet.sequence_number] = self.env.now

            self.network.send_data(packet)

            self.next_seq_num += 1

    def receive_ack(self, ack_packet):
        """
        Recebe um ACK cumulativo vindo do receptor.
        """

        ack_number = ack_packet.sequence_number

        self.metrics.register_ack_received()

        if ack_number in self.send_times:
            rtt = self.env.now - self.send_times[ack_number]
            self.metrics.register_rtt(rtt)

        if ack_number >= self.base:
            self.base = ack_number + 1
            self.acked_until = ack_number

    def _packet_size(self, sequence_number: int) -> int:
        """
        Calcula o tamanho do pacote.

        O último pacote pode ter tamanho menor que CHUNK_SIZE_BYTES.
        """

        remaining_bytes = (
            self.file_size_bytes
            - sequence_number * CHUNK_SIZE_BYTES
        )

        return min(
            CHUNK_SIZE_BYTES,
            remaining_bytes
        )tem