#####################################################
# Camada Física da Computação
# Projeto 2 - Desafios Client/Server
# Aplicação - SERVIDOR
####################################################

import struct
import sys
import time

from enlace import *

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

serialName = "COM3"

FLOAT_SIZE = 4
FIM_TRANSMISSAO = struct.pack('>f', float('inf'))

SIMULAR_ERRO_INTERPRETACAO = False


def decodeFloat(rawBytes):
    if SIMULAR_ERRO_INTERPRETACAO:
        rawBytes = bytes([rawBytes[0] ^ 0xFF]) + rawBytes[1:]
    return struct.unpack('>f', rawBytes)[0]


def main():
    com1 = None
    try:
        print("Iniciou o main")
        com1 = enlace(serialName)

        com1.enable()
        print("Abriu a comunicação")

        print("Aguardando byte de sacrifício...")
        com1.getData(1)
        com1.rx.clearBuffer()
        time.sleep(0.1)

        print("Servidor pronto. Aguardando números do cliente...")
        print("-------------------------------------")

        soma = 0.0
        quantidade = 0

        while True:
            rawBytes, n = com1.getData(FLOAT_SIZE)

            if rawBytes == FIM_TRANSMISSAO:
                print("-------------------------------------")
                print("Marcador de fim de transmissão recebido.")
                break

            numero = decodeFloat(rawBytes)
            print("Recebido: {:.6f}".format(numero))
            soma += numero
            quantidade += 1

        print("Total de números recebidos: {}".format(quantidade))
        print("Soma calculada: {:.6f}".format(soma))
        print("-------------------------------------")

        respostaBytes = struct.pack('>f', soma)
        com1.sendData(respostaBytes)
        com1.tx.getStatus()
        print("Soma enviada ao cliente.")

        com1.disable()
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")

    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        if com1 is not None:
            com1.disable()


if __name__ == "__main__":
    main()
