import argparse
import subprocess
import time


def run(command: list[str], wait: bool = True):
    print(f"\n[RUN] {' '.join(command)}")

    if wait:
        result = subprocess.run(
            command,
            text=True,
            capture_output=True
        )

        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print(result.stderr)

        return result

    return subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )


def docker_exec(container: str, command: str, wait: bool = True):
    return run(
        ["docker", "exec", container, "bash", "-lc", command],
        wait=wait
    )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("scenario", help="Exemplo: A, B ou C")
    parser.add_argument("protocol", choices=["tcp", "rudp"])
    parser.add_argument("delay", type=int, help="Delay em ms")
    parser.add_argument("loss", type=int, help="Perda em porcentagem")

    args = parser.parse_args()

    scenario = args.scenario.lower()
    protocol = args.protocol
    delay = args.delay
    loss = args.loss

    pcap_file = f"captures/{protocol}_scenario_{scenario}.pcap"
    csv_file = f"captures/{protocol}_scenario_{scenario}.csv"

    print("=" * 60)
    print(f"Cenário {args.scenario.upper()} - {protocol.upper()}")
    print(f"Delay: {delay} ms | Perda: {loss}%")
    print("=" * 60)

    docker_exec("redes_client", "tc qdisc del dev eth0 root 2>/dev/null || true")
    docker_exec(
        "redes_client",
        f"tc qdisc add dev eth0 root netem delay {delay}ms loss {loss}%"
    )
    docker_exec("redes_client", "tc qdisc show dev eth0")

    docker_exec("redes_server", f"rm -f {pcap_file} {csv_file}")

    tcpdump_process = docker_exec(
        "redes_server",
        f"tcpdump -i eth0 -w {pcap_file}",
        wait=False
    )

    time.sleep(1)

    if protocol == "tcp":
        server_command = "python3 -m src.server.tcp_server"
        client_command = "python3 -m src.client.tcp_client"
    else:
        server_command = "python3 -m src.server.rudp_server"
        client_command = "python3 -m src.client.rudp_client"

    server_process = docker_exec(
        "redes_server",
        server_command,
        wait=False
    )

    time.sleep(1)

    client_result = docker_exec(
        "redes_client",
        client_command,
        wait=True
    )

    time.sleep(1)

    docker_exec("redes_server", "pkill tcpdump || true")

    time.sleep(1)

    docker_exec(
        "redes_server",
        f"""
        tshark \
        -r {pcap_file} \
        -T fields \
        -e frame.time \
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

    docker_exec("redes_client", "tc qdisc del dev eth0 root 2>/dev/null || true")
    docker_exec("redes_client", "tc qdisc show dev eth0")

    print("=" * 60)
    print("Teste finalizado.")
    print(f"PCAP: {pcap_file}")
    print(f"CSV:  {csv_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()