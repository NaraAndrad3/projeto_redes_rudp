"""
Configurações globais da Fase 2.

Este arquivo centraliza os parâmetros usados pelo simulador SimPy.
A ideia é manter os valores próximos aos utilizados na implementação real
da Fase 1, permitindo comparação entre o sistema real e o modelo simulado.
"""

# =========================
# Arquivo e pacotes
# =========================

# Tamanho do arquivo simulado em bytes.
# Inicialmente usamos 512 KB, mesmo tamanho usado nos experimentos finais da Fase 1.
FILE_SIZE_BYTES = 512 * 1024

# Tamanho de cada bloco/pacote de dados.
# Deve acompanhar o CHUNK_SIZE usado no R-UDP real.
CHUNK_SIZE_BYTES = 1024


# =========================
# Protocolo R-UDP
# =========================

# Tamanho da janela Go-Back-N.
WINDOW_SIZE = 4

# Timeout em segundos.
TIMEOUT = 1.0

# Número máximo de tentativas de retransmissão.
MAX_RETRIES = 100


# =========================
# Cenários de rede
# =========================

SCENARIOS = {
    "A": {
        "delay_ms": 10,
        "loss_probability": 0.0
    },
    "B": {
        "delay_ms": 50,
        "loss_probability": 0.10
    },
    "C": {
        "delay_ms": 100,
        "loss_probability": 0.20
    }
}


# =========================
# Simulação
# =========================

# Número de repetições estatísticas.
# Na Fase 1 usamos 5 execuções. Na Fase 2 precisaremos chegar a 30
# para intervalo de confiança de 95%.
REPETITIONS = 30

# Semente base para tornar os experimentos reproduzíveis.
RANDOM_SEED = 42