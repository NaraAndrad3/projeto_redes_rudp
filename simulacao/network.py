import random
import simpy


class SimulatedNetwork:
    """
    Representa a rede simulada.

    Aplica atraso, jitter e perda de pacotes.
    Também preserva a ordem de entrega dentro de cada direção:
    - DATA: emissor -> receptor
    - ACK: receptor -> emissor
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

        # Controlam o próximo instante possível de entrega em cada direção.
        self.next_data_delivery_time = 0.0
        self.next_ack_delivery_time = 0.0

    def connect(self, sender, receiver):
        self.sender = sender
        self.receiver = receiver

    def sample_delay(self) -> float:
        delay_ms = random.normalvariate(
            self.delay_mean_ms,
            self.delay_std_ms
        )

        delay_ms = max(0.0, delay_ms)

        return delay_ms / 1000.0

    def is_lost(self) -> bool:
        return random.random() < self.loss_probability

    def send_data(self, packet):
        return self.env.process(
            self._deliver_data(packet)
        )

    def send_ack(self, packet):
        return self.env.process(
            self._deliver_ack(packet)
        )

    def _deliver_data(self, packet):
        if self.is_lost():
            self.metrics.register_data_loss()
            return

        delay = self.sample_delay()

        planned_delivery_time = self.env.now + delay

        delivery_time = max(
            planned_delivery_time,
            self.next_data_delivery_time
        )

        self.next_data_delivery_time = delivery_time

        yield self.env.timeout(
            delivery_time - self.env.now
        )

        self.receiver.receive(packet)

    def _deliver_ack(self, packet):
        if self.is_lost():
            self.metrics.register_ack_loss()
            return

        delay = self.sample_delay()

        planned_delivery_time = self.env.now + delay

        delivery_time = max(
            planned_delivery_time,
            self.next_ack_delivery_time
        )

        self.next_ack_delivery_time = delivery_time

        yield self.env.timeout(
            delivery_time - self.env.now
        )

        self.sender.receive_ack(packet)