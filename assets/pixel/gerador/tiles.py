# -*- coding: utf-8 -*-
"""Os fundos (que repetem sem costura) e os quadradinhos do Campo Minado."""
import math
import random

import numpy as np

from pxart import Tela, rgb, mais_escuro, misturar


def ruido(w, h, cx, cy, semente):
    """Ruído suave que emenda nas bordas: grade de cx x cy valores, interpolada."""
    rng = np.random.RandomState(semente)
    grade = rng.rand(cy, cx)
    ys, xs = np.mgrid[0:h, 0:w]
    fx, fy = xs * cx / w, ys * cy / h
    x0, y0 = np.floor(fx).astype(int), np.floor(fy).astype(int)
    tx, ty = fx - x0, fy - y0
    tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
    a, b = grade[y0 % cy, x0 % cx], grade[y0 % cy, (x0 + 1) % cx]
    c, d = grade[(y0 + 1) % cy, x0 % cx], grade[(y0 + 1) % cy, (x0 + 1) % cx]
    return (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty


def _por_tons(v, tons, limites):
    saida = np.zeros(v.shape + (3,), dtype=np.uint8)
    saida[:] = tons[-1]
    for tom, lim in reversed(list(zip(tons, limites))):
        saida[v < lim] = tom
    return saida


def _tela_de(rgb_arr):
    t = Tela(rgb_arr.shape[1], rgb_arr.shape[0])
    t.img[:, :, :3] = rgb_arr
    t.img[:, :, 3] = 255
    return t


# ---------------------------------------------------------------------- grama
GRAMA_TONS = [rgb("3f9a46"), rgb("55b04c"), rgb("5fb845"), rgb("78cc58"), rgb("9ae070")]


def grama(lado=64, semente=11):
    v = 0.5 * ruido(lado, lado, 4, 4, semente) + 0.5 * ruido(lado, lado, 10, 10, semente + 1)
    v = (v - v.min()) / (v.max() - v.min())
    rgb_arr = _por_tons(v, GRAMA_TONS, [0.16, 0.38, 0.62, 0.86])
    t = _tela_de(rgb_arr)
    rng = random.Random(semente)
    # as folhinhas de grama: um traço claro de 2 pixels com uma sombra escura do lado
    for _ in range(int(lado * lado / 26)):
        x, y = rng.randrange(lado), rng.randrange(lado)
        t.px(x % lado, y % lado, rgb("a6e478"))
        t.px(x % lado, (y - 1) % lado, rgb("bdf08e"))
        t.px((x + 1) % lado, y % lado, rgb("3c8f42"))
    for _ in range(int(lado * lado / 60)):
        x, y = rng.randrange(lado), rng.randrange(lado)
        t.px(x, y, rgb("2f7f3c"))
        t.px((x + 1) % lado, (y + 1) % lado, rgb("2f7f3c"))
    # um trevo ou florzinha aqui e ali
    for _ in range(max(1, lado // 14)):
        x, y = rng.randrange(2, lado - 2), rng.randrange(2, lado - 2)
        cor = rng.choice([rgb("fff6c8"), rgb("ffe066"), rgb("ffd0e0")])
        t.px(x, y, cor)
        t.px(x + 1, y, cor)
        t.px(x, y + 1, rgb("e8c84a") if cor == rgb("ffe066") else rgb("f0e0b0"))
    return t


# ---------------------------------------------------------------------- terra
TERRA_TONS = [rgb("4a2e20"), rgb("5e3e2a"), rgb("6e4a32"), rgb("805a3e"), rgb("94704c")]


def terra(lado=64, semente=21):
    v = 0.5 * ruido(lado, lado, 4, 4, semente) + 0.5 * ruido(lado, lado, 10, 10, semente + 1)
    v = (v - v.min()) / (v.max() - v.min())
    rgb_arr = _por_tons(v, TERRA_TONS, [0.2, 0.42, 0.66, 0.88])
    t = _tela_de(rgb_arr)
    rng = random.Random(semente)
    for _ in range(int(lado * lado / 14)):                      # os pontinhos
        x, y = rng.randrange(lado), rng.randrange(lado)
        t.px(x, y, rng.choice([rgb("4a2e20"), rgb("4a2e20"), rgb("a07c58"), rgb("5a3a28")]))
    for _ in range(max(2, lado // 9)):                          # as pedrinhas: luz em cima, sombra embaixo
        x, y = rng.randrange(lado), rng.randrange(lado)
        for dx, dy, cor in ((0, 0, "9c9488"), (1, 0, "b4aca0"), (0, 1, "7a7268"), (1, 1, "625a52")):
            t.px((x + dx) % lado, (y + dy) % lado, rgb(cor))
        t.px((x + 2) % lado, (y + 1) % lado, rgb("3e281c"))
    for _ in range(max(1, lado // 12)):                         # uma raizinha
        x, y = rng.randrange(lado), rng.randrange(lado)
        for k in range(rng.randint(3, 5)):
            t.px((x + k) % lado, (y + (k % 2)) % lado, rgb("7a5a38"))
    return t


# ---------------------------------------------------------------------- favo de mel
def favo(w=24, h=20):
    """Hexágonos de cera e mel: cada célula é clara em cima/à esquerda e escura embaixo/à direita."""
    L, linha_h = 12.0, 10.0
    centros = []
    for linha in range(-1, 3):
        for coluna in range(-1, 3):
            deslocamento = 0.0 if linha % 2 == 0 else L / 2
            centros.append((coluna * L + L / 2 + deslocamento, linha * linha_h + linha_h / 2))

    def hexa(dx, dy):                                    # a "distância" de um hexágono de ponta para cima
        dy = dy * (10.39 / linha_h)
        ax, ay = abs(dx), abs(dy)
        return max(ax, ax * 0.5 + ay * 0.866)

    t = Tela(w, h)
    for y in range(h):
        for x in range(w):
            px_, py_ = x + 0.5, y + 0.5
            ds = sorted((hexa(px_ - cx, py_ - cy), cx, cy) for cx, cy in centros)
            d1, cx, cy = ds[0]
            d2 = ds[1][0]
            if d2 - d1 < 0.9:                            # a parede de cera entre as células
                t.px(x, y, rgb("8a5014") if (x + y) % 2 == 0 else rgb("7a4410"))
                continue
            luz = -((px_ - cx) + (py_ - cy)) / 9.0
            brilho = max(0.0, 1 - d1 / 5.6)
            valor = 0.46 + 0.34 * luz + 0.3 * brilho
            tons = [rgb("c07a1c"), rgb("d8941e"), rgb("eaa828"), rgb("f6c040"), rgb("ffdc70")]
            t.px(x, y, tons[min(4, max(0, int(valor * 5)))])
    return t


# ---------------------------------------------------------------------- madeira
def madeira(lado=32, semente=31):
    """Tábuas na vertical, cada uma de um tom, com veios, fendas escuras e pregos."""
    t = Tela(lado, lado)
    rng = random.Random(semente)
    base = [rgb("b07a48"), rgb("a8703e"), rgb("b88050"), rgb("9e6a3c")]
    largura_tabua = lado // 4
    for i in range(4):
        x0 = i * largura_tabua
        cor = base[i % len(base)]
        claro, escuro = misturar(cor, rgb("ffe8c0"), 0.28), mais_escuro(cor, 0.78)
        for y in range(lado):
            for x in range(x0, x0 + largura_tabua):
                c = cor
                if x == x0 + 1:
                    c = claro                                       # a luz na borda da esquerda
                elif x == x0 + largura_tabua - 2:
                    c = escuro
                t.px(x, y, c)
        for x in range(x0, x0 + largura_tabua):                    # a fenda entre as tábuas
            pass
        for y in range(lado):
            t.px(x0, y, rgb("5a3a1c"))
        for _ in range(3):                                          # os veios
            vx, vy = x0 + rng.randrange(2, largura_tabua - 2), rng.randrange(lado)
            for k in range(rng.randint(4, 9)):
                t.px(vx, (vy + k) % lado, mais_escuro(cor, 0.82))
        t.px(x0 + 3, 3, rgb("4a3018"))
        t.px(x0 + 3, lado - 4, rgb("4a3018"))
        t.px(x0 + 2, 2, rgb("d8b890"))
        t.px(x0 + 2, lado - 5, rgb("d8b890"))
    return t


# ---------------------------------------------------------------------- areia
AREIA_TONS = [rgb("d4b886"), rgb("e0c898"), rgb("ead4a6"), rgb("f2e0b6")]


def areia(lado=16, semente=41):
    v = 0.6 * ruido(lado, lado, 2, 2, semente) + 0.4 * ruido(lado, lado, 4, 4, semente + 1)
    v = (v - v.min()) / (v.max() - v.min())
    t = _tela_de(_por_tons(v, AREIA_TONS, [0.25, 0.55, 0.82]))
    rng = random.Random(semente)
    for _ in range(lado * lado // 12):
        t.px(rng.randrange(lado), rng.randrange(lado), rng.choice([rgb("c4a674"), rgb("f8ecc8")]))
    return t


# ---------------------------------------------------------------------- água
AGUA_TONS = [rgb("2e78c8"), rgb("3a8ad8"), rgb("4c9ee6"), rgb("72b8f2")]


def agua(lado=32, semente=51):
    v = 0.5 * ruido(lado, lado, 3, 3, semente) + 0.5 * ruido(lado, lado, 6, 6, semente + 1)
    v = (v - v.min()) / (v.max() - v.min())
    t = _tela_de(_por_tons(v, AGUA_TONS, [0.28, 0.55, 0.8]))
    rng = random.Random(semente)
    for _ in range(max(3, lado // 5)):                              # as marolinhas: um traço claro e um escuro
        x, y = rng.randrange(lado), rng.randrange(lado)
        for k in range(3):
            t.px((x + k) % lado, y, rgb("d6efff"))
        for k in range(3):
            t.px((x + k + 1) % lado, (y + 1) % lado, rgb("2468b4"))
    return t


# ---------------------------------------------------------------------- pergaminho / osso (miolo das cartas)
def pergaminho(lado=16, semente=71, tons=None):
    tons = tons or [rgb("efdcb0"), rgb("f4e4bc"), rgb("f8ecca"), rgb("fcf4dc")]
    v = 0.5 * ruido(lado, lado, 2, 2, semente) + 0.5 * ruido(lado, lado, 4, 4, semente + 1)
    v = (v - v.min()) / (v.max() - v.min())
    t = _tela_de(_por_tons(v, tons, [0.25, 0.55, 0.82]))
    rng = random.Random(semente)
    for _ in range(lado * lado // 14):                   # as fibrinhas do papel
        x, y = rng.randrange(lado), rng.randrange(lado)
        t.px(x, y, mais_escuro(tons[0], 0.93))
        t.px((x + 1) % lado, y, mais_escuro(tons[0], 0.96))
    return t


def osso(lado=16, semente=73):
    return pergaminho(lado, semente, [rgb("f2ead4"), rgb("f8f2e0"), rgb("fcf8ec"), rgb("ffffff")])


# ---------------------------------------------------------------------- pólen (o que a abelha deixa no campo)
POLEN_TONS = [rgb("dca024"), rgb("ecba34"), rgb("f6d04c"), rgb("ffe27a")]


def polen(lado=64, semente=81):
    v = 0.55 * ruido(lado, lado, 5, 5, semente) + 0.45 * ruido(lado, lado, 12, 12, semente + 1)
    v = (v - v.min()) / (v.max() - v.min())
    t = _tela_de(_por_tons(v, POLEN_TONS, [0.2, 0.5, 0.82]))
    rng = random.Random(semente)
    for _ in range(lado * lado // 30):                     # os grãozinhos de pólen: mais claros e mais escuros
        x, y = rng.randrange(lado), rng.randrange(lado)
        t.px(x, y, rng.choice([rgb("ffeea0"), rgb("c88a1c"), rgb("ffeea0")]))
    for _ in range(lado // 4):                             # alguns maiores, com luz em cima e sombra embaixo
        x, y = rng.randrange(lado), rng.randrange(lado)
        t.px(x, y, rgb("fff6c0"))
        t.px((x + 1) % lado, (y + 1) % lado, rgb("b87a14"))
    return t


# ---------------------------------------------------------------------- moita (sebe)
MOITA_TONS = [rgb("1f5a34"), rgb("2a7040"), rgb("358a4a"), rgb("46a458"), rgb("66c06c")]


def moita(lado=16, semente=61):
    v = 0.5 * ruido(lado, lado, 4, 4, semente) + 0.5 * ruido(lado, lado, 8, 8, semente + 1)
    v = (v - v.min()) / (v.max() - v.min())
    t = _tela_de(_por_tons(v, MOITA_TONS, [0.2, 0.42, 0.64, 0.86]))
    rng = random.Random(semente)
    for _ in range(lado * lado // 12):                               # folhinhas
        x, y = rng.randrange(lado), rng.randrange(lado)
        t.px(x, y, rgb("86d884"))
        t.px((x + 1) % lado, (y + 1) % lado, rgb("1c4e2c"))
    return t


# ---------------------------------------------------------------------- blocos do Campo Minado (10x10)
def bloco_terra_seca():
    """Terra seca e rachada, levantada: luz em cima/esquerda, sombra embaixo/direita."""
    t = Tela(10, 10)
    m = t.m_ret(0, 0, 9, 9)
    t.bisel(m, rgb("c49a64"), rgb("e4c690"), rgb("8a6236"), largura=1)
    rng = random.Random(7)
    for _ in range(14):
        t.px(rng.randrange(2, 8), rng.randrange(2, 8), rng.choice([rgb("b48c58"), rgb("d0a870"), rgb("a67e4c")]))
    for x, y in ((3, 3), (4, 4), (4, 5), (5, 6), (6, 6), (2, 6), (3, 7)):       # a rachadura
        t.px(x, y, rgb("7a542c"))
    t.px(6, 2, rgb("f0d8a8"))
    t.px(2, 2, rgb("f0d8a8"))
    return t


def bloco_areia():
    """Quadrado já aberto: afundado (sombra em cima/esquerda, luz embaixo/direita)."""
    t = Tela(10, 10)
    areia_t = areia(10, 5)
    t.img[:] = areia_t.img
    m = t.m_ret(0, 0, 9, 9)
    # afundado: a borda de cima/esquerda escura, a de baixo/direita clara
    for i in range(10):
        t.px(i, 0, rgb("b89a68"))
        t.px(0, i, rgb("b89a68"))
        t.px(i, 9, rgb("faf0d0"))
        t.px(9, i, rgb("faf0d0"))
    t.px(0, 9, rgb("e8d8b0"))
    t.px(9, 0, rgb("e8d8b0"))
    for i in range(1, 9):
        t.px(i, 1, rgb("d0b27c"))
        t.px(1, i, rgb("d0b27c"))
    return t


def bloco_grama_umida():
    """Quadrado aberto sem nenhum perigo por perto: grama molhada (e uma gota é desenhada por cima)."""
    t = Tela(10, 10)
    g = grama(10, 9)
    t.img[:] = g.img
    for i in range(10):
        t.px(i, 0, rgb("2f7f3c"))
        t.px(0, i, rgb("2f7f3c"))
        t.px(i, 9, rgb("a8e482"))
        t.px(9, i, rgb("a8e482"))
    return t


def bloco_explosao():
    """Terra queimada onde a bomba estourou."""
    t = Tela(10, 10)
    m = t.m_ret(0, 0, 9, 9)
    t.bisel(m, rgb("5a3a2a"), rgb("8a6242"), rgb("3a241a"), largura=1)
    rng = random.Random(3)
    for _ in range(16):
        t.px(rng.randrange(1, 9), rng.randrange(1, 9), rng.choice([rgb("3a241a"), rgb("6e4a34"), rgb("2a1810")]))
    return t


TILES = {"grama": grama, "terra": terra, "favo": favo, "madeira": madeira, "areia": areia, "agua": agua, "moita": moita,
         "pergaminho": pergaminho, "osso": osso, "polen": polen}
BLOCOS = {"bloco_terra_seca": bloco_terra_seca, "bloco_areia": bloco_areia, "bloco_grama_umida": bloco_grama_umida,
          "bloco_explosao": bloco_explosao}
