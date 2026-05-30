"""
    Configurações globais do projeto.

    Este arquivo centraliza valores usados pelo cliente, servidor,
    TCP, R-UDP, testes e logs.
"""

""" 
    Configurações de rede e protocolo. O server avai sceitar conexoes de qualquer interfaze 
"""
SERVER_HOST = "0.0.0.0"
SERVER_PORT_TCP = 5000
SERVER_PORT_UDP = 5001

"""_summary_
    Configurações de Docker. O nome do container do servidor é usado para que o cliente possa 
    se conectar a ele usando o nome do container como hostname.
    
"""
SERVER_DOCKER_NAME = "server"

"""
    Configurações de chunk e buffer.
    CHUNK_SIZE = 1024 define que o arquivo será dividido em blocos de 1 KB.
    BUFFER_SIZE = 4096 define o tamanho do buffer para leitura e escrita de dados.  
"""
CHUNK_SIZE = 1024
BUFFER_SIZE = 4096

"""
    Configurações de R-UDP.
        - WINDOW_SIZE = 4 define o número de pacotes que podem ser enviados sem esperar por um ACK.
        - TIMEOUT = 1.0 define o tempo (em segundos) que o remetente espera por um ACK antes de retransmitir o pacote.
        - MAX_RETRIES = 20 define o número máximo de tentativas de retransmissão antes de considerar a conexão perdida.
"""
WINDOW_SIZE = 4
TIMEOUT = 1.0
MAX_RETRIES = 100

"""
    Configurações de autenticação personalizada. O valor de CUSTOM_AUTH é usado como um token de autenticação
"""
CUSTOM_AUTH = "20261005127_NARA_RAQUEL_DIAS_ANDRADE"

# Caminhos
INPUT_DIR = "data/input"
OUTPUT_DIR = "data/output"
LOG_DIR = "logs"
CAPTURE_DIR = "captures"