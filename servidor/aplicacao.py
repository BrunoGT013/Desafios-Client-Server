#####################################################
# Camada Física da Computação
# Projeto 2 - Desafios Client/Server
# Aplicação - SERVIDOR
####################################################

# esta é a camada superior, de aplicação do seu software de comunicação serial UART.

import struct
import sys
import time

from enlace import *

# corrige acentuação no console do Windows (cp1252 por padrão)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ------------------------------------------------------------
# Configuração
# ------------------------------------------------------------
# voce deverá configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
serialName = "COM3"  # Windows - ajuste para a porta do Arduino do servidor

FLOAT_SIZE = 4  # 1 float IEEE-754 32 bits = 4 bytes
# marcador de fim de transmissão: +infinito está fora do range permitido
# [-1000, +1000], então nunca colide com um número real enviado pelo cliente
FIM_TRANSMISSAO = struct.pack('>f', float('inf'))

# ---- Simulação de erro (item 2 da avaliação) ------------------------------
# Coloque True para forçar uma interpretação errada dos dados recebidos e
# demonstrar ao professor o caso de "erro de interpretação" no servidor.
SIMULAR_ERRO_INTERPRETACAO = False


def decodeFloat(rawBytes):
    if SIMULAR_ERRO_INTERPRETACAO:
        # corrompe deliberadamente 1 bit antes de decodificar, simulando
        # um problema de interpretação dos dados recebidos pelo servidor
        rawBytes = bytes([rawBytes[0] ^ 0xFF]) + rawBytes[1:]
    return struct.unpack('>f', rawBytes)[0]


def main():
    com1 = None
    try:
        print("Iniciou o main")
        com1 = enlace(serialName)

        com1.enable()
        print("Abriu a comunicação")

        # Workaround do byte de sacrifício (ver readme.txt): os primeiros bytes
        # de uma transmissão serial costumam vir com lixo. O servidor "nasce"
        # esperando 1 byte de sacrifício antes de começar a receber de verdade.
        print("Aguardando byte de sacrifício...")
        com1.getData(1)
        com1.rx.clearBuffer()
        time.sleep(0.1)

        print("Servidor pronto. Aguardando números do cliente...")
        print("(o servidor não sabe quantos números virão)")
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

        # Responde ao cliente com a soma, também em ponto flutuante IEEE-754 32 bits
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
