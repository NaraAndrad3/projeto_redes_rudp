from dataclasses import dataclass, field


@dataclass
class SimulationMetrics:
    """
    Armazena as métricas coletadas durante uma execução da simulação.

    Esta classe substitui, no ambiente simulado, aquilo que na Fase 1
    era medido pela aplicação, pelo tcpdump e pelo tshark.
    """

    # Dados
    total_data_packets: int = 0
    original_data_packets: int = 0
    retransmitted_packets: int = 0

    # ACKs
    useful_data_bytes: int = 0
    data_bytes_sent: int = 0
    ack_bytes_sent: int = 0

    # Perdas
    data_packets_lost: int = 0
    ack_packets_lost: int = 0

    # Bytes
    data_bytes_sent: int = 0
    ack_bytes_sent: int = 0

    # Tempo
    start_time: float = 0.0
    end_time: float = 0.0

    # RTTs medidos a partir dos ACKs
    rtt_samples: list[float] = field(default_factory=list)

    def register_original_packet(self, size_bytes: int):
        self.original_data_packets += 1
        self.total_data_packets += 1
        self.useful_data_bytes += size_bytes
        self.data_bytes_sent += size_bytes

    def register_retransmission(self, size_bytes: int):
        """
        Registra uma retransmissão de pacote.
        """
        self.retransmitted_packets += 1
        self.total_data_packets += 1
        self.data_bytes_sent += size_bytes

    def register_ack_sent(self, size_bytes: int):
        """
        Registra o envio de um ACK.
        """
        self.ack_packets_sent += 1
        self.ack_bytes_sent += size_bytes

    def register_ack_received(self):
        """
        Registra um ACK recebido pelo emissor.
        """
        self.ack_packets_received += 1

    def register_data_loss(self):
        """
        Registra a perda de um pacote de dados.
        """
        self.data_packets_lost += 1

    def register_ack_loss(self):
        """
        Registra a perda de um ACK.
        """
        self.ack_packets_lost += 1

    def register_rtt(self, rtt: float):
        """
        Registra uma amostra de RTT.
        """
        self.rtt_samples.append(rtt)

    @property
    def total_bytes_sent(self) -> int:
        """
        Soma bytes de dados e ACKs.
        """
        return self.data_bytes_sent + self.ack_bytes_sent

    @property
    def duration(self) -> float:
        """
        Duração total da simulação.
        """
        return self.end_time - self.start_time

    @property
    def throughput_bps(self) -> float:
        """
        Throughput útil baseado apenas no tamanho original do arquivo.

        Essa métrica é equivalente ao throughput da aplicação na Fase 1.
        """
        if self.duration <= 0:
            return 0.0

        useful_bytes = self.original_data_packets

        return self.useful_data_bytes / self.duration

    @property
    def network_throughput_bps(self) -> float:
        """
        Throughput observado na rede, considerando dados + ACKs.
        """
        if self.duration <= 0:
            return 0.0

        return self.total_bytes_sent / self.duration

    @property
    def mean_rtt(self) -> float:
        """
        RTT médio medido na simulação.
        """
        if not self.rtt_samples:
            return 0.0

        return sum(self.rtt_samples) / len(self.rtt_samples)

    @property
    def efficiency_ratio(self) -> float:
        """
        Razão entre pacotes de dados originais e total de pacotes transmitidos.

        Essa métrica ajuda a avaliar eficiência: quanto mais próximo de 1,
        menor o impacto de ACKs e retransmissões.
        """
        total_packets = (
            self.total_data_packets
            + self.ack_packets_sent
        )

        if total_packets == 0:
            return 0.0

        return self.original_data_packets / total_packets

    def to_dict(self) -> dict:
        """
        Converte as métricas para dicionário, facilitando exportação para CSV.
        """
        return {
            "original_data_packets": self.original_data_packets,
            "total_data_packets": self.total_data_packets,
            "retransmitted_packets": self.retransmitted_packets,
            "ack_packets_sent": self.ack_packets_sent,
            "ack_packets_received": self.ack_packets_received,
            "data_packets_lost": self.data_packets_lost,
            "ack_packets_lost": self.ack_packets_lost,
            "data_bytes_sent": self.data_bytes_sent,
            "ack_bytes_sent": self.ack_bytes_sent,
            "total_bytes_sent": self.total_bytes_sent,
            "duration_s": self.duration,
            "throughput_bps": self.throughput_bps,
            "network_throughput_bps": self.network_throughput_bps,
            "mean_rtt_s": self.mean_rtt,
            "useful_data_bytes": self.useful_data_bytes,
            "efficiency_ratio": self.efficiency_ratio
        }