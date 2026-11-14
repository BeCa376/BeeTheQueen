# -*- coding: utf-8 -*-
"""Rota de Voo (Nectar, Evento 1 — O Novo Jardim).

Estilo "Zip": arraste de flor em flor, preenchendo TODAS as celulas do
campo sem repetir nenhuma, passando pelos pontos numerados em ordem
crescente. Algumas celulas sao barreiras (intransponiveis).

Como jogar:
  - Clique na flor numero 1 para comecar.
  - Arraste (mantendo o botao pressionado) para celulas vizinhas
    (cima/baixo/esquerda/direita) ainda nao visitadas.
  - Os pontos numerados so podem ser visitados na ordem certa.
  - Complete cobrindo TODAS as celulas e terminando no ultimo numero.
  - Para DESFAZER ("dar ré"): arraste de volta por cima do proprio caminho, ou clique numa
    celula dele. Some so o que veio depois daquela celula, o resto fica.

O jogo termina na hora se o caminho for completado; senao, quando o tempo acaba.

Regras de resultado (ate que numero voce ligou, quando o jogo termina):
  - 9 ou 10   -> sucesso      (completar tudo tambem e sucesso)
  - 7 ou 8    -> parcial
  - 6 ou menos -> falha
"""
import functools
import math
import os
import random

import pygame

from . import pixel
from .base import BasePuzzle
from .icones import linha_de_status

DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]

# --- AJUSTES -------------------------------------------------------------
COLUNAS, LINHAS = 5, 4            # o tamanho do quadrado
BARREIRAS = 0                     # quantas celulas bloqueadas (0 = nenhuma)
NUMEROS = 10                      # os pontos numerados vao de 1 ate este
TEMPO_EM_SEGUNDOS = 8.0          # quanto tempo dura o jogo (e aparece na tela)
NUMEROS_PARA_SUCESSO = 9          # ligou ate este numero (ou mais) = sucesso
NUMEROS_PARA_PARCIAL = 7          # daqui ate o de cima = parcial; abaixo disto = falha

CELL_EMPTY = (235, 235, 225)
CELL_VISITED = (240, 200, 60)
CELL_BARRIER = (90, 90, 90)
CELL_HEAD = (214, 158, 46)
CHECKPOINT_DONE = (120, 190, 110)
CHECKPOINT_NEXT = (230, 150, 60)
CHECKPOINT_FUTURE = (140, 150, 200)


def _neighbors(cell, cell_set, visited):
    x, y = cell
    return [(x + dx, y + dy) for dx, dy in DIRS
            if (x + dx, y + dy) in cell_set and (x + dx, y + dy) not in visited]


def _degree(cell, cell_set, visited):
    return len(_neighbors(cell, cell_set, visited))


def _dfs_hamiltonian(path, visited, cell_set, total):
    if len(path) == total:
        return True
    neighbors = _neighbors(path[-1], cell_set, visited)
    # heuristica de Warnsdorff: tenta primeiro quem tem menos opcoes futuras
    neighbors.sort(key=lambda n: _degree(n, cell_set, visited))
    for n in neighbors:
        visited.add(n)
        path.append(n)
        if _dfs_hamiltonian(path, visited, cell_set, total):
            return True
        path.pop()
        visited.remove(n)
    return False


def _serpentine_path(cols, rows):
    """Caminho garantido (cobre a grade inteira, sem barreiras) -- usado
    como reserva caso a geracao aleatoria com barreiras falhe."""
    path = []
    for y in range(rows):
        xs = range(cols) if y % 2 == 0 else range(cols - 1, -1, -1)
        for x in xs:
            path.append((x, y))
    return path


def _generate_path_and_barriers(cols, rows, n_barriers, max_tries=60):
    all_cells = [(x, y) for y in range(rows) for x in range(cols)]
    for _ in range(max_tries):
        barriers = set(random.sample(all_cells, n_barriers)) if n_barriers else set()
        cell_set = set(c for c in all_cells if c not in barriers)
        start = random.choice(list(cell_set))
        visited = {start}
        path = [start]
        if _dfs_hamiltonian(path, visited, cell_set, len(cell_set)):
            return path, barriers
    # reserva: sem barreiras, caminho em zigue-zague garantido
    return _serpentine_path(cols, rows), set()


class RotaDeVoo(BasePuzzle):
    name = "Rota de Voo"
    # texto da tela de preparo (os segundos antes de jogar)
    instrucao = (
        "Clique na flor número 1 e arraste de número em número, até o 10, passando por TODAS as "
        "células sem repetir nenhuma. Errou o caminho? Clique em qualquer ponto dele (ou arraste de volta por cima) "
        "para voltar até ali e tentar outro."
    )

    def __init__(self, rect, difficulty=1, relacao=100):
        self.rect = rect
        self.difficulty = difficulty
        self.done = False
        self.result = None

        self.cols, self.rows, n_barriers = COLUNAS, LINHAS, BARREIRAS

        self.path_solution, self.barriers = _generate_path_and_barriers(
            self.cols, self.rows, n_barriers)
        self.total_cells = len(self.path_solution)

        # os pontos numerados, de 1 ate NUMEROS, espalhados pelo caminho (sempre inicio e fim)
        n_checkpoints = min(NUMEROS, self.total_cells)
        idxs = sorted(set(round(i * (self.total_cells - 1) / (n_checkpoints - 1))
                           for i in range(n_checkpoints)))
        self.checkpoint_cell_of_number = {}
        self.checkpoint_number_of_cell = {}
        for num, idx in enumerate(idxs, start=1):
            cell = self.path_solution[idx]
            self.checkpoint_cell_of_number[num] = cell
            self.checkpoint_number_of_cell[cell] = num
        self.total_checkpoints = len(idxs)
        self.final_cell = self.path_solution[-1]

        cell_w = rect.width / self.cols
        cell_h = rect.height / self.rows
        self.cell_size = (cell_w, cell_h)

        self.player_path = []
        self.visited = set()
        self.next_checkpoint = 1
        self.dragging = False
        self._ultimo_ponto = None         # onde o mouse estava no último movimento (para não perder células)
        self.time_left = TEMPO_EM_SEGUNDOS
        self.total_time = TEMPO_EM_SEGUNDOS
        self.t = 0.0                    # só para as animações (a abelha batendo asa, a flor pulsando)

    # ------------------------------------------------------------ helpers
    def _cell_at(self, pos):
        gx = int((pos[0] - self.rect.left) // self.cell_size[0])
        gy = int((pos[1] - self.rect.top) // self.cell_size[1])
        if 0 <= gx < self.cols and 0 <= gy < self.rows:
            return gx, gy
        return None

    def _cell_center(self, cell):
        gx, gy = cell
        cw, ch = self.cell_size
        return (self.rect.left + gx * cw + cw / 2, self.rect.top + gy * ch + ch / 2)

    def _voltar_ate(self, cell):
        """"Dar ré": a jogadora voltou por cima do proprio caminho. Tudo o que veio DEPOIS
        daquela celula e desfeito (a celula em si, e o que veio antes, ficam)."""
        while self.player_path[-1] != cell:
            solta = self.player_path.pop()
            self.visited.discard(solta)
            if solta in self.checkpoint_number_of_cell:
                self.next_checkpoint -= 1

    def numeros_ligados(self):
        return self.next_checkpoint - 1

    # ------------------------------------------------------------- update
    def update(self, dt):
        self.t += dt
        if self.done:
            return
        self.time_left -= dt
        if self.time_left <= 0:
            self._finish_por_tempo()

    def handle_key(self, key):
        pass

    # ----------------------------------------------------------- o caminho
    def _pode_entrar(self, cell):
        """A célula está livre e (se tiver número) é a próxima flor da ordem?"""
        if cell in self.barriers or cell in self.visited:
            return False
        numero = self.checkpoint_number_of_cell.get(cell)
        return numero is None or numero == self.next_checkpoint

    def _entrar(self, cell):
        """A abelha avança para `cell` (que tem que ser vizinha da ponta do caminho)."""
        self.player_path.append(cell)
        self.visited.add(cell)
        if self.checkpoint_number_of_cell.get(cell) is not None:
            self.next_checkpoint += 1
        if len(self.player_path) == self.total_cells and cell == self.final_cell:
            self._finish_success()

    def _no_miolo(self, pos, cell):
        """O mouse está no miolo da célula (e não raspando na beirada)? Só o miolo vale para voltar atrás,
        assim passar rente ao canto de uma célula do caminho não desfaz nada sem querer."""
        cw, ch = self.cell_size
        x0 = self.rect.left + cell[0] * cw
        y0 = self.rect.top + cell[1] * ch
        return x0 + cw * 0.22 <= pos[0] < x0 + cw * 0.78 and y0 + ch * 0.22 <= pos[1] < y0 + ch * 0.78

    def _passo(self, pos, anterior):
        """O mouse passou por `pos` (vindo de `anterior`): anda, volta ou ignora."""
        cell = self._cell_at(pos)
        if cell is None or cell in self.barriers or not self.player_path:
            return
        ponta = self.player_path[-1]
        if cell == ponta:
            return
        if cell in self.visited:
            if self._no_miolo(pos, cell):
                self._voltar_ate(cell)  # voltou por cima do proprio caminho ("dar ré")
            return
        dx, dy = cell[0] - ponta[0], cell[1] - ponta[1]
        if abs(dx) + abs(dy) == 1:
            if self._pode_entrar(cell):
                self._entrar(cell)
        elif abs(dx) == 1 and abs(dy) == 1:
            # a mão cortou o canto, indo em diagonal: a abelha passa por uma das duas células do meio
            # (a que está mais perto de onde o mouse vinha) e chega na que o mouse alcançou
            meios = [(ponta[0] + dx, ponta[1]), (ponta[0], ponta[1] + dy)]
            meios = [m for m in meios if self._pode_entrar(m)]
            if meios:
                meio = min(meios, key=lambda m: math.dist(self._cell_center(m), anterior))
                self._entrar(meio)
                if not self.done and self._pode_entrar(cell):
                    self._entrar(cell)

    def handle_click(self, pos):
        if self.done:
            return
        self._ultimo_ponto = pos
        cell = self._cell_at(pos)
        if cell is None or cell in self.barriers:
            return
        if not self.player_path:
            if cell == self.checkpoint_cell_of_number[1]:
                self.player_path = [cell]
                self.visited = {cell}
                self.next_checkpoint = 2
                self.dragging = True
            return
        ponta = self.player_path[-1]
        if cell == ponta:
            self.dragging = True  # retomar o arrasto de onde parou
        elif cell in self.visited:
            self._voltar_ate(cell)  # clicou numa celula do proprio caminho: desfaz ate ali e segue dela
            self.dragging = True
        elif abs(cell[0] - ponta[0]) + abs(cell[1] - ponta[1]) == 1:
            self.dragging = True  # clicou numa vizinha da ponta: segue por ela
            if self._pode_entrar(cell):
                self._entrar(cell)

    def handle_drag(self, pos, pressed):
        if self.done or not pressed or not self.dragging or not self.player_path:
            self._ultimo_ponto = pos
            return
        anterior = self._ultimo_ponto or pos
        # o mouse pode andar vários pixels entre um quadro e outro: confere o caminho INTEIRO que ele fez,
        # de 8 em 8 pixels, para não pular nenhuma célula
        passos = max(1, int(math.dist(anterior, pos) / 8))
        ponto_antes = anterior
        for k in range(1, passos + 1):
            ponto = (anterior[0] + (pos[0] - anterior[0]) * k / passos, anterior[1] + (pos[1] - anterior[1]) * k / passos)
            self._passo(ponto, ponto_antes)
            ponto_antes = ponto
            if self.done:
                break
        self._ultimo_ponto = pos

    def handle_release(self, pos):
        self.dragging = False
        self._ultimo_ponto = None

    def _finish_success(self):
        """Completou o caminho inteiro: acabou, sem esperar o tempo."""
        self.done = True
        self.dragging = False
        self.result = "sucesso"

    def _finish_por_tempo(self):
        """O tempo acabou: vale ate que numero o caminho chegou."""
        self.done = True
        self.dragging = False
        ligados = self.numeros_ligados()
        if ligados >= NUMEROS_PARA_SUCESSO:
            self.result = "sucesso"
        elif ligados >= NUMEROS_PARA_PARCIAL:
            self.result = "parcial"
        else:
            self.result = "falha"

    # --------------------------------------------------------------- o destaque do começo
    def _brilho_do_comeco(self, surface, cx, cy, pulso):
        """Um sol atrás da flor 1: um disco claro, raios dourados girando e um halo que pulsa (bem visível na grama)."""
        lado = 200
        folha = pygame.Surface((lado, lado), pygame.SRCALPHA)
        c = lado / 2
        pygame.draw.circle(folha, (255, 250, 200, 120 + int(40 * pulso)), (c, c), int(46 + 6 * pulso))
        for i in range(12):
            ang = self.t * 0.9 + i * (2 * math.pi / 12)
            raio = 80 + 10 * pulso if i % 2 == 0 else 64 + 8 * pulso
            ponta = (c + math.cos(ang) * raio, c + math.sin(ang) * raio)
            a1 = (c + math.cos(ang - 0.15) * 30, c + math.sin(ang - 0.15) * 30)
            a2 = (c + math.cos(ang + 0.15) * 30, c + math.sin(ang + 0.15) * 30)
            pygame.draw.polygon(folha, (255, 236, 110, 215), [a1, ponta, a2])
            pygame.draw.polygon(folha, (214, 150, 20, 235), [a1, ponta, a2], 2)
        pygame.draw.circle(folha, (255, 244, 160, 200), (c, c), int(46 + 6 * pulso), 4)
        surface.blit(folha, (int(cx - c), int(cy - c)))

    def _aviso_do_comeco(self, surface, cx, cy, pulso):
        """"COMECE AQUI!" com uma setinha que pula, por cima ou por baixo da flor (onde houver espaço)."""
        em_cima = cy - 62 > self.rect.top + 18
        pulo = int(5 * pulso)
        y_texto = cy - 56 - pulo if em_cima else cy + 56 + pulo
        pixel.texto(surface, "COMECE AQUI!", (cx, y_texto), tamanho=13, cor=(255, 246, 176))
        if em_cima:
            ponta = (cx, y_texto + 20)
            pontos = [(ponta[0] - 8, ponta[1] - 8), (ponta[0] + 8, ponta[1] - 8), ponta]
        else:
            ponta = (cx, y_texto - 20)
            pontos = [(ponta[0] - 8, ponta[1] + 8), (ponta[0] + 8, ponta[1] + 8), ponta]
        pygame.draw.polygon(surface, (46, 30, 20), [(x + (0 if i == 2 else 0), y) for i, (x, y) in enumerate(pontos)], 0)
        pygame.draw.polygon(surface, (255, 226, 96), pontos, 0)
        pygame.draw.polygon(surface, (46, 30, 20), pontos, 2)

    # --------------------------------------------------------------- draw
    def draw(self, surface):
        pixel.campo(surface, self.rect, "grama", vinheta=False)
        cw, ch = self.cell_size
        polen = pixel.fundo_pronto("polen", self.rect.width, self.rect.height)

        # as divisas das células (uma linha escura e uma clara ao lado, como um sulco na grama)
        for gx in range(1, self.cols):
            x = self.rect.left + round(gx * cw)
            pygame.draw.line(surface, (36, 104, 48), (x - 1, self.rect.top), (x - 1, self.rect.bottom - 1), 2)
            pygame.draw.line(surface, (140, 214, 100), (x + 1, self.rect.top), (x + 1, self.rect.bottom - 1), 1)
        for gy in range(1, self.rows):
            y = self.rect.top + round(gy * ch)
            pygame.draw.line(surface, (36, 104, 48), (self.rect.left, y - 1), (self.rect.right - 1, y - 1), 2)
            pygame.draw.line(surface, (140, 214, 100), (self.rect.left, y + 1), (self.rect.right - 1, y + 1), 1)

        for gy in range(self.rows):
            for gx in range(self.cols):
                cell = (gx, gy)
                area = pygame.Rect(self.rect.left + round(gx * cw) + 3, self.rect.top + round(gy * ch) + 3,
                                   round((gx + 1) * cw) - round(gx * cw) - 6, round((gy + 1) * ch) - round(gy * ch) - 6)
                if cell in self.barriers:
                    pixel.carta(surface, area, "madeira")
                elif cell in self.visited:                       # o pólen que a abelha deixou na célula
                    camada = polen.subsurface(area.move(-self.rect.left, -self.rect.top)).copy()
                    camada.set_alpha(215)
                    surface.blit(camada, area.topleft)
                    pygame.draw.rect(surface, (255, 240, 150), (area.left, area.top, area.width, 2))
                    pygame.draw.rect(surface, (176, 112, 20), (area.left, area.bottom - 2, area.width, 2))
        pixel.vinheta(surface, self.rect)

        # a trilha de pólen: um canudo dourado com luz em cima
        if len(self.player_path) > 1:
            pontos = [self._cell_center(c) for c in self.player_path]
            pygame.draw.lines(surface, (120, 74, 14), False, pontos, 12)
            pygame.draw.lines(surface, (240, 176, 44), False, pontos, 8)
            pygame.draw.lines(surface, (255, 228, 120), False, pontos, 3)
            for ponto in pontos:
                pygame.draw.circle(surface, (240, 176, 44), (int(ponto[0]), int(ponto[1])), 6)
                pygame.draw.circle(surface, (255, 236, 150), (int(ponto[0]) - 1, int(ponto[1]) - 1), 3)

        # as flores numeradas (as do assets): TODAS balançam e sobem e descem de leve; as já ligadas ficam com um
        # visto; a PRÓXIMA pulsa com um brilho; e a PRIMEIRA, antes de começar, grita: brilho grande, raios girando,
        # a flor maior e o aviso "COMECE AQUI!"
        clip_anterior = surface.get_clip()
        surface.set_clip(self.rect)                                 # os raios não passam da moldura
        for num, cell in sorted(self.checkpoint_cell_of_number.items()):
            cx, cy = self._cell_center(cell)
            angulo = math.sin(self.t * 2.2 + num * 1.3) * 6
            subida = math.sin(self.t * 3.0 + num) * 2.5
            escala = 1.0
            if num < self.next_checkpoint:
                estado = "feita"
            elif num == self.next_checkpoint:
                estado = "proxima"
                pulso = (math.sin(self.t * 6) + 1) / 2
                if num == 1:                                       # o começo do caminho: tem que dar na vista
                    self._brilho_do_comeco(surface, cx, cy, pulso)
                    escala = 1.2 + 0.1 * pulso
                else:
                    brilho = pygame.Surface((110, 110), pygame.SRCALPHA)
                    for i in range(6):
                        pygame.draw.circle(brilho, (255, 240, 130, 60 + int(40 * pulso)), (55, 55), 50 - i * 7 + int(3 * pulso))
                    surface.blit(brilho, (int(cx) - 55, int(cy) - 55))
                    escala = 1.06 + 0.1 * pulso
            else:
                estado = "futura"
            flor = pygame.transform.rotozoom(_flor(num, estado), angulo, escala)
            pixel.colar(surface, flor, (cx, cy - 2 + subida))
            if estado == "proxima" and num == 1:
                self._aviso_do_comeco(surface, cx, cy, pulso)

        surface.set_clip(clip_anterior)

        # a abelha na ponta do caminho (virada para onde está indo)
        if self.player_path:
            hx, hy = self._cell_center(self.player_path[-1])
            esquerda = len(self.player_path) > 1 and self.player_path[-1][0] < self.player_path[-2][0]
            pixel.colar(surface, pixel.abelha(self.t, 1, para_a_esquerda=esquerda), (hx + 12, hy - 12))

        linha_de_status(surface, self.rect,
                        f"Arraste da flor 1 até a {self.total_checkpoints}, cobrindo tudo  "
                        f"Números ligados: {self.numeros_ligados()}/{self.total_checkpoints}  "
                        f"Tempo: {max(0, self.time_left):.0f}s",
                        self.time_left / self.total_time)


@functools.lru_cache(maxsize=None)
def _flor(numero, estado):
    """A flor numerada de assets/flor_N.png, do tamanho de um ícone. Estados: futura, proxima, feita (com um visto)."""
    caminho = os.path.join(pixel.PASTA_DOS_DESENHOS, f"flor_{numero}.png")
    try:
        original = pygame.image.load(caminho).convert_alpha()
    except (pygame.error, FileNotFoundError):
        original = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.circle(original, (236, 112, 160), (32, 32), 28)
    flor = pygame.transform.smoothscale(original, (60, 60))
    if estado == "feita":
        flor = pixel.tingir(flor, (236, 255, 228))
        flor.set_alpha(235)
        visto = pygame.Surface((22, 22), pygame.SRCALPHA)
        pygame.draw.circle(visto, (30, 100, 50), (11, 11), 11)
        pygame.draw.circle(visto, (96, 200, 90), (11, 11), 9)
        pygame.draw.lines(visto, (255, 255, 255), False, [(5, 11), (9, 15), (17, 6)], 3)
        flor = flor.copy()
        flor.blit(visto, (38, 0))
    return flor
