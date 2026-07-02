import random
import simpy

from simulacao.config import (
    FILE_SIZE_BYTES,
    CHUNK_SIZE_BYTES,
    WINDOW_SIZE,
    TIMEOUT,
    MAX_RETRIES,
    SCENARIOS,
    RANDOM_SEED
)

from simulacao.metrics import SimulationMetrics
from simulacao.network import SimulatedNetwork
from simulacao.sender import Sender
from simulacao.receiver import Receiver


def run_simulation(
    scenario_name: str,
    seed: int | None = None,
    file_size_bytes: int | None = None,
    chunk_size_bytes: int | None = None,
    window_size: int | None = None,
    timeout: float | None = None,
    max_retries: int | None = None,
    delay_std_ms: float | None = None
):
    """
    Executa uma simulação completa do protocolo R-UDP.

    Todos os parâmetros podem ser sobrescritos, permitindo executar
    diferentes experimentos sem modificar o código-fonte.
    """

    # -----------------------------
    # Seed
    # -----------------------------

    if seed is None:
        random.seed(RANDOM_SEED)
    else:
        random.seed(seed)

    # -----------------------------
    # Cenário
    # -----------------------------

    scenario = SCENARIOS[scenario_name]

    delay_mean_ms = scenario["delay_ms"]
    loss_probability = scenario["loss_probability"]

    # -----------------------------
    # Parâmetros (default)
    # -----------------------------

    if file_size_bytes is None:
        file_size_bytes = FILE_SIZE_BYTES

    if chunk_size_bytes is None:
        chunk_size_bytes = CHUNK_SIZE_BYTES

    if window_size is None:
        window_size = WINDOW_SIZE

    if timeout is None:
        timeout = TIMEOUT

    if max_retries is None:
        max_retries = MAX_RETRIES

    if delay_std_ms is None:
        delay_std_ms = 0.0

    # -----------------------------
    # Ambiente SimPy
    # -----------------------------

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
        file_size_bytes=file_size_bytes,
        chunk_size_bytes=chunk_size_bytes,
        window_size=window_size,
        timeout=timeout,
        max_retries=max_retries
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

    env.process(sender.run())

    env.run()

    return metrics


def print_results(
    scenario_name: str,
    metrics: SimulationMetrics
):
    """
    Exibe um resumo das métricas da simulação.
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


def main():
    """
    Executa os três cenários básicos.
    """

    for scenario in ["A", "B", "C"]:

        metrics = run_simulation(
            scenario_name=scenario
        )

        print_results(
            scenario_name=scenario,
            metrics=metrics
        )

        print()


if __name__ == "__main__":
    main()