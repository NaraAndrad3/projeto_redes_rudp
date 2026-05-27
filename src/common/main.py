from checksum import (
    gera_checksum,
    verifica_checksum
)

dados = b"hello world"

checksum = gera_checksum(dados)

print(checksum)

print(
    verifica_checksum(
        dados,
        checksum
    )
)