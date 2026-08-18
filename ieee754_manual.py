#####################################################
# Camada Física da Computação
# Projeto 2 - Desafios Client/Server
# Demonstração manual da conversão IEEE-754 32 bits
####################################################

# Este script NÃO é usado pela aplicação client/server (que usa struct.pack
# / struct.unpack). Ele existe só para vocês conseguirem explicar ao
# professor, passo a passo e manualmente, como um número decimal vira
# ponto flutuante 32 bits e vice-versa, como pede o item "Nota A+".

import struct
import sys

# corrige acentuação no console do Windows (cp1252 por padrão)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def decimalParaIEEE754(numero):
    sinal = 0 if numero >= 0 else 1
    valor = abs(numero)

    # 1) separa parte inteira e fracionária, converte cada uma para binário
    parteInteira = int(valor)
    parteFracionaria = valor - parteInteira

    binInteiro = bin(parteInteira)[2:] if parteInteira > 0 else "0"

    binFracionario = ""
    frac = parteFracionaria
    for _ in range(30):  # bits de sobra, serão cortados depois
        frac *= 2
        bit = int(frac)
        binFracionario += str(bit)
        frac -= bit
        if frac == 0:
            break

    # 2) normaliza para a forma 1.xxxx * 2^expoente (mantissa normalizada)
    if parteInteira > 0:
        expoente = len(binInteiro) - 1
        mantissaBits = (binInteiro[1:] + binFracionario)
    else:
        # numero < 1: desloca a virgula para a direita ate achar o primeiro 1
        primeiroUm = binFracionario.index('1')
        expoente = -(primeiroUm + 1)
        mantissaBits = binFracionario[primeiroUm + 1:]

    # mantissa tem 23 bits; arredonda (round-half-up) olhando o bit seguinte,
    # em vez de simplesmente truncar (senão o último bit pode não bater
    # com o resultado de struct.pack, que arredonda)
    mantissaBits = (mantissaBits + "0" * 24)[:24]
    mantissaInt = int(mantissaBits[:23], 2)
    bitArredondamento = mantissaBits[23]
    if bitArredondamento == '1':
        mantissaInt += 1
        if mantissaInt >= (1 << 23):  # overflow: 1.111...1 + 1 = 10.000...0
            mantissaInt = 0
            expoente += 1
    mantissaBits = format(mantissaInt, '023b')

    # 3) expoente com bias de 127, em 8 bits
    expoenteComBias = expoente + 127
    expoenteBits = format(expoenteComBias, '08b')

    bits32 = f"{sinal}{expoenteBits}{mantissaBits}"

    print(f"Número decimal:        {numero}")
    print(f"Sinal:                 {sinal}")
    print(f"Parte inteira (bin):   {binInteiro}")
    print(f"Parte fracion. (bin):  {binFracionario}")
    print(f"Expoente (sem bias):   {expoente}")
    print(f"Expoente (com bias 127, 8 bits): {expoenteBits}")
    print(f"Mantissa (23 bits):    {mantissaBits}")
    print(f"Palavra IEEE-754 (32 bits): {bits32}")

    return bits32


def ieee754ParaDecimal(bits32):
    sinal = int(bits32[0])
    expoenteBits = bits32[1:9]
    mantissaBits = bits32[9:]

    expoente = int(expoenteBits, 2) - 127
    mantissa = 1.0
    for i, bit in enumerate(mantissaBits):
        if bit == '1':
            mantissa += 2 ** (-(i + 1))

    valor = mantissa * (2 ** expoente)
    if sinal == 1:
        valor = -valor

    print(f"Palavra IEEE-754 (32 bits): {bits32}")
    print(f"Sinal:                 {sinal}")
    print(f"Expoente (sem bias):   {expoente}")
    print(f"Mantissa (decimal):    {mantissa}")
    print(f"Valor decimal reconstruído: {valor}")

    return valor


def conferirComStruct(numero):
    bitsReferencia = ''.join(format(byte, '08b') for byte in struct.pack('>f', numero))
    return bitsReferencia


if __name__ == "__main__":
    exemplo = 45.45

    print("=" * 60)
    print("1) Decimal -> IEEE-754 (manual)")
    print("=" * 60)
    bits = decimalParaIEEE754(exemplo)

    print()
    print("=" * 60)
    print("2) Conferência com struct.pack (biblioteca padrão)")
    print("=" * 60)
    bitsRef = conferirComStruct(exemplo)
    print(f"Manual:    {bits}")
    print(f"struct:    {bitsRef}")
    print("OK, bate!" if bits == bitsRef else "DIVERGIU, revisar!")

    print()
    print("=" * 60)
    print("3) IEEE-754 -> Decimal (manual)")
    print("=" * 60)
    ieee754ParaDecimal(bitsRef)
