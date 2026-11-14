# -*- coding: utf-8 -*-
"""Antes da Poda (Aurora).

O jardineiro vem atravessando o jardim. Aurora combinou com ele: a colmeia poda as
plantas doentes antes que ele chegue, e ele poupa o resto. Arraste o mouse por cima
das plantas doentes (secas, marrons e tombadas) ou clique nelas para cortar. O que o
traço encostar é cortado, então é preciso desviar das saudáveis.

O jogo termina quando todas as doentes foram cortadas, ou quando o jardineiro chega
ao outro lado.

Regras de resultado (pontos = doentes cortadas, menos 1 por cada saudável cortada por engano):
  - 9 ou 10 pontos   -> sucesso
  - 7 ou 8 pontos    -> parcial
  - 6 ou menos       -> falha
(Sem o desconto das saudáveis, bastaria riscar o jardim todo. Para ignorá-las,
 use PENALIDADE_POR_SAUDAVEL = 0 nos ajustes.)

OS DESENHOS vêm da pasta assets/ do projeto, feitos no Aseprite:
    Flor1.ase, Flor2.ase, Flor3.ase, Flor4.ase, Jardineiro.ase
Se algum não estiver lá, o jogo avisa no terminal e usa um desenho provisório.
"""
import os
import random

import pygame

from . import aseprite, pixel
from .base import BasePuzzle, difficulty_scale
from .icones import escrever

# ============================================================
# AJUSTES -- mexa aqui para balancear e para trocar o visual
# ============================================================
# --- os desenhos ---
PASTA_DOS_DESENHOS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets")
FLORES = ["Flor1", "Flor2", "Flor3", "Flor4"]
TAMANHO_DA_FLOR = 46             # lado maior de cada planta na tela, em pixels
TAMANHO_DO_JARDINEIRO = 50

# --- a dificuldade (o primeiro valor é o do mais fácil, o segundo o do mais difícil) ---
COLUNAS = (10, 10)               # o jardim tem 2 fileiras de plantas: 10 colunas = 20 plantas
PLANTAS_DOENTES = (10, 10)       # quantas das 20 estão doentes
TEMPO_EM_SEGUNDOS = (6.0, 6.0)   # quanto o jardineiro leva para atravessar

# --- o resultado (em pontos: doentes cortadas, menos a penalidade por saudáveis cortadas) ---
MORTAS_PARA_SUCESSO = 9
MORTAS_PARA_PARCIAL = 7
VIVAS_PARA_PARCIAL = 1
VIVAS_PARA_FALHA = 3

# --- a regra do corte ---
MARGEM_DO_CORTE = 0.7            # fração da planta que conta como acerto (o miolo dela)
PASSO_DO_TRACO = 4               # de quantos em quantos pixels o traço é conferido

# --- o visual ---
COR_DA_GRAMA = (170, 205, 130)
COR_DA_TRILHA = (150, 120, 85)
ALTURA_DA_TRILHA = 56
COR_DA_DOENCA = (190, 135, 80)   # as doentes perdem a cor e ficam tingidas desta...
CLAREAR_A_DOENTE = (60, 60, 60)  # ...um pouco mais claras, pro caule não ficar preto...
TOMBO_DA_DOENTE = 14             # ...e tombadas por tantos graus
COR_DO_TRACO = (250, 250, 240)
COR_DO_ACERTO = (90, 170, 80)
COR_DO_ERRO = (220, 60, 50)
COR_DO_TOCO = (105, 75, 50)
DURACAO_DO_EFEITO = 0.4

_AVISADOS = set()


def _provisorio(nome):
    """Um desenho simples pra o jogo funcionar mesmo sem os arquivos."""
    if nome == "Jardineiro":
        s = pygame.Surface((16, 26), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (235, 205, 120), (0, 0, 16, 7))
        pygame.draw.rect(s, (245, 200, 160), (4, 5, 8, 6))
        pygame.draw.rect(s, (50, 90, 130), (3, 11, 10, 15))
    else:
        s = pygame.Surface((20, 30), pygame.SRCALPHA)
        pygame.draw.line(s, (40, 110, 60), (10, 12), (10, 29), 2)
        pygame.draw.circle(s, (225, 90, 90), (10, 8), 7)
    return aseprite.Animacao([s], [100], s.get_size())


def _desenho(nome, alvo):
    """A animação de `nome`, com cerca de `alvo` pixels no lado maior."""
    caminho = os.path.join(PASTA_DOS_DESENHOS, nome + ".ase")
    try:
        animacao = aseprite.carregar(caminho).recortada()
    except ValueError as erro:
        if caminho not in _AVISADOS:
            _AVISADOS.add(caminho)
            print(f"AVISO: Antes da Poda: {erro}; usando um desenho provisório de {nome}.")
        animacao = _provisorio(nome)
    razao = alvo / max(animacao.tamanho)
    quadros = [pygame.transform.smoothscale(q, (max(1, round(q.get_width() * razao)),
                                                max(1, round(q.get_height() * razao))))
               for q in animacao.quadros]
    return aseprite.Animacao(quadros, list(animacao.duracoes), quadros[0].get_size())


def _doente(imagem):
    """A mesma planta, seca e tombada: sem cor própria, para o marrom só querer dizer doença."""
    nova = pygame.transform.grayscale(imagem)
    nova.fill(CLAREAR_A_DOENTE + (0,), special_flags=pygame.BLEND_RGBA_ADD)
    nova.fill(COR_DA_DOENCA + (255,), special_flags=pygame.BLEND_RGBA_MULT)
    return pygame.transform.rotate(nova, TOMBO_DA_DOENTE)


class _Planta:
    def __init__(self, imagem, centro, doente):
        self.imagem = imagem
        self.rect = imagem.get_rect(center=centro)
        self.doente = doente
        self.cortada = False
        self.area_do_corte = self.rect.inflate(-round(self.rect.width * (1 - MARGEM_DO_CORTE)),
                                               -round(self.rect.height * (1 - MARGEM_DO_CORTE)))


class AntesDaPoda(BasePuzzle):
    name = "Antes da Poda"
    # texto da tela de preparo (os segundos antes de jogar)
    instrucao = (
        "O jardineiro está chegando! Arraste o mouse sobre as 10 plantas doentes (secas, "
        "marrons e tombadas) para podá-las antes que ele atravesse o jardim. Rápido, e "
        "cuidado para não cortar as saudáveis."
    )

    def __init__(self, rect, difficulty=1, relacao=100):
        self.rect = rect
        self.difficulty = difficulty
        self.done = False
        self.result = None

        self.total_time = difficulty_scale(difficulty, relacao, *TEMPO_EM_SEGUNDOS)
        self.time_left = self.total_time
        self.tempo = 0.0
        self.saudaveis_cortadas = 0
        self.efeitos = []
        self._traco = []                 # os pontos do traço que está sendo feito

        self.jardineiro = _desenho("Jardineiro", TAMANHO_DO_JARDINEIRO)
        self.plantas = self._montar_plantas(difficulty)
        self.doentes_total = sum(p.doente for p in self.plantas)

    def _montar_plantas(self, difficulty):
        """As plantas em 2 fileiras, em lugares um pouco sorteados."""
        colunas = round(difficulty_scale(difficulty, None, *COLUNAS))
        quantas_doentes = round(difficulty_scale(difficulty, None, *PLANTAS_DOENTES))
        total = colunas * 2
        doentes = [True] * quantas_doentes + [False] * (total - quantas_doentes)
        random.shuffle(doentes)

        imagens = {nome: _desenho(nome, TAMANHO_DA_FLOR).quadros[0] for nome in FLORES}
        largura = self.rect.width / colunas
        altura = (self.rect.height - ALTURA_DA_TRILHA) / 2
        plantas = []
        for i, doente in enumerate(doentes):
            coluna, fileira = i % colunas, i // colunas
            centro = (self.rect.left + largura * (coluna + 0.5) + random.uniform(-4, 4),
                      self.rect.top + altura * (fileira + 0.5) + random.uniform(-4, 4))
            imagem = imagens[random.choice(FLORES)]
            plantas.append(_Planta(_doente(imagem) if doente else imagem, centro, doente))
        return plantas

    # ------------------------------------------------------------ contas
    @property
    def doentes_restantes(self):
        return sum(p.doente and not p.cortada for p in self.plantas)

    def _finish(self):
        self.done = True
        mortas = self.doentes_total - self.doentes_restantes
        vivas = self.saudaveis_cortadas
        if mortas < MORTAS_PARA_PARCIAL or vivas >= VIVAS_PARA_FALHA:
            self.result = "falha"
        elif mortas >= MORTAS_PARA_SUCESSO and vivas < VIVAS_PARA_PARCIAL:
            self.result = "sucesso"
        else:
            self.result = "parcial"

    # ------------------------------------------------------------ o corte
    def _cortar_em(self, ponto):
        for planta in self.plantas:
            if not planta.cortada and planta.area_do_corte.collidepoint(ponto):
                planta.cortada = True
                if not planta.doente:
                    self.saudaveis_cortadas += 1
                self.efeitos.append({"planta": planta, "t": 0.0})

    def _cortar_ate(self, pos):
        """Corta tudo no caminho desde o último ponto (o mouse pode andar rápido)."""
        ax, ay = self._traco[-1]
        passos = max(1, int(max(abs(pos[0] - ax), abs(pos[1] - ay)) / PASSO_DO_TRACO))
        for i in range(1, passos + 1):
            self._cortar_em((ax + (pos[0] - ax) * i / passos, ay + (pos[1] - ay) * i / passos))
        self._traco.append(pos)
        if self.doentes_restantes == 0:
            self._finish()

    # ------------------------------------------------------------ jogo
    def update(self, dt):
        # (os efeitos continuam depois do fim: o último corte termina de cair)
        for efeito in self.efeitos:
            efeito["t"] += dt
        self.efeitos = [e for e in self.efeitos if e["t"] < DURACAO_DO_EFEITO]
        if self.done:
            return
        self.tempo += dt
        self.time_left -= dt
        if self.time_left <= 0:
            self._finish()

    def handle_key(self, key):
        pass

    def handle_click(self, pos):
        if self.done or not self.rect.collidepoint(pos):
            return
        self._traco = [pos]
        self._cortar_ate(pos)

    def handle_drag(self, pos, pressed):
        if self.done or not pressed or not self.rect.collidepoint(pos):
            self._traco = []          # saiu do jardim: o traço recomeça quando voltar
            return
        if not self._traco:
            self._traco = [pos]
        self._cortar_ate(pos)

    def handle_release(self, pos):
        self._traco = []

    # ------------------------------------------------------------ desenho
    def draw(self, surface):
        clip_anterior = surface.get_clip()
        pixel.campo(surface, self.rect, "grama", vinheta=False)
        surface.set_clip(self.rect)
        trilha = pygame.Rect(self.rect.left, self.rect.bottom - ALTURA_DA_TRILHA, self.rect.width, ALTURA_DA_TRILHA)
        # a trilha de terra por onde o jardineiro anda, com a beirada da grama
        surface.blit(pixel.fundo_pronto("terra", trilha.width, trilha.height), trilha.topleft)
        pygame.draw.rect(surface, (44, 28, 18), (trilha.left, trilha.top, trilha.width, 4))
        pygame.draw.rect(surface, (122, 90, 60), (trilha.left, trilha.top + 4, trilha.width, 2))
        pygame.draw.rect(surface, (40, 24, 16), (trilha.left, trilha.bottom - 3, trilha.width, 3))

        toco = pixel.imagem("toco", 1)
        for planta in self.plantas:
            base = planta.rect.midbottom
            sombra = pygame.Surface((planta.rect.width, 12), pygame.SRCALPHA)
            pygame.draw.ellipse(sombra, (20, 50, 20, 90), sombra.get_rect())
            surface.blit(sombra, sombra.get_rect(midbottom=(base[0], base[1] + 4)))
            if planta.cortada:
                pixel.colar(surface, toco, centro=(base[0], base[1] - 7), sombra=False)
            else:
                pixel.colar(surface, planta.imagem, canto=planta.rect.topleft)

        for efeito in self.efeitos:
            progresso = efeito["t"] / DURACAO_DO_EFEITO
            planta = efeito["planta"]
            caindo = planta.imagem.copy()
            caindo.set_alpha(int(255 * (1 - progresso)))
            surface.blit(caindo, planta.rect.move(0, round(30 * progresso)))
            cor = COR_DO_ACERTO if planta.doente else COR_DO_ERRO
            pygame.draw.circle(surface, cor, planta.rect.center, 14 + round(24 * progresso), 3)

        if len(self._traco) > 1:                                  # o rastro do corte: um brilho de lâmina
            pygame.draw.lines(surface, (150, 176, 180), False, self._traco[-12:], 6)
            pygame.draw.lines(surface, COR_DO_TRACO, False, self._traco[-12:], 3)

        fracao = 1.0 - max(0.0, self.time_left) / self.total_time
        quadro = self.jardineiro.quadro_em(self.tempo)
        caminho = self.rect.width - quadro.get_width()
        pixel.colar(surface, quadro, canto=(self.rect.left + round(caminho * fracao), trilha.bottom - quadro.get_height() - 3))
        surface.set_clip(clip_anterior)

        pixel.vinheta(surface, self.rect)
        cor_do_texto = COR_DO_ERRO if self.saudaveis_cortadas else (40, 40, 40)
        escrever(surface, f"Doentes: {self.doentes_restantes}/{self.doentes_total}   "
                          f"Saudáveis cortadas: {self.saudaveis_cortadas}   "
                          f"Tempo: {max(0, self.time_left):.1f}s", (self.rect.left, self.rect.bottom + 10), cor=cor_do_texto)
        pixel.barra(surface, pygame.Rect(self.rect.left, self.rect.bottom + 26, self.rect.width, 10),
                    max(0.0, self.time_left) / self.total_time)
