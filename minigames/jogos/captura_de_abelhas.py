# -*- coding: utf-8 -*-
"""Captura de Abelhas (Evento 2 — Enxame Errante).

Um enxame de abelhas selvagens está solto e a jogadora precisa conduzi-las até o abrigo
(o quadrado com a entrada). As abelhas FOGEM do cursor: é preciso chegar por trás delas e
empurrá-las para a entrada, sem encurralá-las nos cantos.

Regras de resultado (quantas abelhas estão dentro do abrigo quando o jogo termina):
  - 6 ou 7 dentro -> sucesso (com as 7 dentro, o jogo termina na hora)
  - 4 ou 5        -> parcial
  - 0 a 3         -> falha
As abelhas também sentem o cheiro do mel do abrigo e, longe do cursor, vão devagar para a
entrada: isso ajuda a soltar as que ficam presas nos cantos, mas sozinhas não chegam a tempo.
Quanto mais difícil: mais abelhas, entrada mais estreita, menos tempo e abelhas mais rápidas.
"""
import math
import random

import pygame

from . import pixel
from .base import BasePuzzle, difficulty_scale
from .icones import linha_de_status

# --- AJUSTES -------------------------------------------------------------
TEMPO_EM_SEGUNDOS = 15.0          # quanto tempo dura o jogo (e aparece na tela)
QUANTAS_ABELHAS = 7
ABELHAS_PARA_SUCESSO = 6          # este tanto (ou mais) dentro do abrigo = sucesso
ABELHAS_PARA_PARCIAL = 4          # daqui até o de cima = parcial; abaixo disto = falha
SEPARACAO_MINIMA = 92             # as abelhas começam ESPALHADAS: no mínimo esta distância (px) entre duas
DISTANCIA_MINIMA_DA_ENTRADA = 150  # e nenhuma começa perto da entrada do abrigo
MARGEM_DO_CAMPO = 34              # nem encostada nas bordas do campo
RAIO_DE_FUGA = 110                # o mouse a menos desta distância (px) de uma abelha faz ela fugir
VELOCIDADE_DE_FUGA = (340, 380)   # a velocidade (px/s) da fuga no nível mais fácil e no mais difícil
SUSTO_EM_SEGUNDOS = 1.0            # depois de assustada, a abelha ainda corre este tempo (e vai desacelerando) antes de parar
DESVIO_DA_FUGA = 25               # graus que a abelha desvia do caminho reto ao fugir (pra escorregar de lado)
FUNIL_DISTANCIA = 170             # (opcional) perto da entrada, o cheiro do mel puxa para dentro a abelha que JÁ FOI ESPANTADA...
FUNIL_FORCA = 0                   # ...com esta velocidade (px/s). 0 = DESLIGADO: a abelha só anda por causa do mouse.

RAIO_DA_ABELHA = 9
ESPESSURA_DA_PAREDE = 8
COR_DA_PAREDE = (130, 92, 52)
COR_DO_CHAO_DO_ABRIGO = (238, 218, 160)


class CapturaDeAbelhas(BasePuzzle):
    name = "Captura de Abelhas"
    # texto da tela de preparo (os segundos antes de jogar)
    instrucao = (
"Conduza as abelhas selvagens até o abrigo. Elas ficam paradas até o cursor chegar perto, e aí "
        "fogem dele: aproxime-se por trás de cada uma e empurre-a para a entrada, antes que o tempo acabe."
    )

    def __init__(self, rect, difficulty=1, relacao=100):
        self.rect = rect
        self.difficulty = difficulty
        self.done = False
        self.result = None

        self.total = QUANTAS_ABELHAS
        self.tempo_total = TEMPO_EM_SEGUNDOS
        self.time_left = self.tempo_total
        self.raio_de_fuga = RAIO_DE_FUGA
        self.vel_de_fuga = difficulty_scale(difficulty, relacao, *VELOCIDADE_DE_FUGA)
        self.vel_de_passeio = 22                  # só as abelhas que já estão DENTRO do abrigo passeiam
        self.cursor = None

        self._montar_abrigo(difficulty, relacao)
        self._espalhar_abelhas()

    # ------------------------------------------------------------- montagem
    def _montar_abrigo(self, difficulty, relacao):
        # o abrigo ocupa toda a altura do lado direito (sem faixas de cima e de baixo: seriam becos sem saída)
        largura, altura = 130, self.rect.height
        self.abrigo = pygame.Rect(self.rect.right - largura, self.rect.top, largura, altura)
        boca = int(round(difficulty_scale(difficulty, relacao, 120, 84)))      # altura da entrada
        e = ESPESSURA_DA_PAREDE
        resto = (altura - boca) // 2
        a = self.abrigo
        self.entrada = pygame.Rect(a.left, a.top + resto, e, boca)
        self.paredes = [
            pygame.Rect(a.left, a.top, a.width, e),                        # de cima
            pygame.Rect(a.left, a.bottom - e, a.width, e),                 # de baixo
            pygame.Rect(a.right - e, a.top, e, a.height),                  # do fundo
            pygame.Rect(a.left, a.top, e, resto),                          # da frente, acima da entrada
            pygame.Rect(a.left, a.bottom - resto, e, resto),               # da frente, abaixo da entrada
        ]
        self.interior = pygame.Rect(a.left + e, a.top + e, a.width - 2 * e, a.height - 2 * e)

    def _espalhar_abelhas(self):
        """As abelhas começam ESPALHADAS pelo campo (longe umas das outras, das bordas e da entrada) e ficam
        PARADAS: só se mexem quando o mouse chega perto delas."""
        self.abelhas = []
        esquerda = self.rect.left + MARGEM_DO_CAMPO
        direita = self.abrigo.left - 60
        topo, base = self.rect.top + MARGEM_DO_CAMPO, self.rect.bottom - MARGEM_DO_CAMPO
        entrada = pygame.Vector2(self.entrada.centerx, self.entrada.centery)
        separacao = SEPARACAO_MINIMA
        tentativas = 0
        while len(self.abelhas) < self.total:
            tentativas += 1
            if tentativas % 400 == 0:               # campo apertado: aceita um pouco menos de distância
                separacao *= 0.9
            x, y = random.uniform(esquerda, direita), random.uniform(topo, base)
            if (pygame.Vector2(x, y) - entrada).length() < DISTANCIA_MINIMA_DA_ENTRADA:
                continue
            if all(math.hypot(x - b["pos"].x, y - b["pos"].y) >= separacao for b in self.abelhas):
                self.abelhas.append({
                    "pos": pygame.Vector2(x, y),
                    "vel": pygame.Vector2(0, 0),
                    "ang": random.uniform(0, 2 * math.pi),    # (só desencontra o bater de asas de cada abelha)
                    "lado": random.choice((-1, 1)),           # pra que lado ela escorrega ao fugir
                    "dentro": False,
                    "acordada": False,                        # já foi espantada pelo mouse alguma vez?
                    "susto": 0.0,                             # quanto tempo ainda corre, assustada
                    "fuga": pygame.Vector2(),                 # e para que lado
                })

    # ------------------------------------------------------------- entrada
    def handle_key(self, key):
        pass

    def handle_click(self, pos):
        self.handle_drag(pos, True)

    def handle_drag(self, pos, pressed):
        # o cursor repele as abelhas esteja o botão apertado ou não (e o dedo, no celular)
        self.cursor = pygame.Vector2(pos) if self.rect.collidepoint(pos) else None

    def handle_release(self, pos):
        pass

    # ------------------------------------------------------------- atualização
    def update(self, dt):
        self.t = getattr(self, "t", 0.0) + dt                 # só para as asinhas baterem
        if self.done:
            return
        self.time_left -= dt
        dt = min(dt, 0.05)                         # um quadro lento não pode teleportar as abelhas
        for abelha in self.abelhas:
            self._mover(abelha, dt)
        if all(a["dentro"] for a in self.abelhas):
            self._terminar()
        elif self.time_left <= 0:
            self._terminar()

    def abrigadas(self):
        return sum(1 for a in self.abelhas if a["dentro"])

    def _mover(self, abelha, dt):
        pos, vel = abelha["pos"], abelha["vel"]
        desejada = pygame.Vector2()                 # fora do abrigo, a abelha fica PARADA
        if abelha["dentro"]:                        # dentro do abrigo ela passeia à vontade
            abelha["ang"] += random.uniform(-2.2, 2.2) * dt
            desejada = pygame.Vector2(math.cos(abelha["ang"]), math.sin(abelha["ang"])) * self.vel_de_passeio
        else:
            para_a_entrada = pygame.Vector2(self.entrada.centerx + 40, self.entrada.centery) - pos
            if abelha["acordada"] and 1 < para_a_entrada.length() < FUNIL_DISTANCIA:   # perto da entrada, o cheiro do mel puxa
                desejada += para_a_entrada.normalize() * FUNIL_FORCA
            desejada += self._empurrao_das_bordas(pos)
        if not abelha["dentro"]:
            fugindo = False
            if self.cursor is not None:
                do_cursor = pos - self.cursor
                distancia = do_cursor.length()
                if distancia < self.raio_de_fuga:           # o mouse chegou perto: a abelha foge dele
                    if distancia == 0:
                        do_cursor, distancia = pygame.Vector2(1, 0), 1.0
                    direcao = (do_cursor / distancia).rotate(abelha["lado"] * DESVIO_DA_FUGA)
                    forca = self.vel_de_fuga * (0.6 + 0.4 * (1 - distancia / self.raio_de_fuga))
                    desejada = direcao * forca
                    abelha["fuga"], abelha["susto"] = direcao, SUSTO_EM_SEGUNDOS
                    abelha["acordada"] = True
                    fugindo = True
            if not fugindo and abelha["susto"] > 0:         # o mouse já saiu, mas ela ainda corre um pouquinho
                abelha["susto"] -= dt
                desejada = abelha["fuga"] * self.vel_de_fuga * 0.8 * max(0.0, abelha["susto"]) / SUSTO_EM_SEGUNDOS
        vel += (desejada - vel) * min(1.0, 7.0 * dt)
        pos += vel * dt

        r = RAIO_DA_ABELHA
        if abelha["dentro"]:
            area = self.interior
        else:
            area = self.rect
        if pos.x < area.left + r:
            pos.x, vel.x = area.left + r, abs(vel.x) * (0.5 if abelha["dentro"] else 0)
        if pos.x > area.right - r:
            pos.x, vel.x = area.right - r, -abs(vel.x) * (0.5 if abelha["dentro"] else 0)
        if pos.y < area.top + r:
            pos.y, vel.y = area.top + r, abs(vel.y) * (0.5 if abelha["dentro"] else 0)
        if pos.y > area.bottom - r:
            pos.y, vel.y = area.bottom - r, -abs(vel.y) * (0.5 if abelha["dentro"] else 0)

        if not abelha["dentro"]:
            for parede in self.paredes:
                self._empurrar_para_fora(abelha, parede)
            if pos.x - r * 0.3 > self.abrigo.left + ESPESSURA_DA_PAREDE and self.abrigo.top < pos.y < self.abrigo.bottom:
                abelha["dentro"] = True

    def _empurrao_das_bordas(self, pos):
        """Um empurrãozinho pra dentro quando a abelha chega perto da borda (elas não grudam nas paredes)."""
        margem = 26.0
        x = max(0.0, (margem - (pos.x - self.rect.left)) / margem) - max(0.0, (margem - (self.rect.right - pos.x)) / margem)
        y = max(0.0, (margem - (pos.y - self.rect.top)) / margem) - max(0.0, (margem - (self.rect.bottom - pos.y)) / margem)
        return pygame.Vector2(x, y) * 45

    def _empurrar_para_fora(self, abelha, parede):
        pos, vel = abelha["pos"], abelha["vel"]
        r = RAIO_DA_ABELHA
        mais_perto = pygame.Vector2(max(parede.left, min(pos.x, parede.right)),
                                    max(parede.top, min(pos.y, parede.bottom)))
        delta = pos - mais_perto
        distancia = delta.length()
        if distancia >= r:
            return
        if distancia == 0:                         # o centro entrou na parede: sai pelo lado mais perto
            lados = [(pos.x - parede.left, pygame.Vector2(-1, 0)), (parede.right - pos.x, pygame.Vector2(1, 0)),
                     (pos.y - parede.top, pygame.Vector2(0, -1)), (parede.bottom - pos.y, pygame.Vector2(0, 1))]
            _, normal = min(lados, key=lambda lado: lado[0])
            pos += normal * (r + 1)
        else:
            normal = delta / distancia
            pos += normal * (r - distancia)
        contra = vel.dot(normal)
        if contra < 0:
            vel -= normal * contra                 # perde a parte da velocidade que ia contra a parede

    def _terminar(self):
        self.done = True
        dentro = self.abrigadas()
        if dentro >= ABELHAS_PARA_SUCESSO:
            self.result = "sucesso"
        elif dentro >= ABELHAS_PARA_PARCIAL:
            self.result = "parcial"
        else:
            self.result = "falha"

    # ------------------------------------------------------------- desenho
    def _madeira(self, tamanho, vertical):
        """O pedaço de madeira de uma parede (as tábuas seguem o comprimento da parede)."""
        largura, altura = tamanho
        base = pixel.fundo_pronto("madeira", max(largura, altura), max(largura, altura))
        if not vertical:
            base = pygame.transform.rotate(base, 90)
        return base.subsurface((0, 0, largura, altura))

    def _desenhar_abrigo(self, surface):
        a, i = self.abrigo, self.interior
        # por dentro: o favo de mel, com a sombra das paredes e o clarão quente que sai pela entrada
        surface.blit(pixel.fundo_pronto("favo", i.width, i.height), i.topleft)
        sombra = pygame.Surface(i.size, pygame.SRCALPHA)
        for k in range(8):
            pygame.draw.rect(sombra, (70, 30, 4, 70 - k * 8), pygame.Rect(0, 0, i.width, i.height).inflate(-2 * k * 2, -2 * k * 2), 4)
        surface.blit(sombra, i.topleft)
        brilho = pygame.Surface((110, self.entrada.height + 70), pygame.SRCALPHA)
        for k in range(6):
            pygame.draw.ellipse(brilho, (255, 236, 150, 24 + k * 7), brilho.get_rect().inflate(-k * 18, -k * 16))
        surface.blit(brilho, (self.entrada.right - 18, self.entrada.centery - brilho.get_height() // 2))
        # as paredes: tábuas de madeira com luz em cima/esquerda, sombra embaixo/direita e contorno escuro
        for parede in self.paredes:
            vertical = parede.height > parede.width
            surface.blit(self._madeira(parede.size, vertical), parede.topleft)
        for parede in self.paredes:
            pygame.draw.rect(surface, (40, 26, 16), parede, 2)
            pygame.draw.line(surface, (226, 178, 118), (parede.left + 2, parede.top + 2), (parede.right - 3, parede.top + 2), 1)
            pygame.draw.line(surface, (226, 178, 118), (parede.left + 2, parede.top + 2), (parede.left + 2, parede.bottom - 3), 1)
        # os batentes da entrada, com a pontinha dourada
        for y in (self.entrada.top - 4, self.entrada.bottom - 4):
            pygame.draw.rect(surface, (40, 26, 16), (a.left - 3, y, ESPESSURA_DA_PAREDE + 6, 8))
            pygame.draw.rect(surface, (250, 206, 70), (a.left - 2, y + 1, ESPESSURA_DA_PAREDE + 4, 6))
            pygame.draw.rect(surface, (255, 240, 150), (a.left - 2, y + 1, ESPESSURA_DA_PAREDE + 4, 2))
        # a setinha que mostra a entrada (balança de leve)
        meio = self.entrada.centery
        vai_e_vem = int(4 * math.sin(getattr(self, "t", 0.0) * 5))
        ponta = a.left - 8 + vai_e_vem
        pygame.draw.polygon(surface, (40, 26, 16), [(ponta + 3, meio), (ponta - 19, meio - 13), (ponta - 19, meio + 13)])
        pygame.draw.polygon(surface, (255, 226, 96), [(ponta, meio), (ponta - 15, meio - 9), (ponta - 15, meio + 9)])
        pygame.draw.polygon(surface, (255, 248, 190), [(ponta - 3, meio), (ponta - 14, meio - 6), (ponta - 14, meio - 1)])
        pixel.texto(surface, "entrada", (a.left - 46, meio + 24), tamanho=11, cor=(255, 246, 214))

    def draw(self, surface):
        pixel.campo(surface, self.rect, "grama", vinheta=False)
        self._desenhar_abrigo(surface)
        pixel.vinheta(surface, self.rect)
        tempo = getattr(self, "t", 0.0)
        for numero, abelha in enumerate(sorted(self.abelhas, key=lambda b: b["pos"].y)):
            x, y = int(abelha["pos"].x), int(abelha["pos"].y)
            if abs(abelha["vel"].x) > 4:
                abelha["virada"] = abelha["vel"].x < 0
            sombra = pygame.Surface((22, 8), pygame.SRCALPHA)
            pygame.draw.ellipse(sombra, (20, 40, 20, 80), sombra.get_rect())
            surface.blit(sombra, sombra.get_rect(center=(x, y + 14)))
            quadro = pixel.abelha(tempo, 1, para_a_esquerda=abelha.get("virada", False), fase=abelha["ang"])
            pixel.colar(surface, quadro, centro=(x, y), sombra=False)

        linha_de_status(surface, self.rect,
                        f"Abrigadas: {self.abrigadas()}/{self.total}   Tempo: {max(0, self.time_left):.1f}s",
                        self.time_left / self.tempo_total)
