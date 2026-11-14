# -*- coding: utf-8 -*-
"""Comunicação em Símbolos (Evento 2 — Enxame Errante, a nova técnica de comunicação).

Uma abelha mostra uma sequência de símbolos por alguns segundos; depois eles somem e a
jogadora precisa reproduzi-la na ordem, clicando nos símbolos de baixo. São 6 RODADAS, e a
cada rodada a sequência tem um bloco a mais (2, 3, 4, 5, 6 e 7 blocos).

Acertou a sequência: a rodada conta. Errou um símbolo: aquela rodada se perde e já vem a
seguinte (que é maior). O jogo termina depois da 6ª rodada ou quando os 30 segundos acabam.

Regras de resultado (rodadas acertadas quando o jogo termina):
  - 5 ou 6 rodadas   -> sucesso
  - 4 rodadas        -> parcial
  - 0 a 3 rodadas    -> falha
"""
import random

import pygame

from .base import BasePuzzle
from . import pixel
from .icones import VERDE, VERMELHO, desenhar_icone, linha_de_status

SIMBOLOS = ["flor", "gota", "sol", "folha", "colmeia", "estrela"]

# --- AJUSTES -------------------------------------------------------------
TEMPO_EM_SEGUNDOS = 40.0          # quanto tempo dura o jogo TODO (e aparece na tela)
RODADAS = 6                       # quantas sequências
BLOCOS_NA_PRIMEIRA = 1            # a 1ª rodada tem tantos blocos; cada uma seguinte tem 1 a mais
SIMBOLOS_NA_PALETA = 5            # quantos símbolos diferentes para escolher
SEGUNDOS_FIXOS_NA_TELA = 2      # cada sequência fica à mostra: isto, mais...
SEGUNDOS_POR_BLOCO_NA_TELA = 0.5  # ...isto vezes o número de blocos
PAUSA_ENTRE_RODADAS = 0.5
RODADAS_PARA_SUCESSO = 5          # acertou este tanto (ou mais) = sucesso
RODADAS_PARA_PARCIAL = 4          # daqui até o de cima = parcial; abaixo disto = falha


class ComunicacaoEmSimbolos(BasePuzzle):
    name = "Comunicação em Símbolos"
    # texto da tela de preparo (os segundos antes de jogar)
    instrucao = (
        "A abelha mostra uma sequência de símbolos por poucos segundos. Decore e reproduza na mesma "
        "ordem, clicando nos símbolos. São 6 rodadas, cada uma com um bloco a mais, em 30 segundos."
    )

    def __init__(self, rect, difficulty=1, relacao=100):
        self.rect = rect
        self.difficulty = difficulty
        self.done = False
        self.result = None

        self.paleta = SIMBOLOS[:min(len(SIMBOLOS), SIMBOLOS_NA_PALETA)]
        self.tempo_total = TEMPO_EM_SEGUNDOS
        self.time_left = self.tempo_total

        self.rodada = 0                       # a rodada de agora (1 a RODADAS)
        self.acertos = 0                      # quantas sequências já foram reproduzidas certo
        self.comprimento = 0
        self.fase = "mostrar"                 # mostrar | responder | pausa
        self.fase_tempo = 0.0
        self.mensagem = ""
        self.cor_da_mensagem = VERDE
        self._proxima_rodada()

    # ------------------------------------------------------------- rodadas
    def _proxima_rodada(self):
        """Começa a rodada seguinte (a primeira, no começo do jogo)."""
        self.rodada += 1
        self.comprimento = BLOCOS_NA_PRIMEIRA + self.rodada - 1
        while True:                                   # nada de três símbolos iguais seguidos (sem graça)
            self.sequencia = [random.choice(self.paleta) for _ in range(self.comprimento)]
            if not any(self.sequencia[i] == self.sequencia[i + 1] == self.sequencia[i + 2]
                       for i in range(len(self.sequencia) - 2)):
                break
        self.resposta = []
        self.fase = "mostrar"
        self.fase_tempo = SEGUNDOS_FIXOS_NA_TELA + SEGUNDOS_POR_BLOCO_NA_TELA * self.comprimento
        self.mensagem = ""

    def _fechar_a_rodada(self, acertou):
        """Acabou a rodada (certa ou errada): vem a seguinte, ou o jogo termina na última."""
        if acertou:
            self.acertos += 1
        if self.rodada >= RODADAS:
            self._terminar()
            return
        self.fase = "pausa"
        self.fase_tempo = PAUSA_ENTRE_RODADAS
        self.mensagem = "Acertou!" if acertou else "Errou! Vamos à próxima."
        self.cor_da_mensagem = VERDE if acertou else VERMELHO

    # ------------------------------------------------------------- entrada
    def handle_key(self, key):
        pass

    def _botoes(self):
        """Os retângulos dos símbolos de baixo (a paleta)."""
        n = len(self.paleta)
        lado, folga = 54, 14
        largura = n * lado + (n - 1) * folga
        x0 = self.rect.centerx - largura // 2
        y = self.rect.bottom - lado - 10
        return [pygame.Rect(x0 + i * (lado + folga), y, lado, lado) for i in range(n)]

    def handle_click(self, pos):
        if self.done or self.fase != "responder":
            return
        for simbolo, botao in zip(self.paleta, self._botoes()):
            if botao.collidepoint(pos):
                self._escolher(simbolo)
                return

    def _escolher(self, simbolo):
        esperado = self.sequencia[len(self.resposta)]
        if simbolo != esperado:
            self._fechar_a_rodada(acertou=False)
            return
        self.resposta.append(simbolo)
        if len(self.resposta) == len(self.sequencia):
            self._fechar_a_rodada(acertou=True)

    # ------------------------------------------------------------- atualização
    def update(self, dt):
        self.t = getattr(self, "t", 0.0) + dt                  # só para a abelha bater as asas
        if self.done:
            return
        self.time_left -= dt
        if self.time_left <= 0:
            self._terminar()
            return
        if self.fase == "mostrar":
            self.fase_tempo -= dt
            if self.fase_tempo <= 0:
                self.fase = "responder"
        elif self.fase == "pausa":
            self.fase_tempo -= dt
            if self.fase_tempo <= 0:
                self._proxima_rodada()

    def _terminar(self):
        self.done = True
        if self.acertos >= RODADAS_PARA_SUCESSO:
            self.result = "sucesso"
        elif self.acertos >= RODADAS_PARA_PARCIAL:
            self.result = "parcial"
        else:
            self.result = "falha"

    # ------------------------------------------------------------- desenho
    def draw(self, surface):
        pixel.campo(surface, self.rect, "terra", vinheta=False)
        pixel.vinheta(surface, self.rect)

        # a abelha que transmite a mensagem (batendo as asas)
        pixel.colar(surface, pixel.abelha(getattr(self, "t", 0.0), 2), (self.rect.left + 52, self.rect.top + 64))

        # a fileira da sequência: aparece só na fase de mostrar; depois, caixas que se enchem
        n = len(self.sequencia)
        lado, folga = 46, 10
        largura = n * lado + (n - 1) * folga
        x0 = self.rect.centerx - largura // 2 + 30
        y = self.rect.top + 40
        for i in range(n):
            caixa = pygame.Rect(x0 + i * (lado + folga), y, lado, lado)
            if self.fase == "mostrar":
                pixel.carta(surface, caixa, "creme")
                desenhar_icone(self.sequencia[i], surface, caixa.center, lado * 0.75)
            elif i < len(self.resposta):
                pixel.carta(surface, caixa, "verde")
                desenhar_icone(self.resposta[i], surface, caixa.center, lado * 0.75)
            else:
                pixel.carta(surface, caixa, "funda")
                pixel.texto(surface, "?", caixa.center, tamanho=20, cor=(120, 98, 60), contorno=(252, 244, 220))

        # a frase do meio
        if self.fase == "mostrar":
            frase, cor = "Decore a sequência!", (255, 246, 220)
        elif self.fase == "responder":
            frase, cor = "Agora reproduza, na ordem:", (255, 246, 220)
        else:
            frase, cor = self.mensagem, ((190, 255, 170) if self.cor_da_mensagem == VERDE else (255, 190, 176))
        pixel.texto(surface, frase, (self.rect.centerx, self.rect.top + 124), tamanho=14, cor=cor)

        # a paleta
        ativa = self.fase == "responder"
        for simbolo, botao in zip(self.paleta, self._botoes()):
            pixel.carta(surface, botao, "creme" if ativa else "cinza")
            desenhar_icone(simbolo, surface, botao.center, botao.width * 0.7, sombra=ativa)

        linha_de_status(surface, self.rect,
                        f"Rodada: {min(self.rodada, RODADAS)}/{RODADAS}   Acertos: {self.acertos}   "
                        f"Tempo: {max(0, self.time_left):.0f}s",
                        self.time_left / self.tempo_total)
