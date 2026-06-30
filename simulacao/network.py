import random
import simpy

from simulation.packet import (
    PACKET_TYPE_DATA,
    PACKET_TYPE_ACK
)


class SimulatedNetwork:
    """
    Representa a rede simulada.

    Este componente é responsável por aplicar:
    - atraso;
    - jitter;
    - perda de pacotes;
    - entrega de pacotes DATA ao receptor;
    - entrega de pacotes ACK ao emissor.
    """

    def __init__(
        self,
        env: simpy.Environment,
        delay_mean_ms: float,
        delay_std_ms: float,
        loss_probability: float,
        metrics
    ):
        self.env = env
        self.delay_mean_ms = delay_mean_ms
        self.delay_std_ms = delay_std_ms
        self.loss_probability = loss_probability
        self.metrics = metrics

        self.sender = None
        self.receiver = None

    def connect(self, sender, receiver):
        """
        Conecta emissor e receptor à rede simulada.
        """
        self.sender = sender
        self.receiver = receiver

    def sample_delay(self) -> float:
        """
        Gera uma amostra de atraso em segundos.

        O atraso segue uma distribuição normal.
        Caso o valor sorteado seja negativo, ele é limitado a zero.
        """

        delay_ms = random.normalvariate(
            self.delay_mean_ms,
            self.delay_std_ms
        )

        delay_ms = max(0.0, delay_ms)

        return delay_ms / 1000.0

    def is_lost(self) -> bool:
        """
        Decide se um pacote será perdido.

        A perda segue um modelo de Bernoulli:
        - sorteia um número entre 0 e 1;
        - se esse número for menor que a probabilidade de perda,
          o pacote é descartado.
        """

        return random.random() < self.loss_probability

    def send_data(self, packet):
        """
        Envia um pacote DATA do emissor para o receptor.
        """
        return self.env.process(
            self._deliver_data(packet)
        )

    def send_ack(self, packet):
        """
        Envia um pacote ACK do receptor para o emissor.
        """
        return self.env.process(
            self._deliver_ack(packet)
        )

    def _deliver_data(self, packet):
        """
        Processo SimPy responsável por entregar um pacote de dados.
        """

        if self.is_lost():
            self.metrics.register_data_loss()
            return

        delay = self.sample_delay()

        yield self.env.timeout(delay)

        self.receiver.receive(packet)

    def _deliver_ack(self, packet):
        """
        Processo SimPy responsável por entregar um ACK.
        """

        if self.is_lost():
            self.metrics.register_ack_loss()
            return

        delay = self.sample_delay()

        yield self.env.timeout(delay)

        self.sender.receive_ack(packet)