# Projeto de Redes de Computadores - PPGCC/UFPI

## Descrição

Projeto desenvolvido para a disciplina de Redes de Computadores do Programa de Pós-Graduação em Ciência da Computação (PPGCC) da Universidade Federal do Piauí (UFPI).

O objetivo do projeto é implementar, testar e analisar experimentalmente dois mecanismos de transferência de arquivos:

* TCP (Transmission Control Protocol);
* R-UDP (Reliable UDP), implementado em nível de aplicação utilizando UDP.

Além da implementação dos protocolos, foram realizados experimentos controlados utilizando Docker, simulação de condições de rede adversas com NetEm (`tc`), captura de tráfego com `tcpdump`, análise de pacotes com `tshark` e geração de métricas estatísticas para comparação de desempenho.

---

# Status do Projeto

## Fase 1 - Implementação Experimental

✅ Transferência de arquivos via TCP

✅ Transferência de arquivos via R-UDP

✅ Checksum para validação de integridade

✅ Numeração de sequência

✅ ACKs cumulativos

✅ Timeout e retransmissão

✅ Janela deslizante (Go-Back-N)

✅ Simulação de atraso e perda de pacotes

✅ Captura de tráfego utilizando tcpdump

✅ Extração de métricas com tshark

✅ Análise estatística dos resultados

✅ Relatório experimental concluído

## Fase 2 - Modelagem Estocástica

🚧 Em desenvolvimento

* Simulação utilizando SimPy
* Modelagem do sistema de transmissão
* Validação dos resultados experimentais
* Comparação entre modelo e implementação real

---

# Objetivos

## Fase 1 - Implementação Real

* Implementar transferência de arquivos utilizando TCP.
* Implementar transferência de arquivos utilizando R-UDP.
* Desenvolver mecanismos de confiabilidade em nível de aplicação.
* Simular diferentes condições de rede.
* Capturar e analisar o tráfego gerado.
* Comparar métricas da aplicação com métricas observadas na rede.

## Fase 2 - Modelagem Estocástica

* Desenvolver um simulador utilizando SimPy.
* Modelar os protocolos implementados.
* Validar o simulador utilizando os dados experimentais.
* Comparar os resultados simulados e reais.

---

# Tecnologias Utilizadas

* Python 3
* Docker
* Docker Compose
* Ubuntu Linux
* Sockets TCP
* Sockets UDP
* NetEm (`tc`)
* tcpdump
* tshark (Wireshark)
* Pandas
* Plotly
* SimPy
* Jupyter Notebook / Google Colab
* Git e GitHub

---

# Estrutura do Projeto

```text
projeto-redes-rudp/
│
├── src/
│   ├── client/
│   ├── server/
│   └── common/
│
├── docker/
│
├── scripts/
│
├── data/
│   ├── input/
│   └── output/
│
│
├── captures/
│
├── analysis/
│
├── report/
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

# Arquitetura Geral

```text
Cliente
   │
   ▼
TCP ou R-UDP
   │
   ▼
Servidor
   │
   ▼
Arquivo Recebido

          +
          │
          ▼

tcpdump → PCAP → CSV → Análise Estatística → Gráficos
```

---

# Pré-requisitos

Antes de executar o projeto, certifique-se de possuir instalado:

* Python 3.10 ou superior
* Docker
* Docker Compose
* Git
* tcpdump
* tshark (Wireshark)

Verifique as versões instaladas:

```bash
python --version
docker --version
docker compose version
tshark -v
```

---

# Instalação

Clone o repositório:

```bash
git clone <URL_DO_REPOSITORIO>
cd projeto-redes-rudp
```

Crie um ambiente virtual:

```bash
python -m venv .venv
```

Ative o ambiente:

### Linux

```bash
source .venv/bin/activate
```

### Windows (PowerShell)

```powershell
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

---

# Inicialização dos Containers

Na raiz do projeto:

```bash
docker compose up --build -d
```

Verifique os containers:

```bash
docker ps
```

Acessar o cliente:

```bash
docker exec -it redes_client bash
```

Acessar o servidor:

```bash
docker exec -it redes_server bash
```

---

# Execução do TCP

## Servidor

```bash
docker exec -it redes_server bash

python3 -m src.server.tcp_server
```

## Cliente

```bash
docker exec -it redes_client bash

python3 -m src.client.tcp_client
```

---

# Execução do R-UDP

## Servidor

```bash
docker exec -it redes_server bash

python3 -m src.server.rudp_server
```

## Cliente

```bash
docker exec -it redes_client bash

python3 -m src.client.rudp_client
```

---

# Simulação dos Cenários de Rede

Os cenários são configurados utilizando NetEm.

## Cenário A

```bash
tc qdisc replace dev eth0 root netem delay 10ms loss 0%
```

## Cenário B

```bash
tc qdisc replace dev eth0 root netem delay 50ms loss 10%
```

## Cenário C

```bash
tc qdisc replace dev eth0 root netem delay 100ms loss 20%
```

Verificar configuração:

```bash
tc qdisc show dev eth0
```

Remover configuração:

```bash
tc qdisc del dev eth0 root
```

---

# Captura de Tráfego

Iniciar captura:

```bash
tcpdump -i any -w captures/teste.pcap
```

Encerrar captura:

```text
CTRL + C
```

---

# Execução Automatizada dos Experimentos

O script principal executa:

* TCP e R-UDP;
* Cenários A, B e C;
* Cinco repetições por cenário;
* Captura automática dos arquivos PCAP;
* Consolidação dos resultados em CSV.

Execução:

```bash
python scripts/run_all.py
```

---

# Cenários Avaliados

| Cenário | Delay  | Perda |
| ------- | ------ | ----- |
| A       | 10 ms  | 0 %   |
| B       | 50 ms  | 10 %  |
| C       | 100 ms | 20 %  |

---

# Métricas Avaliadas

## Aplicação

* Throughput da aplicação
* Tempo total de transferência
* Taxa de entrega
* Número de retransmissões

## Rede

* Throughput observado
* Quantidade de pacotes
* Volume total trafegado
* Overhead de rede

---

# Extração de Métricas dos PCAPs

Após executar os experimentos:

```bash
python scripts/extract_pcap_metrics.py
```

O script gera um arquivo CSV contendo:

* Quantidade de pacotes;
* Volume total de bytes;
* Duração da captura;
* Throughput observado na rede.

---

# Reprodução da Análise

Os gráficos e tabelas do relatório podem ser reproduzidos utilizando os notebooks localizados em:

```text
analysis/
```

Os notebooks podem ser executados:

* Localmente via Jupyter Notebook;
* No Visual Studio Code;
* No Google Colab.

Os gráficos gerados são armazenados em:

```text
results/figures/
```

---

# Resultados Obtidos

As análises realizadas incluem:

* Throughput médio da aplicação;
* Tempo médio de transferência;
* Retransmissões do protocolo R-UDP;
* Overhead observado na rede;
* Quantidade de pacotes capturados;
* Throughput observado na rede;
* Comparação entre métricas da aplicação e da rede.

---

# Referências

* RFC 768 - User Datagram Protocol (UDP)
* RFC 793 - Transmission Control Protocol (TCP)
* Tanenbaum, A. S.; Wetherall, D. Computer Networks.
* Kurose, J. F.; Ross, K. W. Computer Networking: A Top-Down Approach.

---

# Autor

**Nara Raquel Dias Andrade**

Programa de Pós-Graduação em Ciência da Computação (PPGCC)

Universidade Federal do Piauí (UFPI)

Teresina - PI - Brasil
