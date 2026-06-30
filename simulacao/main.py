import random
import simpy

from simulation.config import (
    FILE_SIZE_BYTES,
    SCENARIOS,
    RANDOM_SEED
)

from simulation.metrics import SimulationMetrics
from simulation.network import SimulatedNetwork
from simulation.sender import Sender
from simulation.receiver import Receiver


def run_simulation(scenario_name: str):
    """
    Executa uma simulação para um cenário específico.
    """

    random.seed(RANDOM_SEED)

    scenario = SCENARIOS[scenario_name]

    delay_mean_ms = scenario["delay_ms"]
    delay_std_ms = delay_mean_ms * 0.10
    loss_probability = scenario["loss_probability"]

    env = simpy.Environment()

    metrics = SimulationMetrics()

    network = SimulatedNetwork(
        env=env,
        delay_mean_ms=delay_mean_ms,
        delay_std_ms=delay_std_ms,
        loss_probability=loss_probability,
        metrics=metrics
    )

    sender = Sender(
        env=env,
        network=network,
        metrics=metrics,
        file_size_bytes=FILE_SIZE_BYTES
    )

    receiver = Receiver(
        env=env,
        network=network,
        metrics=metrics
    )

    network.connect(
        sender=sender,
        receiver=receiver
    )

    env.process(
        sender.run()
    )

    env.run()

    return metrics


def print_results(scenario_name: str, metrics: SimulationMetrics):
    """
    Exibe as principais métricas da simulação.
    """

    print("=" * 60)
    print(f"Simulação R-UDP - Cenário {scenario_name}")
    print("=" * 60)

    print(f"Pacotes originais: {metrics.original_data_packets}")
    print(f"Total de pacotes DATA enviados: {metrics.total_data_packets}")
    print(f"Retransmissões: {metrics.retransmitted_packets}")

    print(f"ACKs enviados: {metrics.ack_packets_sent}")
    print(f"ACKs recebidos: {metrics.ack_packets_received}")

    print(f"Pacotes DATA perdidos: {metrics.data_packets_lost}")
    print(f"ACKs perdidos: {metrics.ack_packets_lost}")

    print(f"Bytes úteis: {metrics.useful_data_bytes}")
    print(f"Bytes DATA enviados: {metrics.data_bytes_sent}")
    print(f"Bytes ACK enviados: {metrics.ack_bytes_sent}")
    print(f"Bytes totais simulados: {metrics.total_bytes_sent}")

    print(f"Duração simulada: {metrics.duration:.4f} s")
    print(f"Throughput útil: {metrics.throughput_bps:.2f} B/s")
    print(f"Throughput da rede: {metrics.network_throughput_bps:.2f} B/s")
    print(f"RTT médio: {metrics.mean_rtt:.4f} s")
    print(f"Eficiência: {metrics.efficiency_ratio:.4f}")


if __name__ == "__main__":
    metrics = run_simulation("A")
    print_results("A", metrics)