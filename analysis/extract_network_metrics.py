import csv
import re
import subprocess
from pathlib import Path


CAPTURES_DIR = Path("captures")
RESULTS_DIR = Path("results")
OUTPUT_FILE = RESULTS_DIR / "network_metrics_512kb.csv"


def run_tshark(pcap_file):
    pcap_path = str(pcap_file).replace("\\", "/")

    command = [
        "docker", "exec", "redes_server",
        "bash", "-lc",
        (
            f"tshark -r {pcap_path} "
            "-T fields "
            "-e frame.time_epoch "
            "-e frame.len"
        )
    ]

    result = subprocess.run(
        command,
        text=True,
        capture_output=True
    )

    if result.stderr:
        print(result.stderr)

    return result.stdout


def parse_filename(filename):
    pattern = r"(tcp|rudp)_scenario_([abc])_run_(\d+)\.pcap"
    match = re.match(pattern, filename)

    if not match:
        return None

    protocol = match.group(1).upper()
    scenario = match.group(2).upper()
    run = int(match.group(3))

    return protocol, scenario, run


def extract_metrics_from_output(output):
    times = []
    total_bytes = 0
    packet_count = 0

    for line in output.splitlines():
        parts = line.strip().split()

        if len(parts) < 2:
            continue

        try:
            timestamp = float(parts[0])
            frame_len = int(parts[1])
        except ValueError:
            continue

        times.append(timestamp)
        total_bytes += frame_len
        packet_count += 1

    if packet_count == 0:
        return 0, 0, 0.0, 0.0

    duration = max(times) - min(times)

    if duration <= 0:
        throughput = 0.0
    else:
        throughput = total_bytes / duration

    return packet_count, total_bytes, duration, throughput


def main():
    RESULTS_DIR.mkdir(exist_ok=True)

    rows = []

    for pcap_file in CAPTURES_DIR.glob("*.pcap"):
        parsed = parse_filename(pcap_file.name)

        if parsed is None:
            continue

        protocol, scenario, run = parsed

        print(f"Processando {pcap_file.name}...")

        output = run_tshark(str(pcap_file))

        packet_count, total_bytes, duration, throughput = (
            extract_metrics_from_output(output)
        )

        rows.append([
            run,
            scenario,
            protocol,
            str(pcap_file),
            packet_count,
            total_bytes,
            duration,
            throughput
        ])

    rows.sort(key=lambda x: (x[0], x[1], x[2]))

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "run",
            "scenario",
            "protocol",
            "pcap_file",
            "network_packet_count",
            "network_total_bytes",
            "network_duration_s",
            "network_throughput_bps"
        ])

        writer.writerows(rows)

    print(f"\nMétricas de rede salvas em: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()