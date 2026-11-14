# -*- coding: utf-8 -*-
"""Quebra-cabeça de Soma (Evento 4 — A Seca Chega, racionar o mel).

A colmeia tem potes de mel com quantidades diferentes e uma meta de consumo. A jogadora
escolhe os potes cuja soma é EXATAMENTE a quantidade necessária, preservando o resto do
estoque. Clicar num pote o escolhe; clicar de novo o devolve. Cada fase traz potes e meta
novos (e a meta sempre pode ser alcançada).

Regras de resultado (fases resolvidas quando o jogo termina):
  - 3 fases   -> sucesso (o jogo termina na hora)
  - 2 fases   -> parcial
  - 0 ou 1    -> falha
São só 10 segundos para as 3 fases, por isso as contas são simples (2 potes, de 6).
"""
import random

import pygame

from .base import BasePuzzle
from . import pixel
from .icones import escrever, linha_de_status

PAUSA_DO_ACERTO = 0.5

# --- AJUSTES -------------------------------------------------------------
TEMPO_EM_SEGUNDOS = 20.0          # quanto tempo dura o jogo TODO (e aparece na tela)
FASES = 3                         # quantas contas
POTES = 6                         # quantos potes em cada conta
MAIOR_POTE = 9                    # os potes valem de 1 até este número
POTES_NA_META = 2                 # a meta é a soma de quantos potes
FASES_PARA_SUCESSO = 3            # resolveu este tanto (ou mais) = sucesso
FASES_PARA_PARCIAL = 2            # daqui até o de cima = parcial; abaixo disto = falha


class QuebraCabecaDeSoma(BasePuzzle):
    name = "Quebra-cabeça de Soma"
    # texto da tela de preparo (os segundos antes de jogar)
    instrucao = (
        "Escolha os potes de mel cuja soma seja exatamente a meta de consumo. Clique para escolher "
        "e clique de novo para devolver. São 3 contas e só 10 segundos: seja rápida!"
    )

    def __init__(self, rect, difficulty=1, relacao=100):
        self.rect = rect
        self.difficulty = difficulty
        self.done = False
        self.result = None

        self.quantidade_de_potes = min(9, POTES)          # (9 potes é o que cabe na tela)
        self.maior_pote = MAIOR_POTE
        self.potes_na_meta = POTES_NA_META
        self.tempo_total = TEMPO_EM_SEGUNDOS
        self.time_left = self.tempo_total

        self.fase = 1
        self.resolvidas = 0
        self.pausa = 0.0
        self._nova_fase()

    def _nova_fase(self):
        n = self.quantidade_de_potes
        for _ in range(60):                       # a meta nunca é igual a um pote só (seria um clique)
            self.valores = [random.randint(1, self.maior_pote) for _ in range(n)]
            escolhidos = random.sample(range(n), self.potes_na_meta)
            self.meta = sum(self.valores[i] for i in escolhidos)
            if self.meta not in self.valores:
                break
        self.selecionados = set()
        # a área de cada pote
        folga = 8
        largura = int(min(74, (self.rect.width - 24 - (n - 1) * folga) / n))
        total = n * largura + (n - 1) * folga
        x0 = self.rect.centerx - total // 2
        y = self.rect.bottom - 108
        self.areas = [pygame.Rect(x0 + i * (largura + folga), y, largura, 92) for i in range(n)]

    def soma(self):
        return sum(self.valores[i] for i in self.selecionados)

    # ------------------------------------------------------------- entrada
    def handle_key(self, key):
        pass

    def handle_click(self, pos):
        if self.done or self.pausa > 0:
            return
        for i, area in enumerate(self.areas):
            if area.inflate(0, 18).collidepoint(pos):          # (o pote erguido continua clicável)
                if i in self.selecionados:
                    self.selecionados.remove(i)
                else:
                    self.selecionados.add(i)
                if self.soma() == self.meta:
                    self._acertou()
                return

    def _acertou(self):
        self.resolvidas += 1
        self.pausa = PAUSA_DO_ACERTO
        if self.resolvidas >= FASES:
            self._terminar()

    # ------------------------------------------------------------- atualização
    def update(self, dt):
        if self.done:
            return
        self.time_left -= dt
        if self.pausa > 0:
            self.pausa -= dt
            if self.pausa <= 0:
                self.fase += 1
                self._nova_fase()
        if not self.done and self.time_left <= 0:
            self._terminar()

    def _terminar(self):
        self.done = True
        if self.resolvidas >= FASES_PARA_SUCESSO:
            self.result = "sucesso"
        elif self.resolvidas >= FASES_PARA_PARCIAL:
            self.result = "parcial"
        else:
            self.result = "falha"

    # ------------------------------------------------------------- desenho
    def draw(self, surface):
        pixel.campo(surface, self.rect, "madeira", vinheta=False)
        pixel.vinheta(surface, self.rect)

        # a placa da meta: um pergaminho com a borda em relevo
        placa = pygame.Rect(0, 0, 230, 58)
        placa.midtop = (self.rect.centerx, self.rect.top + 14)
        pixel.carta(surface, placa, "creme")
        escrever(surface, f"Meta de consumo: {self.meta}", placa.center, tamanho=15, negrito=True, centro=True,
                 cor=(84, 52, 20))

        # a barra da soma (vermelha se passou da meta, verde se acertou)
        soma = self.soma()
        barra = pygame.Rect(0, 0, 360, 16)
        barra.midtop = (self.rect.centerx, placa.bottom + 12)
        passou = soma > self.meta
        cor = ((214, 80, 70), (255, 150, 130), (150, 40, 40)) if passou else \
              ((96, 190, 84), (170, 236, 150), (52, 130, 56)) if soma == self.meta else None
        pixel.barra(surface, barra, min(1.0, soma / max(1, self.meta)), cor)
        texto = f"Soma: {soma}" + ("   Passou da meta! Devolva algum pote." if passou else "")
        pixel.texto(surface, texto, (self.rect.centerx, barra.bottom + 14), tamanho=12, negrito=False,
                    cor=(255, 214, 214) if passou else (255, 246, 220))

        # os potes de mel: o escolhido sobe e ganha um brilho dourado
        pote = pixel.imagem("pote_soma", 2)
        for i, area in enumerate(self.areas):
            erguido = i in self.selecionados
            canto = (area.centerx - pote.get_width() // 2, area.top + (area.height - pote.get_height()) // 2)
            sombra = pygame.Surface((pote.get_width() - 6, 12), pygame.SRCALPHA)
            pygame.draw.ellipse(sombra, (30, 16, 4, 110), sombra.get_rect())
            surface.blit(sombra, sombra.get_rect(center=(area.centerx, area.bottom + 4)))
            if erguido:
                brilho = pixel.imagem("brilho_pote", 2)
                surface.blit(brilho, brilho.get_rect(center=(area.centerx, area.centery - 10)))
                canto = (canto[0], canto[1] - 14)
            pixel.colar(surface, pote, canto=canto, sombra=not erguido)
            escrever(surface, self.valores[i], (canto[0] + 36, canto[1] + 61), tamanho=20, negrito=True, centro=True,
                     cor=(150, 40, 20) if erguido else (84, 52, 20))

        linha_de_status(surface, self.rect,
                        f"Fase: {min(self.fase, FASES)}/{FASES}   Resolvidas: {self.resolvidas}   "
                        f"Tempo: {max(0, self.time_left):.0f}s",
                        self.time_left / self.tempo_total)
