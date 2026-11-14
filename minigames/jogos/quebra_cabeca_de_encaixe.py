# -*- coding: utf-8 -*-
"""Quebra-cabeça de Encaixe (Evento 5 — A Fazenda com Pesticidas, restaurar um habitat seguro).

As peças são pedaços do habitat: flores, árvores, água e abrigos. Toda peça tem exatamente
3 quadrados (reta ou em L), e o tabuleiro 6x5 é dividido em 10 delas. A jogadora arrasta cada peça
para o tabuleiro e precisa ENCAIXAR TODAS, sem sobrepor e sem sobrar espaço. Além de caber,
o habitat só é seguro se as flores ficarem encostadas na água e as árvores encostadas no abrigo.
Para mudar uma peça de lugar, arraste-a de novo (soltar fora do tabuleiro a devolve à bandeja).

O jogo termina na hora se todas as 10 peças forem encaixadas; senão, quando o tempo acaba.

Regras de resultado (peças encaixadas quando o jogo termina):
  - 9 ou 10 peças  -> sucesso
  - 7 ou 8 peças   -> parcial
  - 0 a 6 peças    -> falha
(A regra "flor junto da água, árvore junto do abrigo" fica DESLIGADA; para ligá-la, use
 REGRA_DE_VIZINHANCA = True: aí ela também conta, e quem não a cumpre não passa de parcial.)
O quebra-cabeça é montado a partir de uma solução, então sempre dá para resolver.
"""
import random

import pygame

from .base import BasePuzzle
from .icones import CINZA_CLARO, VERDE, desenhar_icone, linha_de_status

LADO = 40                                  # o quadrado do tabuleiro, em pixels

# --- AJUSTES -------------------------------------------------------------
TEMPO_EM_SEGUNDOS = 40.0          # quanto tempo dura o jogo (e aparece na tela)
COLUNAS, LINHAS = 6, 5            # o tabuleiro (30 quadrados; precisa ser múltiplo de 3)
TAMANHO_DA_PECA = 3               # toda peça tem exatamente 3 quadrados (reta ou em L)
PECAS = COLUNAS * LINHAS // TAMANHO_DA_PECA      # = 10 peças
PECAS_PARA_SUCESSO = 9            # este tanto (ou mais) encaixado = sucesso
PECAS_PARA_PARCIAL = 7            # daqui até o de cima = parcial; abaixo disto = falha
REGRA_DE_VIZINHANCA = False       # True = flor junto da água e árvore junto do abrigo também contam

COR_DO_TABULEIRO = (205, 185, 140)
COR_DA_LINHA = (170, 150, 105)

# tipo -> (cor, ícone, o tipo que precisa estar encostado, ou None)
TIPOS = {
    "flor": ((240, 165, 195), "flor", "agua"),
    "arvore": ((115, 175, 105), "folha", "abrigo"),
    "agua": ((120, 175, 225), "gota", None),
    "abrigo": ((195, 155, 105), "favo", None),
}
VIZINHOS = ((1, 0), (-1, 0), (0, 1), (0, -1))

# as 6 formas possíveis de uma peça de 3 quadrados: 2 retas e 4 em L
FORMAS_DE_3 = (
    ((0, 0), (1, 0), (2, 0)),
    ((0, 0), (0, 1), (0, 2)),
    ((0, 0), (1, 0), (0, 1)),
    ((0, 0), (1, 0), (1, 1)),
    ((0, 0), (0, 1), (1, 1)),
    ((1, 0), (0, 1), (1, 1)),
)


class QuebraCabecaDeEncaixe(BasePuzzle):
    name = "Quebra-cabeça de Encaixe"
    # texto da tela de preparo (os segundos antes de jogar)
    instrucao = (
        f"Arraste as {PECAS} peças para o tabuleiro e monte o habitat: elas precisam caber, sem sobrepor e "
        f"sem sobrar espaço. Encaixe o máximo que conseguir em {TEMPO_EM_SEGUNDOS:.0f} segundos."
    )

    def __init__(self, rect, difficulty=1, relacao=100):
        self.rect = rect
        self.difficulty = difficulty
        self.done = False
        self.result = None

        self.colunas, self.linhas = min(8, COLUNAS), min(5, LINHAS)       # (até 8x5 cabe com a bandeja)
        if (self.colunas * self.linhas) % TAMANHO_DA_PECA:
            raise ValueError(f"O tabuleiro {self.colunas}x{self.linhas} não se divide em peças de {TAMANHO_DA_PECA}.")
        self.tempo_total = TEMPO_EM_SEGUNDOS
        self.time_left = self.tempo_total
        self.tabuleiro = pygame.Rect(rect.left + 8, rect.centery - self.linhas * LADO // 2,
                                     self.colunas * LADO, self.linhas * LADO)

        self._montar_pecas()
        self._montar_bandeja()
        self.posicoes = {}                              # peça -> (coluna, linha) do canto de cima à esquerda
        self.ocupacao = {}                              # (coluna, linha) -> peça
        self.segurando = None                           # a peça que está sendo arrastada
        self.pega = (0, 0)                              # onde, dentro da peça, a jogadora pegou
        self.ponteiro = (0, 0)

    # ------------------------------------------------------------- a montagem do quebra-cabeça
    def _montar_pecas(self):
        """Divide o tabuleiro em peças de 3 quadrados (a solução) e dá um tipo a cada uma."""
        regioes = self._dividir_em_trios()
        tipos, regras = self._sortear_tipos(regioes)
        self.regras_ativas = regras and REGRA_DE_VIZINHANCA
        self.pecas = []
        for i, (celulas, tipo) in enumerate(zip(regioes, tipos)):
            x0 = min(c[0] for c in celulas)
            y0 = min(c[1] for c in celulas)
            forma = sorted((x - x0, y - y0) for x, y in celulas)
            self.pecas.append({"id": i, "tipo": tipo, "forma": forma, "solucao": (x0, y0),
                               "largura": max(f[0] for f in forma) + 1, "altura": max(f[1] for f in forma) + 1})
        random.shuffle(self.pecas)
        self.pecas_por_id = {p["id"]: p for p in self.pecas}

    def _dividir_em_trios(self):
        """Cobre o tabuleiro inteiro com peças de 3 quadrados, sorteando as formas.
        Vai preenchendo sempre o primeiro quadrado livre (de cima para baixo, da esquerda
        para a direita); se uma escolha deixa um buraco impossível, volta atrás e tenta outra."""
        livres = {(x, y) for y in range(self.linhas) for x in range(self.colunas)}
        regioes = []

        def preencher():
            if not livres:
                return True
            primeiro = min(livres, key=lambda c: (c[1], c[0]))
            formas = list(FORMAS_DE_3)
            random.shuffle(formas)
            for forma in formas:
                ancora = min(forma, key=lambda c: (c[1], c[0]))      # o quadrado da forma que cai no `primeiro`
                celulas = [(primeiro[0] + dx - ancora[0], primeiro[1] + dy - ancora[1]) for dx, dy in forma]
                if all(c in livres for c in celulas):
                    livres.difference_update(celulas)
                    regioes.append(celulas)
                    if preencher():
                        return True
                    regioes.pop()
                    livres.update(celulas)
            return False

        if not preencher():
            raise ValueError(f"Não deu para dividir o tabuleiro {self.colunas}x{self.linhas} em peças de 3.")
        return regioes

    def _sortear_tipos(self, regioes):
        """Tipos tais que, NA SOLUÇÃO, flores encostam em água e árvores em abrigo."""
        dono = {c: i for i, r in enumerate(regioes) for c in r}
        vizinhas = [set() for _ in regioes]
        for (x, y), i in dono.items():
            for dx, dy in VIZINHOS:
                j = dono.get((x + dx, y + dy))
                if j is not None and j != i:
                    vizinhas[i].add(j)
        nomes = list(TIPOS)
        for _ in range(800):
            tipos = [random.choice(nomes) for _ in regioes]
            if set(tipos) != set(nomes):
                continue
            if all(TIPOS[t][2] is None or any(tipos[j] == TIPOS[t][2] for j in vizinhas[i])
                   for i, t in enumerate(tipos)):
                return tipos, True
        return [nomes[i % len(nomes)] for i in range(len(regioes))], False     # (quase nunca acontece)

    def _montar_bandeja(self):
        """Onde cada peça fica esperando: uma casinha fixa para cada uma, em miniatura."""
        area = pygame.Rect(self.tabuleiro.right + 14, self.rect.top + 8,
                           self.rect.right - self.tabuleiro.right - 22, self.rect.height - 16)
        self.bandeja = area
        colunas, linhas = 3, 4
        largura, altura = area.width / colunas, area.height / linhas
        maior_l = max(p["largura"] for p in self.pecas)
        maior_a = max(p["altura"] for p in self.pecas)
        self.mini = max(8, int(min((largura - 8) / maior_l, (altura - 8) / maior_a, 16)))
        for i, peca in enumerate(self.pecas):
            casa = pygame.Rect(area.left + (i % colunas) * largura, area.top + (i // colunas) * altura,
                               largura, altura)
            peca["casa"] = casa

    # ------------------------------------------------------------- consultas
    def encaixadas(self):
        return len(self.posicoes)

    def _celulas_da_peca(self, peca, coluna, linha):
        return [(coluna + dx, linha + dy) for dx, dy in peca["forma"]]

    def _cabe(self, peca, coluna, linha):
        for c in self._celulas_da_peca(peca, coluna, linha):
            if not (0 <= c[0] < self.colunas and 0 <= c[1] < self.linhas) or c in self.ocupacao:
                return False
        return True

    def _regra_cumprida(self, peca):
        """True se a peça não exige vizinho, ou se ele está encostado nela."""
        procurado = TIPOS[peca["tipo"]][2]
        if procurado is None or not self.regras_ativas:
            return True
        coluna, linha = self.posicoes[peca["id"]]
        minhas = set(self._celulas_da_peca(peca, coluna, linha))
        for x, y in minhas:
            for dx, dy in VIZINHOS:
                outra = self.ocupacao.get((x + dx, y + dy))
                if outra is not None and outra != peca["id"] and self.pecas_por_id[outra]["tipo"] == procurado:
                    return True
        return False

    def regras_cumpridas(self):
        return all(self._regra_cumprida(p) for p in self.pecas if p["id"] in self.posicoes)

    # ------------------------------------------------------------- entrada
    def handle_key(self, key):
        pass

    def _peca_em(self, pos):
        for peca in self.pecas:                                       # no tabuleiro
            if peca["id"] in self.posicoes:
                coluna, linha = self.posicoes[peca["id"]]
                for c in self._celulas_da_peca(peca, coluna, linha):
                    if self._area_da_celula(c).collidepoint(pos):
                        return peca, "tabuleiro"
        for peca in self.pecas:                                       # na bandeja
            if peca["id"] not in self.posicoes and peca["casa"].collidepoint(pos):
                return peca, "bandeja"
        return None, None

    def handle_click(self, pos):
        if self.done:
            return
        peca, de_onde = self._peca_em(pos)
        if peca is None:
            return
        self.ponteiro = pos
        if de_onde == "bandeja":
            self.pega = (peca["largura"] * LADO // 2, peca["altura"] * LADO // 2)      # segura pelo meio
        else:
            coluna, linha = self.posicoes[peca["id"]]
            self.pega = (pos[0] - (self.tabuleiro.left + coluna * LADO), pos[1] - (self.tabuleiro.top + linha * LADO))
            self._tirar_do_tabuleiro(peca)
        self.segurando = peca

    def handle_drag(self, pos, pressed):
        self.ponteiro = pos
        if self.segurando is not None and not pressed:                # soltou o botão fora do jogo
            self.handle_release(pos)

    def handle_release(self, pos):
        if self.segurando is None or self.done:
            return
        peca, self.segurando = self.segurando, None
        coluna, linha = self._casa_sob(pos)
        if self._cabe(peca, coluna, linha):
            self._por_no_tabuleiro(peca, coluna, linha)
            if self.encaixadas() == len(self.pecas):
                self._terminar()

    def _casa_sob(self, pos):
        """O quadrado do tabuleiro onde cairia o canto de cima à esquerda da peça."""
        x = pos[0] - self.pega[0] - self.tabuleiro.left
        y = pos[1] - self.pega[1] - self.tabuleiro.top
        return int(round(x / LADO)), int(round(y / LADO))

    def _por_no_tabuleiro(self, peca, coluna, linha):
        self.posicoes[peca["id"]] = (coluna, linha)
        for c in self._celulas_da_peca(peca, coluna, linha):
            self.ocupacao[c] = peca["id"]

    def _tirar_do_tabuleiro(self, peca):
        coluna, linha = self.posicoes.pop(peca["id"])
        for c in self._celulas_da_peca(peca, coluna, linha):
            self.ocupacao.pop(c, None)

    # ------------------------------------------------------------- atualização
    def update(self, dt):
        if self.done:
            return
        self.time_left -= dt
        if self.time_left <= 0:
            self._terminar()

    def _terminar(self):
        self.done = True
        self.segurando = None
        encaixadas = self.encaixadas()
        if encaixadas >= PECAS_PARA_SUCESSO:
            self.result = "sucesso"
        elif encaixadas >= PECAS_PARA_PARCIAL:
            self.result = "parcial"
        else:
            self.result = "falha"
        if self.regras_ativas and self.result == "sucesso" and not self.regras_cumpridas():
            self.result = "parcial"

    # ------------------------------------------------------------- desenho
    def _area_da_celula(self, celula):
        return pygame.Rect(self.tabuleiro.left + celula[0] * LADO, self.tabuleiro.top + celula[1] * LADO, LADO, LADO)

    def _desenhar_forma(self, surface, peca, canto, lado, com_icone=True, feliz=None):
        """Desenha a peça com o canto de cima à esquerda em `canto`, cada quadrado com `lado` pixels."""
        cor, icone, _ = TIPOS[peca["tipo"]]
        celulas = set(peca["forma"])
        for dx, dy in celulas:
            area = pygame.Rect(canto[0] + dx * lado, canto[1] + dy * lado, lado, lado)
            pygame.draw.rect(surface, cor, area)
        escura = tuple(int(c * 0.62) for c in cor)
        for dx, dy in celulas:
            x, y = canto[0] + dx * lado, canto[1] + dy * lado
            espessura = 3 if lado >= 24 else 2
            if (dx, dy - 1) not in celulas:
                pygame.draw.line(surface, escura, (x, y), (x + lado, y), espessura)
            if (dx, dy + 1) not in celulas:
                pygame.draw.line(surface, escura, (x, y + lado), (x + lado, y + lado), espessura)
            if (dx - 1, dy) not in celulas:
                pygame.draw.line(surface, escura, (x, y), (x, y + lado), espessura)
            if (dx + 1, dy) not in celulas:
                pygame.draw.line(surface, escura, (x + lado, y), (x + lado, y + lado), espessura)
        if com_icone:
            dx, dy = sorted(celulas)[len(celulas) // 2]
            desenhar_icone(icone, surface, (canto[0] + dx * lado + lado // 2, canto[1] + dy * lado + lado // 2),
                           lado * 0.8)
            if feliz:                                                  # a regra de vizinhança está cumprida
                cx, cy = canto[0] + dx * lado + lado - 8, canto[1] + dy * lado + 8
                pygame.draw.circle(surface, (35, 125, 55), (cx, cy), 7)
                pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 7, 1)
                pygame.draw.lines(surface, (255, 255, 255), False, [(cx - 3, cy), (cx - 1, cy + 3), (cx + 3, cy - 3)], 2)

    def draw(self, surface):
        pygame.draw.rect(surface, (235, 226, 196), self.rect, border_radius=8)
        pygame.draw.rect(surface, (150, 150, 150), self.rect, 2, border_radius=8)

        # o tabuleiro vazio
        pygame.draw.rect(surface, COR_DO_TABULEIRO, self.tabuleiro)
        for x in range(self.colunas + 1):
            pygame.draw.line(surface, COR_DA_LINHA, (self.tabuleiro.left + x * LADO, self.tabuleiro.top),
                             (self.tabuleiro.left + x * LADO, self.tabuleiro.bottom), 1)
        for y in range(self.linhas + 1):
            pygame.draw.line(surface, COR_DA_LINHA, (self.tabuleiro.left, self.tabuleiro.top + y * LADO),
                             (self.tabuleiro.right, self.tabuleiro.top + y * LADO), 1)
        pygame.draw.rect(surface, (120, 100, 70), self.tabuleiro, 3)

        # as peças já encaixadas
        for peca in self.pecas:
            if peca["id"] in self.posicoes:
                coluna, linha = self.posicoes[peca["id"]]
                canto = (self.tabuleiro.left + coluna * LADO, self.tabuleiro.top + linha * LADO)
                self._desenhar_forma(surface, peca, canto, LADO, feliz=(
                    self.regras_ativas and TIPOS[peca["tipo"]][2] is not None and self._regra_cumprida(peca)))

        # a bandeja
        pygame.draw.rect(surface, (222, 210, 175), self.bandeja, border_radius=8)
        for peca in self.pecas:
            if peca["id"] not in self.posicoes and peca is not self.segurando:
                casa = peca["casa"]
                canto = (casa.centerx - peca["largura"] * self.mini // 2, casa.centery - peca["altura"] * self.mini // 2)
                self._desenhar_forma(surface, peca, canto, self.mini, com_icone=self.mini >= 12)
                pygame.draw.rect(surface, CINZA_CLARO, casa.inflate(-6, -6), 1, border_radius=6)

        # a peça na mão (meio transparente, para ver o que há embaixo) e, por cima, o contorno
        # do lugar onde ela cairia: verde se cabe, vermelho se não
        if self.segurando is not None:
            peca = self.segurando
            coluna, linha = self._casa_sob(self.ponteiro)
            folha = pygame.Surface((peca["largura"] * LADO + 2, peca["altura"] * LADO + 2), pygame.SRCALPHA)
            self._desenhar_forma(folha, peca, (1, 1), LADO)
            folha.set_alpha(185)
            surface.blit(folha, (self.ponteiro[0] - self.pega[0] - 1, self.ponteiro[1] - self.pega[1] - 1))
            cor = VERDE if self._cabe(peca, coluna, linha) else (205, 85, 80)
            for c in self._celulas_da_peca(peca, coluna, linha):
                pygame.draw.rect(surface, cor, self._area_da_celula(c), 3)

        regra = "flor junto da água, árvore junto do abrigo   " if self.regras_ativas else ""
        linha_de_status(surface, self.rect,
                        f"Encaixadas: {self.encaixadas()}/{len(self.pecas)}   {regra}"
                        f"Tempo: {max(0, self.time_left):.0f}s",
                        self.time_left / self.tempo_total)
