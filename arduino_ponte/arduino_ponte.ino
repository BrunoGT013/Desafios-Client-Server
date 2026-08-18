/*
  Camada Física da Computação - Projeto 2
  Ponte serial entre os dois Arduinos.

  Grave este MESMO sketch nos dois Arduinos (o do cliente e o do servidor).

  Cada Arduino conversa com seu PC pela UART de hardware (pinos D0/D1,
  usada pelo cabo USB/FTDI) e repassa os bytes para o outro Arduino por
  uma segunda UART, feita em software (pinos D10/D11), ligada por jumpers.

  Ligação entre os dois Arduinos (jumpers):
    Arduino A pino 11 (TX) -> Arduino B pino 10 (RX)
    Arduino A pino 10 (RX) -> Arduino B pino 11 (TX)
    Arduino A GND          -> Arduino B GND       (obrigatório!)
*/

#include <SoftwareSerial.h>

const int PIN_RX_LINK = 10;
const int PIN_TX_LINK = 11;

SoftwareSerial linkSerial(PIN_RX_LINK, PIN_TX_LINK);

void setup() {
  Serial.begin(115200);      // fala com o PC via USB/FTDI
  linkSerial.begin(115200);  // fala com o outro Arduino via jumper
}

void loop() {
  if (Serial.available()) {
    linkSerial.write(Serial.read());
  }
  if (linkSerial.available()) {
    Serial.write(linkSerial.read());
  }
}
