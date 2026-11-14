# -*- coding: utf-8 -*-
"""Rastro de Polen (Melina, Evento 1 — O Novo Jardim).

Arraste o mouse para 'pintar' o campo de amarelo (polinizar) antes que o
tempo acabe. Quanto mais area coberta, melhor o resultado.

O jogo termina na hora se o campo for coberto por inteiro (100%). Se não, termina quando
o tempo acaba.

Regras de resultado (fracao do campo coberta quando o jogo termina):
  - 80% ou mais    -> sucesso
  - 75% a 80%      -> parcial
  - menos de 75%   -> falha
"""
import random

import pygame

from . import pixel
from .base import BasePuzzle
from .icones import linha_de_status

BRUSH_RADIUS_CELLS = 1  # quantas celulas ao redor do cursor sao pintadas de uma vez

# --- AJUSTES -------------------------------------------------------------
TEMPO_EM_SEGUNDOS = 10.0           # quanto tempo dura o jogo (e aparece na tela)
COBERTURA_PARA_SUCESSO = 0.80     # esta fração do campo (ou mais) = sucesso
COBERTURA_PARA_PARCIAL = 0.75     # daí até a de cima = parcial; abaixo disto = falha


class RastroDePolen(BasePuzzle):
    name = "Rastro de Pólen"
    # texto da tela de preparo (os segundos antes de jogar)
    instrucao = (
        "Arraste o mouse (mantendo o botão pressionado) para polinizar o campo de "
        "amarelo. Cubra o máximo possível antes que o tempo acabe: se cobrir tudo, o jogo termina na hora."
    )

    def __init__(self, rect, difficulty=1, relacao=100):
        self.rect = rect
        self.difficulty = difficulty
        self.done = False
        self.result = None

        # o campo é dividido em células IGUAIS que cobrem o campo TODO, de ponta a ponta (sem sobrar faixa
        # que não dá para pintar): 18 é só o tamanho aproximado de cada uma
        self.cell_size = 18
        self.cols = max(1, round(rect.width / self.cell_size))
        self.rows = max(1, round(rect.height / self.cell_size))
        self.covered = [[False] * self.cols for _ in range(self.rows)]
        self.total_cells = self.cols * self.rows
        self.covered_count = 0

        self.time_left = TEMPO_EM_SEGUNDOS
        self.brilhos = []              # faíscas de pólen que sobem quando a abelha passa (só enfeite)

    def _cell_at(self, pos):
        x, y = pos[0] - self.rect.left, pos[1] - self.rect.top
        if 0 <= x < self.rect.width and 0 <= y < self.rect.height:
            return int(x * self.cols // self.rect.width), int(y * self.rows // self.rect.height)
        return None

    def _area_da_celula(self, gx, gy):
        """A área da célula na tela: as células dividem o campo por inteiro, sem folga."""
        x0 = self.rect.left + gx * self.rect.width // self.cols
        x1 = self.rect.left + (gx + 1) * self.rect.width // self.cols
        y0 = self.rect.top + gy * self.rect.height // self.rows
        y1 = self.rect.top + (gy + 1) * self.rect.height // self.rows
        return pygame.Rect(x0, y0, x1 - x0, y1 - y0)

    def _paint(self, pos):
        cell = self._cell_at(pos)
        if cell is None:
            return
        gx, gy = cell
        for dy in range(-BRUSH_RADIUS_CELLS, BRUSH_RADIUS_CELLS + 1):
            for dx in range(-BRUSH_RADIUS_CELLS, BRUSH_RADIUS_CELLS + 1):
                x, y = gx + dx, gy + dy
                if 0 <= x < self.cols and 0 <= y < self.rows and not self.covered[y][x]:
                    self.covered[y][x] = True
                    self.covered_count += 1
                    area = self._area_da_celula(x, y)
                    for _ in range(2):
                        self.brilhos.append([random.uniform(area.left, area.right), random.uniform(area.top, area.bottom), 0.0])
        if self.covered_count >= self.total_cells:      # campo todo coberto: acabou, sem esperar o tempo
            self._finish()

    def update(self, dt):
        for brilho in self.brilhos:                      # (as faíscas continuam subindo depois do fim)
            brilho[2] += dt
            brilho[1] -= 28 * dt
        self.brilhos = [b for b in self.brilhos if b[2] < 0.5][-120:]
        if self.done:
            return
        self.time_left -= dt
        if self.time_left <= 0:
            self._finish()

    def handle_key(self, key):
        pass

    def handle_click(self, pos):
        if self.done:
            return
        self._paint(pos)

    def handle_drag(self, pos, pressed):
        if self.done or not pressed:
            return
        self._paint(pos)

    def _finish(self):
        self.done = True
        ratio = self.covered_count / max(1, self.total_cells)
        if ratio >= COBERTURA_PARA_SUCESSO:
            self.result = "sucesso"
        elif ratio >= COBERTURA_PARA_PARCIAL:
            self.result = "parcial"
        else:
            self.result = "falha"

    def draw(self, surface):
        pixel.campo(surface, self.rect, "grama", vinheta=False)
        # o pólen: cada célula coberta mostra o pedaço do desenho do pólen que fica no lugar dela, com luz nas
        # bordas de cima/esquerda e sombra nas de baixo/direita (para parecer uma camada por cima da grama)
        polen = pixel.fundo_pronto("polen", self.rect.width, self.rect.height)
        for gy in range(self.rows):
            for gx in range(self.cols):
                if not self.covered[gy][gx]:
                    continue
                area = self._area_da_celula(gx, gy)
                surface.blit(polen, area.topleft, area.move(-self.rect.left, -self.rect.top))
                if gy == 0 or not self.covered[gy - 1][gx]:
                    pygame.draw.rect(surface, (255, 244, 170), (area.left, area.top, area.width, 2))
                if gx == 0 or not self.covered[gy][gx - 1]:
                    pygame.draw.rect(surface, (255, 238, 150), (area.left, area.top, 2, area.height))
                if gy == self.rows - 1 or not self.covered[gy + 1][gx]:
                    pygame.draw.rect(surface, (150, 92, 14), (area.left, area.bottom - 4, area.width, 4))
                    pygame.draw.rect(surface, (96, 62, 24), (area.left, area.bottom - 1, area.width, 1))
                if gx == self.cols - 1 or not self.covered[gy][gx + 1]:
                    pygame.draw.rect(surface, (170, 108, 18), (area.right - 3, area.top, 3, area.height))
        pixel.vinheta(surface, self.rect)
        for x, y, t in self.brilhos:
            lado = 4 if t < 0.25 else 2
            pygame.draw.rect(surface, (255, 252, 214), (int(x), int(y), lado, lado))
        ratio = self.covered_count / max(1, self.total_cells)
        linha_de_status(surface, self.rect,
                        f"Arraste o mouse para polinizar  Coberto: {ratio*100:.0f}%  "
                        f"Tempo: {max(0, self.time_left):.1f}s", ratio)
