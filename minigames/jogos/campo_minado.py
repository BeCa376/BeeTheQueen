# -*- coding: utf-8 -*-
"""Campo Minado (Evento 4 — A Seca Chega, resgatar as flores nativas).

O terreno seco esconde áreas comprometidas. A jogadora clica nos quadrados para revelá-los:
cada número diz quantas áreas perigosas existem ao redor daquele quadrado. O objetivo é
revelar todas as áreas seguras (onde ainda há água para as flores) sem pisar nas perigosas.

O primeiro clique é sempre seguro (e já abre uma clareira). Pisar numa área perigosa é um
"erro"; no terceiro erro o jogo acaba.

O jogo termina na hora se todas as áreas seguras forem reveladas, no terceiro erro, ou quando o
tempo acaba.

Regras de resultado: valem DUAS contas, e o resultado é o PIOR das duas:
  as bombas (erros)               0 ou 1 -> sucesso   |  2 -> parcial   |  3 -> falha
  o quanto do campo foi revelado  80% ou mais -> sucesso | 70% a 80% -> parcial | menos de 70% -> falha
Exemplo: 0 bombas mas só 65% revelado = falha; 1 bomba e 90% revelado = sucesso.
"""
import random

import pygame

from .base import BasePuzzle
from . import pixel
from .icones import linha_de_status

COLUNAS, LINHAS, LADO = 15, 6, 40
ERROS_MAXIMOS = 3

# --- AJUSTES -------------------------------------------------------------
TEMPO_EM_SEGUNDOS = 20.0          # quanto tempo dura o jogo (e aparece na tela)
MINAS = 8                         # quantas áreas perigosas (de 90 quadrados)
ERROS_PARA_SUCESSO = 1            # até este tanto de bombas ainda é sucesso (3 bombas = fim, falha)
COBERTURA_PARA_SUCESSO = 0.80     # revelou esta fração (ou mais) das seguras = sucesso
COBERTURA_PARA_PARCIAL = 0.70     # daqui até a de cima = parcial; abaixo disto = falha

COR_TERRA = (196, 166, 112)
COR_TERRA_BORDA = (160, 130, 80)
COR_AREIA = (240, 230, 200)
COR_AGUA = (205, 228, 240)
CORES_DOS_NUMEROS = {1: (50, 85, 200), 2: (45, 135, 55), 3: (200, 55, 55), 4: (90, 45, 150),
                     5: (150, 45, 35), 6: (30, 135, 135), 7: (30, 30, 30), 8: (110, 110, 110)}


class CampoMinado(BasePuzzle):
    name = "Campo Minado"
    # texto da tela de preparo (os segundos antes de jogar)
    instrucao = (
        "Clique nos quadrados do terreno seco: o número diz quantas áreas perigosas há ao redor. "
        "Revele o máximo de áreas seguras em 10 segundos, sem pisar nas perigosas (3 bombas e acabou)."
    )

    def __init__(self, rect, difficulty=1, relacao=100):
        self.rect = rect
        self.difficulty = difficulty
        self.done = False
        self.result = None

        self.minas = MINAS
        self.tempo_total = TEMPO_EM_SEGUNDOS
        self.time_left = self.tempo_total
        self.erros = 0
        self.seguras_total = COLUNAS * LINHAS - self.minas
        self.reveladas = 0

        self.origem = (rect.centerx - COLUNAS * LADO // 2, rect.centery - LINHAS * LADO // 2)
        self.mina = [[False] * COLUNAS for _ in range(LINHAS)]
        self.aberta = [[False] * COLUNAS for _ in range(LINHAS)]
        self.explodida = [[False] * COLUNAS for _ in range(LINHAS)]
        self.vizinhas = [[0] * COLUNAS for _ in range(LINHAS)]
        self.minas_colocadas = False

    # ------------------------------------------------------------- o tabuleiro
    def _vizinhos(self, x, y):
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if (dx or dy) and 0 <= x + dx < COLUNAS and 0 <= y + dy < LINHAS:
                    yield x + dx, y + dy

    def _colocar_minas(self, x, y):
        """Sorteia as minas depois do 1º clique, longe dele (o 1º clique abre uma clareira)."""
        proibidas = {(x, y), *self._vizinhos(x, y)}
        livres = [(cx, cy) for cy in range(LINHAS) for cx in range(COLUNAS) if (cx, cy) not in proibidas]
        for cx, cy in random.sample(livres, self.minas):
            self.mina[cy][cx] = True
        for cy in range(LINHAS):
            for cx in range(COLUNAS):
                self.vizinhas[cy][cx] = sum(self.mina[vy][vx] for vx, vy in self._vizinhos(cx, cy))
        self.minas_colocadas = True

    def _celula_em(self, pos):
        x = (pos[0] - self.origem[0]) // LADO
        y = (pos[1] - self.origem[1]) // LADO
        if 0 <= x < COLUNAS and 0 <= y < LINHAS and pos[0] >= self.origem[0] and pos[1] >= self.origem[1]:
            return int(x), int(y)
        return None

    # ------------------------------------------------------------- entrada
    def handle_key(self, key):
        pass

    def handle_click(self, pos):
        if self.done:
            return
        celula = self._celula_em(pos)
        if celula is None:
            return
        x, y = celula
        if self.aberta[y][x] or self.explodida[y][x]:
            return
        if not self.minas_colocadas:
            self._colocar_minas(x, y)
        if self.mina[y][x]:
            self.explodida[y][x] = True
            self.erros += 1
            if self.erros >= ERROS_MAXIMOS:
                self._terminar()
            return
        self._revelar(x, y)
        if self.reveladas >= self.seguras_total:
            self._terminar()

    def _revelar(self, x, y):
        """Abre o quadrado; se não há perigo ao redor, abre também os vizinhos (em cascata)."""
        pilha = [(x, y)]
        while pilha:
            cx, cy = pilha.pop()
            if self.aberta[cy][cx] or self.mina[cy][cx]:
                continue
            self.aberta[cy][cx] = True
            self.reveladas += 1
            if self.vizinhas[cy][cx] == 0:
                pilha.extend(self._vizinhos(cx, cy))

    # ------------------------------------------------------------- atualização
    def update(self, dt):
        if self.done:
            return
        self.time_left -= dt
        if self.time_left <= 0:
            self._terminar()

    def _terminar(self):
        self.done = True
        # nível de cada conta: 0 = sucesso, 1 = parcial, 2 = falha; vale o pior
        if self.erros <= ERROS_PARA_SUCESSO:
            pelas_bombas = 0
        elif self.erros < ERROS_MAXIMOS:
            pelas_bombas = 1
        else:
            pelas_bombas = 2
        fracao = self.reveladas / self.seguras_total
        if fracao >= COBERTURA_PARA_SUCESSO:
            pela_cobertura = 0
        elif fracao >= COBERTURA_PARA_PARCIAL:
            pela_cobertura = 1
        else:
            pela_cobertura = 2
        self.result = ("sucesso", "parcial", "falha")[max(pelas_bombas, pela_cobertura)]

    # ------------------------------------------------------------- desenho
    def draw(self, surface):
        pixel.campo(surface, self.rect, "grama", vinheta=False)
        pixel.vinheta(surface, self.rect)
        for y in range(LINHAS):
            for x in range(COLUNAS):
                area = pygame.Rect(self.origem[0] + x * LADO, self.origem[1] + y * LADO, LADO, LADO)
                self._desenhar_quadrado(surface, area, x, y)
        linha_de_status(surface, self.rect,
                        f"Seguras: {self.reveladas}/{self.seguras_total}   Erros: {self.erros}/{ERROS_MAXIMOS}   "
                        f"Tempo: {max(0, self.time_left):.0f}s",
                        self.time_left / self.tempo_total)

    def _desenhar_quadrado(self, surface, area, x, y):
        escala = LADO // 10                                   # os quadradinhos têm 10x10 pixels de desenho
        if self.explodida[y][x]:
            surface.blit(pixel.imagem("bloco_explosao", escala), area.topleft)
            pixel.colar(surface, pixel.imagem("bomba", 1), centro=area.center)
        elif self.aberta[y][x]:
            n = self.vizinhas[y][x]
            if n == 0:                                        # nenhum perigo por perto: grama molhada e uma gotinha
                surface.blit(pixel.imagem("bloco_grama_umida", escala), area.topleft)
                pixel.colar(surface, pixel.imagem("gota_mini", 2), centro=area.center)
            else:
                surface.blit(pixel.imagem("bloco_areia", escala), area.topleft)
                pixel.texto(surface, n, (area.centerx, area.centery - 1), tamanho=20, cor=CORES_DOS_NUMEROS[n],
                            contorno=(255, 248, 226))
        else:
            surface.blit(pixel.imagem("bloco_terra_seca", escala), area.topleft)
