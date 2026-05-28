import struct
from checksum import gera_checksum, verifica_checksum

HEADER_FORMAT = "!I32sI"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
ACK_FORMAT = "!I"
ACK_SIZE = struct.calcsize(ACK_FORMAT)

class Packet:
    """
    Representa um pacote do protocolo R-UDP.

    Campos:
    - sequence_number: número de sequência do pacote
    - checksum: hash SHA256 do payload
    - payload_size: tamanho real dos dados
    - payload: bloco de dados do arquivo
    """
    
    def __init__(self, sequence_number: int, payload: bytes):
        self.sequence_number = sequence_number
        self.payload = payload
        self.payload_size = len(payload)
        self.checksum = gera_checksum(payload)
        
    
    def to_bytes(self) -> bytes:
        """ Converte o pacote para bytes para envio pela rede. 
        O cabeçalho é composto pelo número de sequência, checksum e tamanho do payload, seguido pelo payload.
        """
        header = struct.pack(HEADER_FORMAT, self.sequence_number, self.checksum, self.payload_size)
        return header + self.payload
    
    @classmethod
    def from_bytes(cls, data: bytes):
        """ Converte bytes recebidos da rede para um objeto Packet. 
        O cabeçalho é lido para extrair o número de sequência, checksum e tamanho do payload, seguido pelo payload.
        """
        header = data[:HEADER_SIZE]
        payload = data[HEADER_SIZE:]
        
        sequence_number, checksum, payload_size = struct.unpack(HEADER_FORMAT, header)
        
        payload = payload[:payload_size]
        
        if not verifica_checksum(payload, checksum):
            raise ValueError("Checksum inválido")
        
        packet = cls(sequence_number, payload) # Criar o pacote usando o construtor para calcular o checksum e tamanho do payload
        packet.checksum = checksum  # Manter o checksum original para comparação futura
        packet.payload_size = payload_size  # Manter o tamanho real do payload
        
        return packet

class ACK:
    """
    Representa um ACK do protocolo R-UDP. O ack informa o remetente que um pacote foi recebido com sucesso,
    usando o número de sequência do pacote ACK para identificar qual pacote foi reconhecido.

    Campos:
    - ack_number: número de sequência do pacote ACK
    """
    
    def __init__(self, ack_number: int):
        self.ack_number = ack_number
        
    def to_bytes(self) -> bytes:
        """ Converte o ACK para bytes para envio pela rede. 
        O formato é composto apenas pelo número de sequência.
        """
        return struct.pack(ACK_FORMAT, self.ack_number)
    
    @classmethod
    def from_bytes(cls, data: bytes):
        """ Converte bytes recebidos da rede para um objeto ACK. 
        O formato é composto apenas pelo número de sequência.
        """
        ack_number = struct.unpack(ACK_FORMAT, data[:ACK_SIZE])[0]
        
        return cls(ack_number)


