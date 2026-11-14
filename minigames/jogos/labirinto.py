# -*- coding: utf-8 -*-
"""Labirinto (Evento 4 — A Seca Chega, a rota até a água).

A jogadora guia a abelha por um labirinto de pedras até a fonte de água (o quadrado azul com a
gota). Clique no quadrado ao lado da abelha, arraste o mouse por cima dos quadrados ou use as
setas do teclado.

O jogo termina na hora se a abelha chegar na água; senão, quando o tempo acaba.

Regras de resultado:
  - chegou na água                                       -> sucesso
  - não chegou, mas andou 75% ou mais do caminho         -> parcial
  - andou menos que isso                                 -> falha
("Andou do caminho" = quantos quadrados da rota mais curta ela já percorreu, no seu melhor
 momento; voltar atrás não tira o que já foi andado.)
"""
import random
from collections import deque

import pygame

from .base import BasePuzzle, difficulty_scale
from . import pixel
from .icones import linha_de_status

LADO = 40
MAXIMO_DE_PASSOS_POR_GESTO = 3

# --- AJUSTES -------------------------------------------------------------
TEMPO_EM_SEGUNDOS = 10.0          # quanto tempo dura o jogo (e aparece na tela)
PROGRESSO_PARA_PARCIAL = 0.75     # andou esta fração (ou mais) da rota e não chegou = parcial

COR_PEDRA = (105, 105, 118)
COR_TRILHA = (232, 222, 150)
COR_AGUA = (110, 170, 220)


class Labirinto(BasePuzzle):
    name = "Labirinto"
    # texto da tela de preparo (os segundos antes de jogar)
    instrucao = (
        "Guie a abelha até a fonte de água (o quadrado azul) antes que o tempo acabe: 10 segundos. "
        "Clique nos quadrados ao lado dela, arraste o mouse por cima deles ou use as setas."
    )

    def __init__(self, rect, difficulty=1, relacao=100):
        self.rect = rect
        self.difficulty = difficulty
        self.done = False
        self.result = None

        self.colunas = min(15, int(round(difficulty_scale(difficulty, relacao, 11, 15))))   # (15 colunas é o que cabe na área)
        self.linhas = min(6, int(round(difficulty_scale(difficulty, relacao, 5, 6))))
        self.tempo_total = TEMPO_EM_SEGUNDOS
        self.time_left = self.tempo_total
        self.movimentos = 0
        self.origem = (rect.centerx - self.colunas * LADO // 2, rect.centery - self.linhas * LADO // 2)

        minimo = int((self.colunas + self.linhas) * 1.5)
        melhor = None
        for _ in range(80):                         # procura um labirinto bem sinuoso; guarda o melhor visto
            self._gerar()
            curta = self._distancia(self.inicio, self.agua)
            if melhor is None or curta > melhor[0]:
                melhor = (curta, self.passagens, self.inicio, self.agua)
            if curta >= minimo:
                break
        self.mais_curta, self.passagens, self.inicio, self.agua = melhor
        self.posicao = self.inicio
        self.visitadas = {self.inicio}
        self.melhor_progresso = 0         # quantos quadrados da rota mais curta já andou (o melhor momento)

    # ------------------------------------------------------------- o labirinto
    def _gerar(self):
        self.passagens = {(x, y): set() for y in range(self.linhas) for x in range(self.colunas)}
        atual = (random.randrange(self.colunas), random.randrange(self.linhas))
        visitadas, pilha = {atual}, [atual]
        while pilha:                                # corredores: busca em profundidade
            x, y = pilha[-1]
            novos = [c for c in self._vizinhas((x, y)) if c not in visitadas]
            if not novos:
                pilha.pop()
                continue
            proxima = random.choice(novos)
            self.passagens[(x, y)].add(proxima)
            self.passagens[proxima].add((x, y))
            visitadas.add(proxima)
            pilha.append(proxima)
        paredes = [(a, b) for a in self.passagens for b in self._vizinhas(a)
                   if a < b and b not in self.passagens[a]]
        random.shuffle(paredes)                     # derruba algumas paredes: surgem atalhos
        for a, b in paredes[:int(self.colunas * self.linhas * 0.12)]:
            self.passagens[a].add(b)
            self.passagens[b].add(a)
        self.inicio = (0, random.randrange(self.linhas))
        self.agua = (self.colunas - 1, random.randrange(self.linhas))

    def _vizinhas(self, celula):
        x, y = celula
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if 0 <= x + dx < self.colunas and 0 <= y + dy < self.linhas:
                yield (x + dx, y + dy)

    def _caminho(self, de, para, limite=None):
        """A rota mais curta entre dois quadrados (lista de quadrados, sem o de partida) ou None."""
        veio = {de: None}
        fila = deque([(de, 0)])
        while fila:
            atual, passos = fila.popleft()
            if atual == para:
                caminho = []
                while atual != de:
                    caminho.append(atual)
                    atual = veio[atual]
                return caminho[::-1]
            if limite is not None and passos >= limite:
                continue
            for proxima in self.passagens[atual]:
                if proxima not in veio:
                    veio[proxima] = atual
                    fila.append((proxima, passos + 1))
        return None

    def _distancia(self, de, para):
        return len(self._caminho(de, para))

    def _celula_em(self, pos):
        x = (pos[0] - self.origem[0]) // LADO
        y = (pos[1] - self.origem[1]) // LADO
        if pos[0] >= self.origem[0] and pos[1] >= self.origem[1] and 0 <= x < self.colunas and 0 <= y < self.linhas:
            return int(x), int(y)
        return None

    # ------------------------------------------------------------- entrada
    def handle_key(self, key):
        direcoes = {pygame.K_UP: (0, -1), pygame.K_w: (0, -1), pygame.K_DOWN: (0, 1), pygame.K_s: (0, 1),
                    pygame.K_LEFT: (-1, 0), pygame.K_a: (-1, 0), pygame.K_RIGHT: (1, 0), pygame.K_d: (1, 0)}
        if key in direcoes and not self.done:
            dx, dy = direcoes[key]
            self._ir_para((self.posicao[0] + dx, self.posicao[1] + dy))

    def handle_click(self, pos):
        celula = self._celula_em(pos)
        if celula is not None:
            self._ir_para(celula)

    def handle_drag(self, pos, pressed):
        if pressed:
            celula = self._celula_em(pos)
            if celula is not None:
                self._ir_para(celula)

    def _ir_para(self, alvo):
        """Anda até o quadrado, passo a passo (só se estiver perto e sem parede no caminho)."""
        if self.done or alvo == self.posicao or alvo not in self.passagens:
            return
        caminho = self._caminho(self.posicao, alvo, MAXIMO_DE_PASSOS_POR_GESTO)
        if caminho is None or len(caminho) > MAXIMO_DE_PASSOS_POR_GESTO:
            return
        for passo in caminho:
            self.posicao = passo
            self.movimentos += 1
            self.visitadas.add(passo)
            self.melhor_progresso = max(self.melhor_progresso, self.mais_curta - self._distancia(passo, self.agua))
            if passo == self.agua:
                self._terminar()
                return

    # ------------------------------------------------------------- atualização
    def update(self, dt):
        self.t = getattr(self, "t", 0.0) + dt                  # só para a abelha bater as asas
        if self.done:
            return
        self.time_left -= dt
        if self.time_left <= 0:
            self._terminar()

    def _terminar(self):
        self.done = True
        self.result = "sucesso" if self.posicao == self.agua else "falha"

    # ------------------------------------------------------------- desenho
    def _area(self, celula):
        return pygame.Rect(self.origem[0] + celula[0] * LADO, self.origem[1] + celula[1] * LADO, LADO, LADO)

    def _montar_paredes(self):
        """As sebes (paredes) como uma imagem pronta: textura de folhas, contorno escuro, luz em cima/esquerda,
        sombra embaixo/direita e a sombra que elas jogam no chão. As paredes não mudam, então é feito uma vez só."""
        espessura = 10
        meio = espessura // 2
        ox, oy = self.origem[0] - self.rect.left, self.origem[1] - self.rect.top
        largura, altura = self.colunas * LADO, self.linhas * LADO
        pedacos = [pygame.Rect(ox - meio, oy - meio, largura + espessura, espessura),
                   pygame.Rect(ox - meio, oy + altura - meio, largura + espessura, espessura),
                   pygame.Rect(ox - meio, oy - meio, espessura, altura + espessura),
                   pygame.Rect(ox + largura - meio, oy - meio, espessura, altura + espessura)]
        for (x, y), abertas in self.passagens.items():
            if (x + 1, y) in self.passagens and (x + 1, y) not in abertas:
                pedacos.append(pygame.Rect(ox + (x + 1) * LADO - meio, oy + y * LADO - meio, espessura, LADO + espessura))
            if (x, y + 1) in self.passagens and (x, y + 1) not in abertas:
                pedacos.append(pygame.Rect(ox + x * LADO - meio, oy + (y + 1) * LADO - meio, LADO + espessura, espessura))
        forma = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        for p in pedacos:
            pygame.draw.rect(forma, (255, 255, 255, 255), p)
        mascara = pygame.mask.from_surface(forma)
        tamanho = self.rect.size

        def deslocada(dx, dy):
            m = pygame.mask.Mask(tamanho)
            m.draw(mascara, (dx, dy))
            return m

        pronta = pygame.Surface(tamanho, pygame.SRCALPHA)
        sombra_no_chao = mascara.to_surface(setcolor=(30, 20, 6, 90), unsetcolor=(0, 0, 0, 0))
        pronta.blit(sombra_no_chao, (3, 5))
        contorno = pygame.mask.Mask(tamanho)
        for dx in (-2, 0, 2):
            for dy in (-2, 0, 2):
                contorno.draw(mascara, (dx, dy))
        contorno.erase(mascara, (0, 0))
        pronta.blit(contorno.to_surface(setcolor=(18, 52, 30, 255), unsetcolor=(0, 0, 0, 0)), (0, 0))
        textura = pixel.fundo_pronto("moita", tamanho[0], tamanho[1]).convert_alpha()
        com_textura = pygame.Surface(tamanho, pygame.SRCALPHA)
        mascara.to_surface(com_textura, setsurface=textura, unsetcolor=(0, 0, 0, 0))
        pronta.blit(com_textura, (0, 0))
        luz = mascara.copy()
        luz.erase(deslocada(2, 2), (0, 0))
        sombra = mascara.copy()
        sombra.erase(deslocada(-2, -2), (0, 0))
        pronta.blit(sombra.to_surface(setcolor=(16, 56, 34, 255), unsetcolor=(0, 0, 0, 0)), (0, 0))
        pronta.blit(luz.to_surface(setcolor=(132, 214, 112, 255), unsetcolor=(0, 0, 0, 0)), (0, 0))
        self._paredes_prontas = pronta

    def draw(self, surface):
        tempo = getattr(self, "t", 0.0)
        pixel.campo(surface, self.rect, "grama", vinheta=False)
        contorno = pygame.Rect(self.origem[0], self.origem[1], self.colunas * LADO, self.linhas * LADO)
        surface.blit(pixel.fundo_pronto("areia", contorno.width, contorno.height), contorno.topleft)     # o caminho
        polen = pixel.fundo_pronto("polen", contorno.width, contorno.height)
        for celula in self.passagens:                                       # por onde a abelha já passou: pólen
            if celula in self.visitadas:
                area = self._area(celula).inflate(-8, -8)
                camada = polen.subsurface(area.move(-contorno.left, -contorno.top)).copy()
                camada.set_alpha(190)
                surface.blit(camada, area.topleft)
                pygame.draw.rect(surface, (255, 240, 150), (area.left, area.top, area.width, 2))
                pygame.draw.rect(surface, (176, 112, 20), (area.left, area.bottom - 2, area.width, 2))
        # a água: o destino
        agua = self._area(self.agua).inflate(-6, -6)
        surface.blit(pixel.fundo_pronto("agua", agua.width, agua.height), agua.topleft)
        pygame.draw.rect(surface, (20, 60, 120), agua, 2)
        pygame.draw.line(surface, (180, 226, 255), (agua.left + 2, agua.top + 2), (agua.right - 3, agua.top + 2), 2)
        pixel.colar(surface, pixel.imagem("gota", 1), centro=agua.center)

        if getattr(self, "_paredes_prontas", None) is None:
            self._montar_paredes()
        surface.blit(self._paredes_prontas, self.rect.topleft)
        pixel.vinheta(surface, self.rect)

        # a abelha, virada para onde andou por último
        atual = self._area(self.posicao).center
        ultima = getattr(self, "_ultima_posicao", atual)
        if atual[0] != ultima[0]:
            self._virada = atual[0] < ultima[0]
        self._ultima_posicao = atual
        sombra = pygame.Surface((26, 9), pygame.SRCALPHA)
        pygame.draw.ellipse(sombra, (20, 30, 10, 90), sombra.get_rect())
        surface.blit(sombra, sombra.get_rect(center=(atual[0], atual[1] + 15)))
        pixel.colar(surface, pixel.abelha(tempo, 1, para_a_esquerda=getattr(self, "_virada", False)), centro=atual, sombra=False)
        linha_de_status(surface, self.rect,
                        f"Movimentos: {self.movimentos}   Tempo: {max(0, self.time_left):.0f}s",
                        self.time_left / self.tempo_total)
