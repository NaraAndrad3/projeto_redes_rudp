import hashlib


def gera_checksum(data: bytes) -> str:
    """ Gera um checksum para os dados fornecidos.

    Args:
        data (str or bytes): Os dados para os quais o checksum deve ser gerado. Pode ser uma string ou bytes.

    Returns:
        str: O checksum gerado.
    """
    return hashlib.sha256(data).digest()


def verifica_checksum(data, checksum):
    """ Verifica se o checksum dos dados corresponde ao checksum fornecido.

    Args:
        data (str or bytes): Os dados para os quais o checksum deve ser verificado. Pode ser uma string ou bytes.
        checksum (str): O checksum a ser comparado.

    Returns:
        bool: True se o checksum dos dados corresponder ao checksum fornecido, False caso contrário.
    """
    return gera_checksum(data) == checksum




dados = b'hello'

c = gera_checksum(dados)
print(f"Checksum: {c}")

verifica_checksum(dados, c)  # True
