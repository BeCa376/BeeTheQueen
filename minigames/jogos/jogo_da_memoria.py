# -*- coding: utf-8 -*-
"""Jogo da Memória (Evento 2 — Enxame Errante, recrutar a equipe de trabalho).

Cartas viradas para baixo guardam símbolos das funções da colmeia (coleta de pólen,
construção, defesa...). A jogadora vira duas por vez e precisa achar todos os pares antes
que o tempo acabe. Cada par achado é uma abelha recrutada para uma função.

O jogo termina na hora se todos os pares forem achados; senão, quando o tempo acaba.

Regras de resultado (pares achados quando o jogo termina):
  - 6 ou 7 pares  -> sucesso
  - 4 ou 5 pares  -> parcial
  - 0 a 3 pares   -> falha
"""
import math
import random

import pygame

from . import pixel
from .base import BasePuzzle
from .icones import desenhar_icone, linha_de_status

# o símbolo de cada função da colmeia (o nome é o do desenho em icones.py)
SIMBOLOS = ["flor", "colmeia", "bandeira", "gota", "animal", "sol", "folha", "pote", "estrela", "abelha"]
ESPERA_DO_ERRO = 0.85          # segundos com as duas cartas erradas à mostra

# --- AJUSTES -------------------------------------------------------------
TEMPO_EM_SEGUNDOS = 25.0          # quanto tempo dura o jogo (e aparece na tela)
PARES = 7                         # 7 pares = 14 cartas
PARES_PARA_SUCESSO = 6            # este tanto (ou mais) = sucesso
PARES_PARA_PARCIAL = 4            # daqui até o de cima = parcial; abaixo disto = falha


class JogoDaMemoria(BasePuzzle):
    name = "Jogo da Memória"
    # texto da tela de preparo (os segundos antes de jogar)
    instrucao = (
        "Vire duas cartas por vez e encontre os pares de símbolos da colmeia. Cada par é uma abelha "
        "recrutada. Forme toda a equipe antes que o tempo acabe, errando o mínimo possível."
    )

    def __init__(self, rect, difficulty=1, relacao=100):
        self.rect = rect
        self.difficulty = difficulty
        self.done = False
        self.result = None

        self.pares = min(len(SIMBOLOS), PARES)
        self.tempo_total = TEMPO_EM_SEGUNDOS
        self.time_left = self.tempo_total
        self.erros = 0
        self.achados = 0
        self.abertas = []            # as cartas viradas agora (ainda sem par)
        self.espera = 0.0

        simbolos = random.sample(SIMBOLOS, self.pares)
        valores = simbolos + simbolos
        random.shuffle(valores)
        self.cartas = [{"simbolo": v, "estado": "baixo", "area": pygame.Rect(0, 0, 0, 0)} for v in valores]
        self._posicionar()

    def _posicionar(self):
        """Escolhe a grade que deixa as cartas maiores dentro da área."""
        n = len(self.cartas)
        folga = 8
        melhor = None
        for colunas in range(2, n + 1):
            linhas = math.ceil(n / colunas)
            lado = min((self.rect.width - (colunas - 1) * folga) / colunas,
                       (self.rect.height - (linhas - 1) * folga) / linhas, 92)
            sobra = colunas * linhas - n
            if melhor is None or (lado, -sobra) > (melhor[0], -melhor[3]):
                melhor = (lado, colunas, linhas, sobra)
        lado, colunas, linhas, _ = melhor
        largura = colunas * lado + (colunas - 1) * folga
        altura = linhas * lado + (linhas - 1) * folga
        x0 = self.rect.centerx - largura / 2
        y0 = self.rect.centery - altura / 2
        for i, carta in enumerate(self.cartas):
            c, l = i % colunas, i // colunas
            carta["area"] = pygame.Rect(int(x0 + c * (lado + folga)), int(y0 + l * (lado + folga)),
                                        int(lado), int(lado))

    # ------------------------------------------------------------- entrada
    def handle_key(self, key):
        pass

    def handle_click(self, pos):
        if self.done or self.espera > 0:
            return
        for carta in self.cartas:
            if carta["estado"] == "baixo" and carta["area"].collidepoint(pos):
                carta["estado"] = "cima"
                self.abertas.append(carta)
                if len(self.abertas) == 2:
                    self._comparar()
                return

    def _comparar(self):
        a, b = self.abertas
        if a["simbolo"] == b["simbolo"]:
            a["estado"] = b["estado"] = "par"
            self.achados += 1
            self.abertas = []
            if self.achados == self.pares:
                self._terminar()
        else:
            self.erros += 1
            self.espera = ESPERA_DO_ERRO

    # ------------------------------------------------------------- atualização
    def update(self, dt):
        if self.done:
            return
        self.time_left -= dt
        if self.espera > 0:
            self.espera -= dt
            if self.espera <= 0:
                for carta in self.abertas:
                    carta["estado"] = "baixo"
                self.abertas = []
        if not self.done and self.time_left <= 0:
            self._terminar()

    def _terminar(self):
        self.done = True
        if self.achados >= PARES_PARA_SUCESSO:
            self.result = "sucesso"
        elif self.achados >= PARES_PARA_PARCIAL:
            self.result = "parcial"
        else:
            self.result = "falha"

    # ------------------------------------------------------------- desenho
    def draw(self, surface):
        pixel.campo(surface, self.rect, "terra", vinheta=False)
        for carta in self.cartas:
            area = carta["area"]
            if carta["estado"] == "baixo":
                # o verso: moldura de âmbar, favo de mel por dentro e a colmeia no meio
                pixel.carta(surface, area, "ambar")
                placa = pygame.Surface((area.width - 28, area.height - 28), pygame.SRCALPHA)
                pygame.draw.ellipse(placa, (92, 48, 8, 120), placa.get_rect())
                surface.blit(placa, placa.get_rect(center=area.center))
                desenhar_icone("colmeia", surface, area.center, area.width * 0.45)
            else:
                par = carta["estado"] == "par"
                pixel.carta(surface, area, "verde" if par else "creme", destaque=(120, 220, 110) if par else None)
                desenhar_icone(carta["simbolo"], surface, area.center, area.width * 0.7)
        pixel.vinheta(surface, self.rect)
        linha_de_status(surface, self.rect,
                        f"Pares: {self.achados}/{self.pares}   Erros: {self.erros}   "
                        f"Tempo: {max(0, self.time_left):.0f}s",
                        self.time_left / self.tempo_total)
