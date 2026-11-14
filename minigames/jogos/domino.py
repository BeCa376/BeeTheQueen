# -*- coding: utf-8 -*-
"""Dominó (Evento 4 — A Seca Chega, pedir ajuda às colmeias vizinhas).

As peças representam colmeias e quantidades de água. A jogadora recebe uma peça já na mesa e
precisa encaixar TODAS as outras, ligando valores iguais, até formar a corrente de ajuda.
Clique numa peça da mão: se ela só cabe numa ponta, encaixa sozinha; se cabe nas duas, clique
na ponta que você quer. Encaixou errado e travou? Clique numa peça da corrente para devolvê-la à mão (junto com as que
vêm depois dela). A peça que já estava na mesa fica. As peças sempre têm solução.

O jogo termina na hora se todas as peças forem encaixadas; senão, quando o tempo acaba.

Regras de resultado (peças na mesa quando o jogo termina, contando a que já veio na mesa):
  - 7 ou 8 peças  -> sucesso
  - 5 ou 6 peças  -> parcial
  - 0 a 4 peças   -> falha
"""
import random

import pygame

from .base import BasePuzzle, difficulty_scale
from . import pixel
from .icones import OURO, linha_de_status

COMPRIMENTO, ALTURA = 64, 32             # tamanho de uma peça (deitada)

# --- AJUSTES -------------------------------------------------------------
TEMPO_EM_SEGUNDOS = 15.0          # quanto tempo dura o jogo (e aparece na tela)
PECAS = 8                         # quantas peças no total (contando a que já vem na mesa)
PECAS_PARA_SUCESSO = 7            # este tanto (ou mais) na mesa = sucesso
PECAS_PARA_PARCIAL = 5            # daqui até o de cima = parcial; abaixo disto = falha
COR_DAS_BOLINHAS = (70, 130, 200)

# onde ficam as bolinhas num quadrado, em fração de lado (0..1), para cada valor
_C, _E, _D = 0.5, 0.28, 0.72
BOLINHAS = {
    0: [], 1: [(_C, _C)], 2: [(_E, _E), (_D, _D)], 3: [(_E, _E), (_C, _C), (_D, _D)],
    4: [(_E, _E), (_D, _E), (_E, _D), (_D, _D)], 5: [(_E, _E), (_D, _E), (_C, _C), (_E, _D), (_D, _D)],
    6: [(_E, _E), (_D, _E), (_E, _C), (_D, _C), (_E, _D), (_D, _D)],
}


class Domino(BasePuzzle):
    name = "Dominó"
    # texto da tela de preparo (os segundos antes de jogar)
    instrucao = (
        "Encaixe todas as peças, ligando números iguais, para formar a corrente de ajuda entre as "
        "colmeias. Clique numa peça para encaixá-la; clique numa peça da corrente para desfazê-la."
    )

    def __init__(self, rect, difficulty=1, relacao=100):
        self.rect = rect
        self.difficulty = difficulty
        self.done = False
        self.result = None

        self.total = min(9, PECAS)                                                          # (9 peças é o que cabe na área)
        self.maior_valor = min(6, int(round(difficulty_scale(difficulty, relacao, 4, 6))))     # (as bolinhas vão até 6)
        self.tempo_total = TEMPO_EM_SEGUNDOS
        self.time_left = self.tempo_total
        self.erros = 0
        self.tremor = 0.0
        self.selecionada = None            # peça da mão que cabe nas duas pontas, esperando a ponta

        trilha = self._sortear_trilha(self.total, self.maior_valor)
        meio = len(trilha) // 2
        self.cadeia = [trilha[meio]]       # (esquerda, direita), da esquerda para a direita
        self.indice_da_inicial = 0         # onde está, na corrente, a peça que já veio na mesa
        self.mao = []
        for i, (a, b) in enumerate(trilha):
            if i != meio:
                self.mao.append((a, b) if random.random() < 0.5 else (b, a))
        random.shuffle(self.mao)

    @staticmethod
    def _sortear_trilha(n, maior):
        """n peças diferentes, uma ligada à outra (a solução que sempre existe)."""
        while True:
            atual = random.randint(0, maior)
            usadas, trilha = set(), []
            for _ in range(n):
                opcoes = [w for w in range(maior + 1) if frozenset((atual, w)) not in usadas]
                if not opcoes:
                    break
                proximo = random.choice(opcoes)
                usadas.add(frozenset((atual, proximo)))
                trilha.append((atual, proximo))
                atual = proximo
            if len(trilha) == n:
                return trilha

    # ------------------------------------------------------------- as regras do encaixe
    def pontas(self):
        return self.cadeia[0][0], self.cadeia[-1][1]

    def encaixes(self, peca):
        """Onde a peça cabe: {'esq': peça girada, 'dir': peça girada} (só as pontas que servem)."""
        a, b = peca
        esquerda, direita = self.pontas()
        onde = {}
        if a == direita:
            onde["dir"] = (a, b)
        elif b == direita:
            onde["dir"] = (b, a)
        if b == esquerda:
            onde["esq"] = (a, b)
        elif a == esquerda:
            onde["esq"] = (b, a)
        return onde

    def _colocar(self, peca, ponta):
        girada = self.encaixes(peca)[ponta]
        self.mao.remove(peca)
        if ponta == "dir":
            self.cadeia.append(girada)
        else:
            self.cadeia.insert(0, girada)
            self.indice_da_inicial += 1
        self.selecionada = None
        if not self.mao:
            self._terminar()

    def _devolver(self, indice):
        """Tira da corrente a peça `indice` e todas as que vêm depois dela (do lado dela), devolvendo-as
        à mão. A peça inicial nunca sai."""
        inicial = self.indice_da_inicial
        if indice == inicial:
            return
        if indice > inicial:
            saem = self.cadeia[indice:]
            del self.cadeia[indice:]
        else:
            saem = self.cadeia[:indice + 1]
            del self.cadeia[:indice + 1]
            self.indice_da_inicial -= indice + 1
        self.mao.extend(saem)
        self.selecionada = None

    # ------------------------------------------------------------- posições na tela
    def _area_da_corrente(self):
        largura = len(self.cadeia) * COMPRIMENTO
        return pygame.Rect(self.rect.centerx - largura // 2, self.rect.top + 74, largura, ALTURA)

    def _area_da_peca_da_corrente(self, indice):
        base = self._area_da_corrente()
        return pygame.Rect(base.left + indice * COMPRIMENTO, base.top, COMPRIMENTO, ALTURA)

    def _areas_da_mao(self):
        folga = 8
        largura = len(self.mao) * COMPRIMENTO + max(0, len(self.mao) - 1) * folga
        x0 = self.rect.centerx - largura // 2
        y = self.rect.bottom - ALTURA - 28
        return [pygame.Rect(x0 + i * (COMPRIMENTO + folga), y, COMPRIMENTO, ALTURA) for i in range(len(self.mao))]

    def _marcadores(self):
        base = self._area_da_corrente()
        return {"esq": pygame.Rect(base.left - 36, base.top, 30, ALTURA),
                "dir": pygame.Rect(base.right + 6, base.top, 30, ALTURA)}

    # ------------------------------------------------------------- entrada
    def handle_key(self, key):
        pass

    def handle_click(self, pos):
        if self.done:
            return
        # 1) a ponta escolhida para a peça que cabe nos dois lados
        if self.selecionada is not None:
            for ponta, marcador in self._marcadores().items():
                if marcador.collidepoint(pos) and ponta in self.encaixes(self.selecionada):
                    self._colocar(self.selecionada, ponta)
                    return
        # 2) uma peça da mão
        for peca, area in zip(list(self.mao), self._areas_da_mao()):
            if area.collidepoint(pos):
                onde = self.encaixes(peca)
                if not onde:
                    self.erros += 1
                    self.tremor = 0.4
                    self.selecionada = None
                elif len(onde) == 1:
                    self._colocar(peca, next(iter(onde)))
                else:
                    self.selecionada = peca
                return
        # 3) uma peça da corrente: desfaz dali até a ponta
        for indice in range(len(self.cadeia)):
            if self._area_da_peca_da_corrente(indice).collidepoint(pos):
                self._devolver(indice)
                return
        self.selecionada = None

    # ------------------------------------------------------------- atualização
    def update(self, dt):
        if self.done:
            return
        self.time_left -= dt
        self.tremor = max(0.0, self.tremor - dt)
        if self.time_left <= 0:
            self._terminar()

    def na_mesa(self):
        return self.total - len(self.mao)

    def _terminar(self):
        self.done = True
        if self.na_mesa() >= PECAS_PARA_SUCESSO:
            self.result = "sucesso"
        elif self.na_mesa() >= PECAS_PARA_PARCIAL:
            self.result = "parcial"
        else:
            self.result = "falha"

    # ------------------------------------------------------------- desenho
    def _desenhar_peca(self, surface, area, peca, destaque=False):
        """Uma peça de osso em relevo: o risco do meio entalhado e as bolinhas azuis."""
        pixel.carta(surface, area, "osso", destaque=OURO if destaque else None)
        x = area.centerx
        pygame.draw.line(surface, (150, 132, 100), (x - 1, area.top + 8), (x - 1, area.bottom - 9), 2)
        pygame.draw.line(surface, (255, 254, 244), (x + 1, area.top + 8), (x + 1, area.bottom - 9), 1)
        pinta = pixel.imagem("pinta", 2)
        for metade, valor in enumerate(peca):
            quadrado = pygame.Rect(area.left + metade * (area.width // 2), area.top, area.width // 2, area.height)
            for fx, fy in BOLINHAS[valor]:
                pixel.colar(surface, pinta, centro=(quadrado.left + fx * quadrado.width, quadrado.top + fy * quadrado.height),
                            sombra=False)

    def draw(self, surface):
        pixel.campo(surface, self.rect, "madeira", vinheta=False)
        pixel.vinheta(surface, self.rect)

        pixel.texto(surface, "A corrente de ajuda", (self.rect.centerx, self.rect.top + 26), tamanho=13)
        for i, peca in enumerate(self.cadeia):
            self._desenhar_peca(surface, self._area_da_peca_da_corrente(i), peca)

        if self.selecionada is not None:                       # as duas pontas possíveis
            for ponta, marcador in self._marcadores().items():
                if ponta in self.encaixes(self.selecionada):
                    pixel.carta(surface, marcador, "creme", destaque=OURO)
                    pixel.texto(surface, "+", marcador.center, tamanho=24, cor=(255, 214, 80))

        areas = self._areas_da_mao()
        deslocamento = 4 if self.tremor > 0 and int(self.tremor * 30) % 2 else 0
        for peca, area in zip(self.mao, areas):
            self._desenhar_peca(surface, area.move(deslocamento, 0), peca, destaque=(peca == self.selecionada))
        pixel.texto(surface, "Suas peças", (self.rect.centerx, areas[0].top - 16 if areas else self.rect.bottom - 70),
                    tamanho=12, negrito=False, cor=(255, 246, 220))

        if self.mao and not any(self.encaixes(p) for p in self.mao):
            pixel.texto(surface, "Nenhuma peça encaixa! Clique numa peça da corrente para desfazer.",
                        (self.rect.centerx, self.rect.top + 128), tamanho=12, cor=(255, 190, 176))

        linha_de_status(surface, self.rect,
                        f"Na mesa: {self.na_mesa()}/{self.total}   "
                        f"Tempo: {max(0, self.time_left):.0f}s",
                        self.time_left / self.tempo_total)
