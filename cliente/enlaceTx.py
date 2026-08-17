#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################
# Camada Física da Computação
#Carareto
#17/02/2018
#  Camada de Enlace
####################################################

# Importa pacote de tempo
import time

# Threads
import threading

# Class
class TX(object):

    def __init__(self, fisica):
        self.fisica      = fisica
        self.buffer      = bytes(bytearray())
        self.transLen    = 0
        self.empty       = True
        self.threadMutex = False
        self.threadStop  = False


    def thread(self):
        while not self.threadStop:
            if(self.threadMutex):
                self.transLen    = self.fisica.write(self.buffer)
                self.threadMutex = False

    def threadStart(self):
        self.thread = threading.Thread(target=self.thread, args=())
        self.thread.start()

    def threadKill(self):
        self.threadStop = True

    def threadPause(self):
        self.threadMutex = False

    def threadResume(self):
        self.threadMutex = True

    def sendBuffer(self, data):
        self.transLen   = 0
        self.buffer = data
        self.threadMutex  = True

    def getBufferLen(self):
        return(len(self.buffer))

    def getStatus(self):
        # BUG ORIGINAL: getStatus() era chamado logo apos sendBuffer(),
        # mas quem realmente escreve na porta e preenche "transLen" e a
        # thread TX, que roda em paralelo (thread.thread). Como a leitura
        # acontecia antes da thread terminar de escrever, transLen ainda
        # estava no valor inicial (0), entao a funcao sempre "informava"
        # que nada tinha sido enviado, mesmo com o envio ocorrendo certo.
        # Correcao: esperar ate a thread TX sinalizar que terminou
        # (threadMutex volta a False) antes de devolver transLen.
        while(self.threadMutex == True):
            time.sleep(0.01)
        return(self.transLen)


    def getIsBussy(self):
        return(self.threadMutex)
