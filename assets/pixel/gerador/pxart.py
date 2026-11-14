# -*- coding: utf-8 -*-
"""Caixa de ferramentas de pixel art (gera os PNGs do jogo).

Luz sempre vinda de CIMA, à ESQUERDA: o que está virado para lá é mais claro, o que está virado para
baixo e para a direita é mais escuro. Todo desenho tem contorno escuro e um brilhinho, como a abelha e a folha.
"""
import math
import random

import numpy as np
from PIL import Image


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mais_escuro(cor, f):
    return tuple(max(0, min(255, int(c * f))) for c in cor)


def misturar(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


class Tela:
    """Uma imagem pequena (RGBA) e as ferramentas para desenhar nela pixel a pixel."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.img = np.zeros((h, w, 4), dtype=np.uint8)

    # ---------------------------------------------------------------- máscaras (onde desenhar)
    def vazia(self):
        return np.zeros((self.h, self.w), dtype=bool)

    def m_ret(self, x0, y0, x1, y1):
        """Retângulo com os cantos incluídos (x0..x1, y0..y1)."""
        m = self.vazia()
        m[max(0, y0):min(self.h, y1 + 1), max(0, x0):min(self.w, x1 + 1)] = True
        return m

    def m_ret_arredondado(self, x0, y0, x1, y1, r=2):
        """Retângulo com os cantos cortados em degrau (raio r em pixels)."""
        m = self.m_ret(x0, y0, x1, y1)
        for i in range(r):
            for j in range(r - i):
                for (cx, cy) in ((x0 + i, y0 + j), (x1 - i, y0 + j), (x0 + i, y1 - j), (x1 - i, y1 - j)):
                    if 0 <= cx < self.w and 0 <= cy < self.h:
                        m[cy, cx] = False
        return m

    def m_elipse(self, cx, cy, rx, ry):
        ys, xs = np.mgrid[0:self.h, 0:self.w]
        return ((xs + 0.5 - cx) / rx) ** 2 + ((ys + 0.5 - cy) / ry) ** 2 <= 1.0

    def m_elipse_rot(self, cx, cy, rx, ry, ang):
        """Elipse girada em `ang` radianos (rx é o raio ao longo do eixo girado)."""
        ys, xs = np.mgrid[0:self.h, 0:self.w]
        dx, dy = xs + 0.5 - cx, ys + 0.5 - cy
        u = dx * math.cos(ang) + dy * math.sin(ang)
        v = -dx * math.sin(ang) + dy * math.cos(ang)
        return (u / rx) ** 2 + (v / ry) ** 2 <= 1.0

    def m_poligono(self, pontos):
        """Polígono preenchido (os pontos em coordenadas de pixel; o centro do pixel é que conta)."""
        m = self.vazia()
        n = len(pontos)
        for y in range(self.h):
            py = y + 0.5
            cruzamentos = []
            for i in range(n):
                (x1, y1), (x2, y2) = pontos[i], pontos[(i + 1) % n]
                if (y1 <= py < y2) or (y2 <= py < y1):
                    cruzamentos.append(x1 + (py - y1) * (x2 - x1) / (y2 - y1))
            cruzamentos.sort()
            for a, b in zip(cruzamentos[0::2], cruzamentos[1::2]):
                for x in range(self.w):
                    if a <= x + 0.5 < b:
                        m[y, x] = True
        return m

    def m_linha(self, x0, y0, x1, y1, espessura=1):
        m = self.vazia()
        passos = max(abs(x1 - x0), abs(y1 - y0), 1) * 2
        for i in range(passos + 1):
            x = x0 + (x1 - x0) * i / passos
            y = y0 + (y1 - y0) * i / passos
            xi, yi = int(math.floor(x)), int(math.floor(y))
            for dy in range(espessura):
                for dx in range(espessura):
                    if 0 <= xi + dx < self.w and 0 <= yi + dy < self.h:
                        m[yi + dy, xi + dx] = True
        return m

    # ---------------------------------------------------------------- pintar
    def pintar(self, mascara, cor, alfa=255):
        self.img[mascara] = (*cor, alfa)

    def px(self, x, y, cor, alfa=255):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.img[y, x] = (*cor, alfa)

    def opaca(self):
        return self.img[:, :, 3] > 0

    def bisel(self, mascara, base, claro, escuro, largura=1, brilho=None, claro2=None, escuro2=None):
        """Preenche `mascara` com a cor base e dá volume: a borda de cima/esquerda fica clara, a de baixo/direita
        escura. Com `largura` 2 ou 3 há degraus (claro2/escuro2 são o segundo tom, mais perto do miolo)."""
        if base is not None:
            self.pintar(mascara, base)
        h, w = mascara.shape
        INF = 99

        def distancia(dy, dx):
            """Quantos pixels, andando (dy, dx), até sair da forma."""
            d = np.full(mascara.shape, INF, dtype=int)
            for k in range(1, largura + 1):
                fora = np.ones_like(mascara)
                ys0, ys1 = (k, h) if dy > 0 else (0, h - k) if dy < 0 else (0, h)
                xs0, xs1 = (k, w) if dx > 0 else (0, w - k) if dx < 0 else (0, w)
                yo0, yo1 = (0, h - k) if dy > 0 else (k, h) if dy < 0 else (0, h)
                xo0, xo1 = (0, w - k) if dx > 0 else (k, w) if dx < 0 else (0, w)
                fora[ys0:ys1, xs0:xs1] = ~mascara[yo0:yo1, xo0:xo1]
                d[mascara & fora & (d == INF)] = k
            return d

        dl = np.minimum(distancia(1, 0), distancia(0, 1))          # perto da borda de cima ou da esquerda
        dd = np.minimum(distancia(-1, 0), distancia(0, -1))        # perto da borda de baixo ou da direita
        tons_claros = [claro, claro2 or claro, claro2 or claro][:max(1, largura)]
        tons_escuros = [escuro, escuro2 or escuro, escuro2 or escuro][:max(1, largura)]
        for k in range(largura, 0, -1):
            self.pintar(mascara & (dd == k) & (dd < dl), tons_escuros[k - 1])
            self.pintar(mascara & (dl == k) & (dl <= dd), tons_claros[k - 1])
        if brilho is not None:
            for (x, y) in brilho[0]:
                self.px(x, y, brilho[1])

    def contorno(self, cor, diagonais=False, so_fora=True):
        """Contorno de 1 pixel em volta de tudo o que já foi desenhado."""
        opaca = self.opaca()
        borda = np.zeros_like(opaca)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)) + (((1, 1), (-1, -1), (1, -1), (-1, 1)) if diagonais else ()):
            deslocada = np.zeros_like(opaca)
            ys = slice(max(0, dy), self.h + min(0, dy))
            xs = slice(max(0, dx), self.w + min(0, dx))
            yd = slice(max(0, -dy), self.h + min(0, -dy))
            xd = slice(max(0, -dx), self.w + min(0, -dx))
            deslocada[ys, xs] = opaca[yd, xd]
            borda |= deslocada
        borda &= ~opaca
        self.pintar(borda, cor)

    def sombra_no_chao(self, cx, cy, rx, ry, cor=(0, 0, 0), alfa=70):
        """Uma elipse de sombra escura e translúcida, só onde ainda não há desenho."""
        m = self.m_elipse(cx, cy, rx, ry) & ~self.opaca()
        self.pintar(m, cor, alfa)

    # ---------------------------------------------------------------- salvar / ver
    def salvar(self, caminho):
        Image.fromarray(self.img, "RGBA").save(caminho)

    def imagem(self):
        return Image.fromarray(self.img, "RGBA")


def folha_de_contato(itens, ampliacao=8, colunas=6, fundo=(196, 214, 168), margem=6, legenda=True):
    """Várias Telas lado a lado, ampliadas sem suavizar (para conferir a arte)."""
    from PIL import ImageDraw
    largura_celula = max(t.w for _, t in itens) * ampliacao + margem * 2
    altura_celula = max(t.h for _, t in itens) * ampliacao + margem * 2 + (14 if legenda else 0)
    linhas = (len(itens) + colunas - 1) // colunas
    folha = Image.new("RGBA", (largura_celula * colunas, altura_celula * linhas), (*fundo, 255))
    desenho = ImageDraw.Draw(folha)
    for k, (nome, tela) in enumerate(itens):
        x, y = (k % colunas) * largura_celula, (k // colunas) * altura_celula
        grande = tela.imagem().resize((tela.w * ampliacao, tela.h * ampliacao), Image.NEAREST)
        folha.alpha_composite(grande, (x + margem, y + margem))
        if legenda:
            desenho.text((x + margem, y + altura_celula - 14), f"{nome} {tela.w}x{tela.h}", fill=(30, 30, 30, 255))
    return folha


def ruido_toroidal(w, h, semente, escala=1):
    """Ruído que emenda nas bordas (para os fundos repetirem sem costura)."""
    rng = random.Random(semente)
    return [[rng.random() for _ in range(w)] for _ in range(h)]
