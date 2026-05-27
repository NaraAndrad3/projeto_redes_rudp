# Projeto de Redes de Computadores - PPGCC/UFPI

## Descrição

Projeto desenvolvido para a disciplina de Redes de Computadores do Programa de Pós-Graduação em Ciência da Computação (PPGCC/UFPI).

O objetivo é implementar e analisar um sistema de transferência de arquivos utilizando:

- TCP tradicional;
- R-UDP (Reliable UDP) com mecanismo de confiabilidade implementado em nível de aplicação.

Além da implementação, serão realizados experimentos controlados com Docker, simulação de perdas e atrasos de rede utilizando `tc`, captura de tráfego com `tcpdump` e análise estatística dos resultados.

---

## Objetivos

### Fase 1 - Implementação Real

- Implementar transferência de arquivos via TCP.
- Implementar transferência de arquivos via R-UDP.
- Desenvolver mecanismo de:
  - numeração de sequência;
  - ACKs;
  - timeout;
  - retransmissão;
  - validação de integridade.
- Simular diferentes condições de rede.
- Capturar tráfego utilizando tcpdump.
- Comparar métricas da aplicação com métricas observadas na rede.

### Fase 2 - Modelagem Estocástica

- Desenvolver simulador utilizando SimPy.
- Validar o simulador utilizando os dados obtidos na Fase 1.
- Comparar resultados simulados e experimentais.

---

## Tecnologias Utilizadas

- Python 3
- Docker
- Ubuntu Linux
- Sockets TCP
- Sockets UDP
- tc (Traffic Control)
- tcpdump
- Pandas
- Plotly
- SimPy
- Git/GitHub

---

## Estrutura do Projeto

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
├── logs/
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

## Arquitetura Geral

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

tcpdump → PCAP → CSV → Análise Estatística
```

---

## Cenários de Teste

### Cenário A

- Perda: 0%
- Delay: 10 ms

### Cenário B

- Perda: 10%
- Delay: 50 ms

### Cenário C

- Perda: 20%
- Delay: 100 ms

---

## Métricas Avaliadas

- Tempo total de transferência
- Throughput
- RTT
- Taxa de retransmissão
- Perda de pacotes
- Vazão efetiva

---

## Roadmap da implementaçao do projeto

### Ambiente

- [x] Criação do repositório
- [x] Estrutura inicial de diretórios
- [ ] Configuração Docker
- [ ] Configuração da rede virtual

### Implementação TCP

- [ ] Servidor TCP
- [ ] Cliente TCP
- [ ] Transferência de arquivos

### Implementação R-UDP

- [ ] Estrutura de pacotes
- [ ] Checksum
- [ ] ACKs
- [ ] Timeout
- [ ] Retransmissão
- [ ] Janela deslizante (Go-Back-N)

### Testes

- [ ] Cenário A
- [ ] Cenário B
- [ ] Cenário C

### Captura e análise

- [ ] tcpdump
- [ ] Exportação CSV
- [ ] Geração de gráficos

### Simulação

- [ ] Modelagem em SimPy
- [ ] Validação cruzada

## Autor

Nara Raquel Dias Andrade

Programa de Pós-Graduação em Ciência da Computação (PPGCC)

Universidade Federal do Piauí