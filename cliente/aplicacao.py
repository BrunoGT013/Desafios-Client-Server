#####################################################
# Camada Física da Computação
# Projeto 2 - Desafios Client/Server
# Aplicação - CLIENTE
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
serialName = "COM4"  # Windows - ajuste para a porta do Arduino do cliente

FLOAT_SIZE = 4  # 1 float IEEE-754 32 bits = 4 bytes
FIM_TRANSMISSAO = struct.pack('>f', float('inf'))
TIMEOUT_RESPOSTA = 5.0  # segundos, conforme enunciado

# Números a enviar: entre 5 e 15 valores, no intervalo [-1000, +1000],
# com no mínimo 6 casas de precisão. Podem ficar "hard coded" como abaixo.
numeros = [
    45.450000,
    -1.435670,
    154.767830,
    -999.999999,
    0.123456,
    777.777777,
    -321.098765,
]


def main():
    com1 = None
    try:
        print("Iniciou o main")
        com1 = enlace(serialName)

        com1.enable()
        print("Abriu a comunicação")

        # Workaround do byte de sacrifício (ver readme.txt): envia 1 byte
        # descartável para "absorver" o lixo gerado no início da transmissão.
        # O servidor já deve estar de pé aguardando esse byte.
        time.sleep(0.2)
        com1.sendData(b'00')
        time.sleep(1)

        print("Enviando {} números...".format(len(numeros)))
        print("-------------------------------------")
        somaLocal = 0.0
        for numero in numeros:
            # o numero que realmente viaja é o float32 (perde um pouco de
            # precisao ao converter), entao somamos essa versao arredondada
            # aqui tambem - assim a soma local fica igual a que o servidor
            # vai calcular, e nao fica "inconsistencia" por causa de
            # arredondamento
            bytesNumero = struct.pack('>f', numero)
            numeroEnviado = struct.unpack('>f', bytesNumero)[0]

            print("Enviando: {:.6f}".format(numeroEnviado))
            com1.sendData(bytesNumero)
            com1.tx.getStatus()
            somaLocal += numeroEnviado

        # Marcador de fim de transmissão: o servidor não sabe quantos
        # números virão, então esse marcador é quem sinaliza o término.
        com1.sendData(FIM_TRANSMISSAO)
        com1.tx.getStatus()
        print("-------------------------------------")
        print("Transmissão concluída. Soma local: {:.6f}".format(somaLocal))

        print("Aguardando resposta do servidor (timeout {}s)...".format(TIMEOUT_RESPOSTA))
        t0 = time.time()
        while com1.rx.getBufferLen() < FLOAT_SIZE:
            if time.time() - t0 > TIMEOUT_RESPOSTA:
                print("[TIME OUT] Servidor não respondeu em {}s.".format(TIMEOUT_RESPOSTA))
                com1.disable()
                return
            time.sleep(0.01)

        respostaBytes, n = com1.getData(FLOAT_SIZE)
        somaServidor = struct.unpack('>f', respostaBytes)[0]
        print("Soma recebida do servidor: {:.6f}".format(somaServidor))

        if abs(somaServidor - somaLocal) < 1e-3:
            print("SUCESSO: soma recebida confere com o cálculo local.")
        else:
            print("INCONSISTÊNCIA: soma do servidor ({:.6f}) difere da soma local ({:.6f})"
                  .format(somaServidor, somaLocal))

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
