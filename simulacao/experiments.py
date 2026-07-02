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
    RANDOM_SEED
)

from simulacao.main import run_simulation


RESULTS_DIR = Path("results/simulation")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def save_rows(output_file: Path, header: list[str], rows: list[list]):
    """
    Salva uma lista de linhas em um arquivo CSV.
    """

    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)


def metrics_to_row(
    experiment_name: str,
    run_id: int,
    scenario_name: str,
    file_size_bytes: int,
    chunk_size_bytes: int,
    window_size: int,
    timeout: float,
    max_retries: int,
    delay_std_ms: float,
    metrics
):
    """
    Converte as métricas de uma simulação em uma linha de CSV.
    """

    scenario = SCENARIOS[scenario_name]

    return [
        experiment_name,
        run_id,
        scenario_name,
        file_size_bytes,
        chunk_size_bytes,
        window_size,
        timeout,
        max_retries,
        scenario["delay_ms"],
        delay_std_ms,
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


CSV_HEADER = [
    "experiment",
    "run",
    "scenario",
    "file_size_bytes",
    "chunk_size_bytes",
    "window_size",
    "timeout_s",
    "max_retries",
    "delay_mean_ms",
    "delay_std_ms",
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
]


def run_validation_experiment(repetitions: int = 30):
    """
    Executa o experimento base de validação.

    Este experimento corresponde aos cenários A, B e C da Fase 1,
    usando os mesmos parâmetros principais do R-UDP real.
    """

    rows = []

    for run_id in range(1, repetitions + 1):
        for scenario_name in SCENARIOS.keys():
            seed = RANDOM_SEED + run_id * 100 + ord(scenario_name)

            random.seed(seed)

            metrics = run_simulation(
                scenario_name=scenario_name,
                seed=seed,
                file_size_bytes=FILE_SIZE_BYTES,
                chunk_size_bytes=CHUNK_SIZE_BYTES,
                window_size=WINDOW_SIZE,
                timeout=TIMEOUT,
                max_retries=MAX_RETRIES,
                delay_std_ms=0.0
            )

            rows.append(
                metrics_to_row(
                    experiment_name="validation",
                    run_id=run_id,
                    scenario_name=scenario_name,
                    file_size_bytes=FILE_SIZE_BYTES,
                    chunk_size_bytes=CHUNK_SIZE_BYTES,
                    window_size=WINDOW_SIZE,
                    timeout=TIMEOUT,
                    max_retries=MAX_RETRIES,
                    delay_std_ms=0.0,
                    metrics=metrics
                )
            )

            print(
                f"[validation] run={run_id} "
                f"scenario={scenario_name} "
                f"duration={metrics.duration:.4f}s "
                f"throughput={metrics.throughput_bps:.2f} "
                f"retrans={metrics.retransmitted_packets}"
            )

    output_file = RESULTS_DIR / "validation_metrics.csv"

    save_rows(
        output_file=output_file,
        header=CSV_HEADER,
        rows=rows
    )

    print(f"\nArquivo salvo em: {output_file}")

def run_jitter_experiment(repetitions: int = 30):
    """
    Executa o experimento de impacto do jitter.

    O objetivo é avaliar como a variação da latência influencia:
    - tempo de transferência;
    - throughput;
    - RTT médio;
    - retransmissões.

    Neste experimento, mantemos os cenários A, B e C,
    mas variamos o desvio padrão do atraso.
    """

    jitter_values_ms = [0, 0.5, 1, 1.5, 2]

    rows = []

    for delay_std_ms in jitter_values_ms:
        for run_id in range(1, repetitions + 1):
            for scenario_name in SCENARIOS.keys():
                seed = (
                    RANDOM_SEED
                    + run_id * 100
                    + ord(scenario_name)
                    + int(delay_std_ms * 10)
                )

                random.seed(seed)

                metrics = run_simulation(
                    scenario_name=scenario_name,
                    seed=seed,
                    file_size_bytes=FILE_SIZE_BYTES,
                    chunk_size_bytes=CHUNK_SIZE_BYTES,
                    window_size=WINDOW_SIZE,
                    timeout=TIMEOUT,
                    max_retries=MAX_RETRIES,
                    delay_std_ms=delay_std_ms
                )

                rows.append(
                    metrics_to_row(
                        experiment_name="jitter",
                        run_id=run_id,
                        scenario_name=scenario_name,
                        file_size_bytes=FILE_SIZE_BYTES,
                        chunk_size_bytes=CHUNK_SIZE_BYTES,
                        window_size=WINDOW_SIZE,
                        timeout=TIMEOUT,
                        max_retries=MAX_RETRIES,
                        delay_std_ms=delay_std_ms,
                        metrics=metrics
                    )
                )

                print(
                    f"[jitter] std={delay_std_ms}ms "
                    f"run={run_id} "
                    f"scenario={scenario_name} "
                    f"duration={metrics.duration:.4f}s "
                    f"rtt={metrics.mean_rtt:.4f}s "
                    f"retrans={metrics.retransmitted_packets}"
                )

    output_file = RESULTS_DIR / "jitter_metrics.csv"

    save_rows(
        output_file=output_file,
        header=CSV_HEADER,
        rows=rows
    )

    print(f"\nArquivo salvo em: {output_file}")

def run_window_experiment(repetitions: int = 30):
    """
    Executa o experimento de sensibilidade ao tamanho da janela.

    O objetivo é avaliar como diferentes valores de WINDOW_SIZE
    afetam o desempenho do Go-Back-N.
    """

    window_values = [1, 2, 4, 8, 16, 32]

    rows = []

    for window_size in window_values:
        for run_id in range(1, repetitions + 1):
            for scenario_name in SCENARIOS.keys():
                seed = (
                    RANDOM_SEED
                    + run_id * 100
                    + ord(scenario_name)
                    + window_size * 1000
                )

                random.seed(seed)

                metrics = run_simulation(
                    scenario_name=scenario_name,
                    seed=seed,
                    file_size_bytes=FILE_SIZE_BYTES,
                    chunk_size_bytes=CHUNK_SIZE_BYTES,
                    window_size=window_size,
                    timeout=TIMEOUT,
                    max_retries=MAX_RETRIES,
                    delay_std_ms=0.0
                )

                rows.append(
                    metrics_to_row(
                        experiment_name="window_sensitivity",
                        run_id=run_id,
                        scenario_name=scenario_name,
                        file_size_bytes=FILE_SIZE_BYTES,
                        chunk_size_bytes=CHUNK_SIZE_BYTES,
                        window_size=window_size,
                        timeout=TIMEOUT,
                        max_retries=MAX_RETRIES,
                        delay_std_ms=0.0,
                        metrics=metrics
                    )
                )

                print(
                    f"[window] window={window_size} "
                    f"run={run_id} "
                    f"scenario={scenario_name} "
                    f"duration={metrics.duration:.4f}s "
                    f"throughput={metrics.throughput_bps:.2f} "
                    f"retrans={metrics.retransmitted_packets}"
                )

    output_file = RESULTS_DIR / "window_metrics.csv"

    save_rows(
        output_file=output_file,
        header=CSV_HEADER,
        rows=rows
    )

    print(f"\nArquivo salvo em: {output_file}")

def run_file_size_experiment(repetitions: int = 30):
    """
    Executa o experimento de curva de vazão por tamanho de arquivo.

    O objetivo é avaliar como o tamanho do arquivo influencia:
    - duração da transferência;
    - throughput;
    - retransmissões;
    - overhead.

    Este experimento atende à tarefa de analisar vazão com arquivos
    de diferentes tamanhos no simulador.
    """

    file_sizes = [
        1 * 1024 * 1024,      # 1 MB
        5 * 1024 * 1024,      # 5 MB
        10 * 1024 * 1024,     # 10 MB
        50 * 1024 * 1024,     # 50 MB
        100 * 1024 * 1024     # 100 MB
    ]

    rows = []

    for file_size_bytes in file_sizes:
        file_size_mb = file_size_bytes / (1024 * 1024)

        for run_id in range(1, repetitions + 1):
            for scenario_name in SCENARIOS.keys():
                seed = (
                    RANDOM_SEED
                    + run_id * 100
                    + ord(scenario_name)
                    + int(file_size_mb * 1000)
                )

                random.seed(seed)

                metrics = run_simulation(
                    scenario_name=scenario_name,
                    seed=seed,
                    file_size_bytes=file_size_bytes,
                    chunk_size_bytes=CHUNK_SIZE_BYTES,
                    window_size=WINDOW_SIZE,
                    timeout=TIMEOUT,
                    max_retries=MAX_RETRIES,
                    delay_std_ms=0.0
                )

                rows.append(
                    metrics_to_row(
                        experiment_name="file_size_curve",
                        run_id=run_id,
                        scenario_name=scenario_name,
                        file_size_bytes=file_size_bytes,
                        chunk_size_bytes=CHUNK_SIZE_BYTES,
                        window_size=WINDOW_SIZE,
                        timeout=TIMEOUT,
                        max_retries=MAX_RETRIES,
                        delay_std_ms=0.0,
                        metrics=metrics
                    )
                )

                print(
                    f"[file_size] size={file_size_mb:.0f}MB "
                    f"run={run_id} "
                    f"scenario={scenario_name} "
                    f"duration={metrics.duration:.2f}s "
                    f"throughput={metrics.throughput_bps:.2f} "
                    f"retrans={metrics.retransmitted_packets}"
                )

    output_file = RESULTS_DIR / "file_size_metrics.csv"

    save_rows(
        output_file=output_file,
        header=CSV_HEADER,
        rows=rows
    )

    print(f"\nArquivo salvo em: {output_file}")

def run_stress_experiment(repetitions: int = 30):
    """
    Executa o cenário de estresse.

    O objetivo é prever o comportamento do protocolo R-UDP
    com uma taxa de perda superior aos cenários da Fase 1.

    Cenário de estresse:
    - delay médio: 100 ms
    - perda: 25%
    """

    stress_scenario = {
        "scenario": "STRESS",
        "delay_ms": 100,
        "loss_probability": 0.25
    }

    rows = []

    for run_id in range(1, repetitions + 1):
        seed = RANDOM_SEED + run_id * 100 + 999

        random.seed(seed)

        # Criamos um cenário temporário sem alterar o config.py.
        SCENARIOS["STRESS"] = {
            "delay_ms": stress_scenario["delay_ms"],
            "loss_probability": stress_scenario["loss_probability"]
        }

        metrics = run_simulation(
            scenario_name="STRESS",
            seed=seed,
            file_size_bytes=FILE_SIZE_BYTES,
            chunk_size_bytes=CHUNK_SIZE_BYTES,
            window_size=WINDOW_SIZE,
            timeout=TIMEOUT,
            max_retries=MAX_RETRIES,
            delay_std_ms=0.0
        )

        rows.append(
            metrics_to_row(
                experiment_name="stress_25_loss",
                run_id=run_id,
                scenario_name="STRESS",
                file_size_bytes=FILE_SIZE_BYTES,
                chunk_size_bytes=CHUNK_SIZE_BYTES,
                window_size=WINDOW_SIZE,
                timeout=TIMEOUT,
                max_retries=MAX_RETRIES,
                delay_std_ms=0.0,
                metrics=metrics
            )
        )

        print(
            f"[stress] run={run_id} "
            f"duration={metrics.duration:.4f}s "
            f"throughput={metrics.throughput_bps:.2f} "
            f"retrans={metrics.retransmitted_packets} "
            f"loss_data={metrics.data_packets_lost} "
            f"loss_ack={metrics.ack_packets_lost}"
        )

    output_file = RESULTS_DIR / "stress_metrics.csv"

    save_rows(
        output_file=output_file,
        header=CSV_HEADER,
        rows=rows
    )

    print(f"\nArquivo salvo em: {output_file}")


if __name__ == "__main__":
    #run_jitter_experiment()
    #run_window_experiment()
    #run_file_size_experiment()
    run_stress_experiment()