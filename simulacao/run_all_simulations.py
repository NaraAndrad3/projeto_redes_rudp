import csv
import random
from pathlib import Path

from simulacao.config import (
    SCENARIOS,
    FILE_SIZE_BYTES,
    CHUNK_SIZE_BYTES,
    WINDOW_SIZE,
    TIMEOUT,
    MAX_RETRIES,
    REPETITIONS,
    RANDOM_SEED
)

from simulacao.main import run_simulation


RESULTS_DIR = Path("results")
OUTPUT_FILE = RESULTS_DIR / "simulation_metrics_512kb.csv"


def ensure_dirs():
    RESULTS_DIR.mkdir(exist_ok=True)


def init_csv():
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "run",
            "scenario",
            "file_size_bytes",
            "chunk_size_bytes",
            "window_size",
            "timeout_s",
            "max_retries",
            "delay_ms",
            "loss_probability",
            "original_data_packets",
            "total_data_packets",
            "retransmitted_packets",
            "ack_packets_sent",
            "ack_packets_received",
            "data_packets_lost",
            "ack_packets_lost",
            "useful_data_bytes",
            "data_bytes_sent",
            "ack_bytes_sent",
            "total_bytes_sent",
            "duration_s",
            "throughput_bps",
            "network_throughput_bps",
            "mean_rtt_s",
            "efficiency_ratio"
        ])


def append_row(run_id, scenario_name, scenario, metrics):
    row = [
        run_id,
        scenario_name,
        FILE_SIZE_BYTES,
        CHUNK_SIZE_BYTES,
        WINDOW_SIZE,
        TIMEOUT,
        MAX_RETRIES,
        scenario["delay_ms"],
        scenario["loss_probability"],
        metrics.original_data_packets,
        metrics.total_data_packets,
        metrics.retransmitted_packets,
        metrics.ack_packets_sent,
        metrics.ack_packets_received,
        metrics.data_packets_lost,
        metrics.ack_packets_lost,
        metrics.useful_data_bytes,
        metrics.data_bytes_sent,
        metrics.ack_bytes_sent,
        metrics.total_bytes_sent,
        metrics.duration,
        metrics.throughput_bps,
        metrics.network_throughput_bps,
        metrics.mean_rtt,
        metrics.efficiency_ratio
    ]

    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(row)


def main():
    ensure_dirs()
    init_csv()

    for run_id in range(1, REPETITIONS + 1):
        for scenario_name, scenario in SCENARIOS.items():
            seed = RANDOM_SEED + run_id * 100 + ord(scenario_name)
            random.seed(seed)

            print("=" * 60)
            print(f"Simulação {run_id} | Cenário {scenario_name}")
            print("=" * 60)

            metrics = run_simulation(
                scenario_name=scenario_name,
                seed=seed
            )

            append_row(
                run_id=run_id,
                scenario_name=scenario_name,
                scenario=scenario,
                metrics=metrics
            )

            print(
                f"Tempo: {metrics.duration:.4f}s | "
                f"Throughput: {metrics.throughput_bps:.2f} B/s | "
                f"Retransmissões: {metrics.retransmitted_packets}"
            )

    print("\nTodas as simulações foram concluídas.")
    print(f"Resultados salvos em: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()