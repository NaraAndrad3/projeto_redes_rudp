import csv
import re
import subprocess
import time
from pathlib import Path


RESULTS_DIR = Path("results")
CAPTURES_DIR = Path("captures")

CONTAINER_CLIENT = "redes_client"
CONTAINER_SERVER = "redes_server"

TEST_FILE = "test_512kb.bin"
REPETITIONS = 5

OUTPUT_FILE = RESULTS_DIR / f"app_metrics_{TEST_FILE.replace('.bin', '')}.csv"

SCENARIOS = [
    {"scenario": "A", "delay_ms": 10, "loss_percent": 0},
    {"scenario": "B", "delay_ms": 50, "loss_percent": 10},
    {"scenario": "C", "delay_ms": 100, "loss_percent": 20},
]

PROTOCOLS = ["tcp", "rudp"]


def run_command(command, capture=True):
    result = subprocess.run(
        command,
        shell=True,
        text=True,
        capture_output=capture
    )

    return result


def docker_exec(container, command, capture=True):
    return run_command(
        f'docker exec {container} bash -lc "{command}"',
        capture=capture
    )


def ensure_dirs():
    RESULTS_DIR.mkdir(exist_ok=True)
    CAPTURES_DIR.mkdir(exist_ok=True)


def init_csv():
    if OUTPUT_FILE.exists():
        print(f"[INFO] Arquivo CSV já existe: {OUTPUT_FILE}")
        print("[INFO] Novas linhas serão adicionadas ao final.")
        return

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "run",
            "scenario",
            "protocol",
            "file",
            "delay_ms",
            "loss_percent",
            "status",
            "bytes_expected",
            "bytes_received",
            "delivery_rate",
            "elapsed_time_s",
            "throughput_bps",
            "retransmissions",
            "pcap_file",
            "network_csv_file"
        ])


def append_metrics(row):
    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(row)


def kill_old_processes():
    docker_exec(
        CONTAINER_SERVER,
        "pkill -f 'python3 -m src.server.tcp_server' || true"
    )
    docker_exec(
        CONTAINER_SERVER,
        "pkill -f 'python3 -m src.server.rudp_server' || true"
    )
    docker_exec(
        CONTAINER_SERVER,
        "pkill tcpdump || true"
    )
    time.sleep(1)


def apply_tc(delay_ms, loss_percent):
    docker_exec(
        CONTAINER_CLIENT,
        "tc qdisc del dev eth0 root 2>/dev/null || true"
    )

    docker_exec(
        CONTAINER_CLIENT,
        f"tc qdisc add dev eth0 root netem delay {delay_ms}ms loss {loss_percent}%"
    )

    result = docker_exec(
        CONTAINER_CLIENT,
        "tc qdisc show dev eth0"
    )

    print("[TC]")
    print(result.stdout)


def clear_tc():
    docker_exec(
        CONTAINER_CLIENT,
        "tc qdisc del dev eth0 root 2>/dev/null || true"
    )


def start_tcpdump(pcap_file):
    return subprocess.Popen(
        f'docker exec {CONTAINER_SERVER} bash -lc "tcpdump -i eth0 -w {pcap_file}"',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )


def stop_tcpdump():
    docker_exec(
        CONTAINER_SERVER,
        "pkill tcpdump || true"
    )

    time.sleep(1)


def export_pcap_to_csv(pcap_file, csv_file):
    docker_exec(
        CONTAINER_SERVER,
        f"""
        tshark \
        -r {pcap_file} \
        -T fields \
        -e frame.time_epoch \
        -e ip.src \
        -e ip.dst \
        -e tcp.srcport \
        -e tcp.dstport \
        -e udp.srcport \
        -e udp.dstport \
        -e frame.len \
        -E header=y \
        -E separator=, \
        > {csv_file}
        """
    )


def run_server(protocol):
    if protocol == "tcp":
        command = "python3 -m src.server.tcp_server"
    else:
        command = "python3 -m src.server.rudp_server"

    return subprocess.Popen(
        f'docker exec {CONTAINER_SERVER} bash -lc "{command}"',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )


def run_client(protocol):
    if protocol == "tcp":
        command = f"python3 -m src.client.tcp_client {TEST_FILE}"
    else:
        command = f"python3 -m src.client.rudp_client {TEST_FILE}"

    result = docker_exec(
        CONTAINER_CLIENT,
        command
    )

    output = ""

    if result.stdout:
        output += result.stdout

    if result.stderr:
        output += result.stderr

    return output


def extract_metric(pattern, text, default=None, cast=float):
    match = re.search(pattern, text)

    if not match:
        return default

    value = match.group(1).replace(",", ".")

    return cast(value)


def extract_client_metrics(protocol, output):
    bytes_expected = extract_metric(
        r"Bytes.*?enviados:\s*(\d+)",
        output,
        default=0,
        cast=int
    )

    elapsed_time = extract_metric(
        r"Tempo total:\s*([\d.]+)",
        output,
        default=0.0,
        cast=float
    )

    throughput = extract_metric(
        r"Throughput.*?:\s*([\d.]+)",
        output,
        default=0.0,
        cast=float
    )

    if protocol == "rudp":
        retransmissions = extract_metric(
            r"Retransmiss.*?:\s*(\d+)",
            output,
            default=0,
            cast=int
        )
    else:
        retransmissions = ""

    max_retries_hit = (
        "máximo de tentativas" in output
        or "mÃ¡ximo de tentativas" in output
        or "maximo de tentativas" in output
    )

    return (
        bytes_expected,
        elapsed_time,
        throughput,
        retransmissions,
        max_retries_hit
    )


def get_received_bytes(protocol, filename):
    if protocol == "tcp":
        received_file = f"data/output/received_tcp_{filename}"
    else:
        received_file = f"data/output/received_rudp_{filename}"

    result = docker_exec(
        CONTAINER_SERVER,
        f"wc -c {received_file} 2>/dev/null | awk '{{print $1}}'"
    )

    output = result.stdout.strip()

    if not output:
        return 0

    return int(output)


def clean_output_files(filename):
    docker_exec(
        CONTAINER_SERVER,
        f"rm -f data/output/received_tcp_{filename}"
    )

    docker_exec(
        CONTAINER_SERVER,
        f"rm -f data/output/received_rudp_{filename}"
    )


def calculate_delivery_rate(bytes_expected, bytes_received):
    if bytes_expected == 0:
        return 0.0

    return bytes_received / bytes_expected


def classify_status(bytes_expected, bytes_received, max_retries_hit):
    if bytes_expected > 0 and bytes_received == bytes_expected and not max_retries_hit:
        return "success"

    if bytes_received > 0:
        return "partial_failure"

    return "failure"


def sanitize_metrics_for_failure(status, elapsed_time, throughput):
    if status == "failure":
        return "", ""

    return elapsed_time, throughput


def run_single_test(run_id, scenario, protocol):
    scenario_name = scenario["scenario"]
    delay_ms = scenario["delay_ms"]
    loss_percent = scenario["loss_percent"]

    pcap_file = (
        f"captures/{protocol}_scenario_{scenario_name.lower()}_run_{run_id}.pcap"
    )

    network_csv_file = (
        f"captures/{protocol}_scenario_{scenario_name.lower()}_run_{run_id}.csv"
    )

    print("=" * 70)
    print(f"Run {run_id} | Cenário {scenario_name} | {protocol.upper()}")
    print(f"Arquivo: {TEST_FILE}")
    print(f"Delay={delay_ms}ms | Loss={loss_percent}%")
    print("=" * 70)

    kill_old_processes()
    clean_output_files(TEST_FILE)

    apply_tc(delay_ms, loss_percent)

    docker_exec(
        CONTAINER_SERVER,
        f"rm -f {pcap_file} {network_csv_file}"
    )

    start_tcpdump(pcap_file)
    time.sleep(1)

    run_server(protocol)
    time.sleep(2)

    client_output = run_client(protocol)

    print("[CLIENT OUTPUT]")
    print(client_output)

    time.sleep(6)

    stop_tcpdump()
    export_pcap_to_csv(pcap_file, network_csv_file)

    (
        bytes_expected,
        elapsed_time,
        throughput,
        retransmissions,
        max_retries_hit
    ) = extract_client_metrics(protocol, client_output)

    bytes_received = get_received_bytes(protocol, TEST_FILE)

    delivery_rate = calculate_delivery_rate(
        bytes_expected,
        bytes_received
    )

    status = classify_status(
        bytes_expected,
        bytes_received,
        max_retries_hit
    )

    elapsed_time, throughput = sanitize_metrics_for_failure(
        status,
        elapsed_time,
        throughput
    )

    append_metrics([
        run_id,
        scenario_name,
        protocol.upper(),
        TEST_FILE,
        delay_ms,
        loss_percent,
        status,
        bytes_expected,
        bytes_received,
        round(delivery_rate, 4),
        elapsed_time,
        throughput,
        retransmissions,
        pcap_file,
        network_csv_file
    ])

    clear_tc()

    print(f"Status: {status}")
    print(f"Bytes esperados: {bytes_expected}")
    print(f"Bytes recebidos: {bytes_received}")
    print(f"Taxa de entrega: {delivery_rate:.2%}")
    print(f"PCAP: {pcap_file}")
    print(f"CSV rede: {network_csv_file}")


def main():
    ensure_dirs()
    init_csv()

    try:
        for run_id in range(1, REPETITIONS + 1):
            for scenario in SCENARIOS:
                for protocol in PROTOCOLS:
                    run_single_test(
                        run_id,
                        scenario,
                        protocol
                    )

    finally:
        clear_tc()
        kill_old_processes()

    print("\nTodos os testes foram finalizados.")
    print(f"Métricas salvas em: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()