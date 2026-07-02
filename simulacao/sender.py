import math

from simulacao.packet import create_data_packet


class Sender:
    def __init__(
        self,
        env,
        network,
        metrics,
        file_size_bytes: int,
        chunk_size_bytes: int,
        window_size: int,
        timeout: float,
        max_retries: int
    ):
        self.env = env
        self.network = network
        self.metrics = metrics
        self.file_size_bytes = file_size_bytes
        self.chunk_size_bytes = chunk_size_bytes
        self.window_size = window_size
        self.timeout = timeout
        self.max_retries = max_retries

        self.total_packets = math.ceil(
            file_size_bytes / chunk_size_bytes
        )

        self.base = 0
        self.next_seq_num = 0
        self.retries = 0
        self.send_times = {}

        self.ack_event = env.event()
        self.finished = False

    def run(self):
        self.metrics.start_time = self.env.now

        while self.base < self.total_packets:
            self._send_window()

            current_base = self.base
            timeout_event = self.env.timeout(self.timeout)

            result = yield self.ack_event | timeout_event

            if self.ack_event in result:
                self.ack_event = self.env.event()
                self.retries = 0
                continue

            if self.base == current_base:
                self.retries += 1

                if self.retries > self.max_retries:
                    print("[SIM] Número máximo de tentativas atingido.")
                    break

                self._retransmit_from_base()

        self.metrics.end_time = self.env.now
        self.finished = True

    def _send_window(self):
        while (
            self.next_seq_num < self.base + self.window_size
            and self.next_seq_num < self.total_packets
        ):
            packet_size = self._packet_size(self.next_seq_num)

            packet = create_data_packet(
                sequence_number=self.next_seq_num,
                size_bytes=packet_size,
                current_time=self.env.now
            )

            self.metrics.register_original_packet(packet.size_bytes)
            self.send_times[packet.sequence_number] = self.env.now

            self.network.send_data(packet)

            self.next_seq_num += 1

    def _retransmit_from_base(self):
        self.next_seq_num = self.base

        while (
            self.next_seq_num < self.base + self.window_size
            and self.next_seq_num < self.total_packets
        ):
            packet_size = self._packet_size(self.next_seq_num)

            packet = create_data_packet(
                sequence_number=self.next_seq_num,
                size_bytes=packet_size,
                current_time=self.env.now
            )

            self.metrics.register_retransmission(packet.size_bytes)
            self.send_times[packet.sequence_number] = self.env.now

            self.network.send_data(packet)

            self.next_seq_num += 1

    def receive_ack(self, ack_packet):
        ack_number = ack_packet.sequence_number

        self.metrics.register_ack_received()

        if ack_number in self.send_times:
            rtt = self.env.now - self.send_times[ack_number]
            self.metrics.register_rtt(rtt)

        if ack_number >= self.base:
            self.base = ack_number + 1

            if not self.ack_event.triggered:
                self.ack_event.succeed()

    def _packet_size(self, sequence_number: int) -> int:
        remaining_bytes = (
            self.file_size_bytes
            - sequence_number * self.chunk_size_bytes
        )

        return min(
            self.chunk_size_bytes,
            remaining_bytes
        )