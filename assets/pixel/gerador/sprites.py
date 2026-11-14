# -*- coding: utf-8 -*-
"""Os ícones novos, em 32x32 (o mesmo tamanho da sua abelha): estrela, gota, pote de mel, colmeia, bandeira,
sol, flor, bomba, e o toco da poda."""
import math

import numpy as np

from pxart import Tela, rgb

CONTORNO_QUENTE = rgb("3a2214")
CONTORNO_AZUL = rgb("12204c")
CONTORNO_ROSA = rgb("4a1840")
CONTORNO_ESCURO = rgb("120e18")
TAM = 32


def estrela():
    t = Tela(TAM, TAM)
    cx, cy, R, r = 16.0, 17.2, 14.2, 6.2
    vertices = []
    for i in range(10):
        raio = R if i % 2 == 0 else r
        ang = -math.pi / 2 + i * math.pi / 5
        vertices.append((cx + math.cos(ang) * raio, cy + math.sin(ang) * raio))
    tudo = t.m_poligono(vertices)
    t.pintar(tudo, rgb("f9c42c"))
    # as facetas: de cada braço, a metade que olha para a luz é mais clara
    for i in range(5):
        ponta = vertices[2 * i]
        vale_esq, vale_dir = vertices[(2 * i - 1) % 10], vertices[(2 * i + 1) % 10]
        a = t.m_poligono([ponta, vale_esq, (cx, cy)])
        b = t.m_poligono([ponta, vale_dir, (cx, cy)])
        ca = ((ponta[0] + vale_esq[0] + cx) / 3 + (ponta[1] + vale_esq[1] + cy) / 3)
        cb = ((ponta[0] + vale_dir[0] + cx) / 3 + (ponta[1] + vale_dir[1] + cy) / 3)
        claro, escuro = (a, b) if ca < cb else (b, a)
        t.pintar(claro & tudo, rgb("ffe46c"))
        t.pintar(escuro & tudo, rgb("e89a1a"))
    t.bisel(tudo, None, rgb("fff6b0"), rgb("b86a0e"), largura=1)
    t.pintar(t.m_elipse(cx, cy, 2.6, 2.6) & tudo, rgb("fff0a0"))
    for x, y in ((14, 6), (15, 6), (10, 13), (11, 13), (14, 15), (15, 14)):
        t.px(x, y, rgb("ffffff"))
    t.contorno(CONTORNO_QUENTE)
    return t


def gota():
    t = Tela(TAM, TAM)
    corpo = t.m_elipse(16, 20.4, 10.6, 10.6)
    ponta = t.m_poligono([(16, 1.6), (6.2, 17.6), (25.8, 17.6)])
    m = corpo | ponta
    t.bisel(m, rgb("3a8ae6"), rgb("8ad0ff"), rgb("164aa8"), largura=3, claro2=rgb("5ab0f6"), escuro2=rgb("2468cc"))
    # faixa de brilho do lado esquerdo e o brilhinho de cima
    for k in range(7):
        t.px(8 + (1 if k > 3 else 0), 17 + k, rgb("d8f2ff"))
        t.px(9 + (1 if k > 3 else 0), 17 + k, rgb("b4e4ff"))
    t.pintar(t.m_ret(11, 24, 12, 26), rgb("9ad8ff"))
    for x, y in ((15, 7), (15, 8), (14, 9), (14, 10)):
        t.px(x, y, rgb("d8f2ff"))
    t.pintar(t.m_elipse(11.4, 15.4, 1.6, 1.6), rgb("ffffff"))
    t.px(20, 24, rgb("1c58b4"))
    t.contorno(CONTORNO_AZUL)
    return t


def pote_de_mel():
    t = Tela(TAM, TAM)
    corpo = t.m_ret_arredondado(6, 13, 25, 29, 3)
    ombro = t.m_ret(8, 10, 23, 13)
    vidro = corpo | ombro
    t.bisel(vidro, rgb("f4aa24"), rgb("ffd976"), rgb("a8620c"), largura=2, claro2=rgb("f8c04a"), escuro2=rgb("cc8218"))
    # o mel: mais escuro quanto mais embaixo
    t.pintar(t.m_ret(8, 16, 23, 27), rgb("f2a226"))
    t.pintar(t.m_ret(8, 21, 23, 27), rgb("e8901c"))
    t.pintar(t.m_ret(8, 25, 23, 27), rgb("d07812"))
    t.pintar(t.m_ret(8, 16, 10, 25), rgb("ffe08a"))
    t.pintar(t.m_ret(8, 16, 8, 21), rgb("fff4c8"))
    # bolhinhas
    for x, y in ((21, 18), (19, 24), (13, 26)):
        t.px(x, y, rgb("ffe9a0"))
    # a rotulinha de pergaminho, com um hexágono de favo
    t.bisel(t.m_ret(12, 19, 20, 25), rgb("fff0cc"), rgb("ffffff"), rgb("d8b878"), largura=1)
    hexa = [(16, 20.2), (18.2, 21.4), (18.2, 23.2), (16, 24.4), (13.8, 23.2), (13.8, 21.4)]
    t.pintar(t.m_poligono(hexa), rgb("e8a020"))
    t.px(15, 21, rgb("ffd060"))
    # a tampa de madeira, com veios
    tampa = t.m_ret_arredondado(7, 4, 24, 9, 1)
    t.bisel(tampa, rgb("a86e3a"), rgb("d8a468"), rgb("68401e"), largura=2, claro2=rgb("c08850"), escuro2=rgb("864e28"))
    for x, y in ((10, 6), (11, 6), (12, 6), (16, 7), (17, 7), (18, 7), (21, 6)):
        t.px(x, y, rgb("8a5428"))
    t.pintar(t.m_ret(9, 5, 12, 5), rgb("dcb078"))
    # o fio de mel escorrendo pelo ombro
    t.pintar(t.m_ret(20, 10, 22, 14), rgb("ffc232"))
    t.pintar(t.m_ret(21, 14, 22, 16), rgb("f0a824"))
    t.px(21, 17, rgb("ffd44a"))
    t.px(20, 10, rgb("ffe27a"))
    t.contorno(CONTORNO_QUENTE)
    return t


def colmeia():
    t = Tela(TAM, TAM)
    palha = dict(base=rgb("eab648"), claro=rgb("ffe594"), escuro=rgb("a86a1e"), claro2=rgb("f8cf70"), escuro2=rgb("c88a30"))

    def anel(x0, y0, x1, y1):
        t.bisel(t.m_ret_arredondado(x0, y0, x1, y1, 3), largura=2, **palha)
        for x in range(x0 + 3, x1 - 2, 4):               # as tranças de palha
            t.px(x, (y0 + y1) // 2, rgb("b87420"))
            t.px(x + 1, (y0 + y1) // 2 + 1, rgb("b87420"))

    t.bisel(t.m_elipse(16, 6.4, 3.4, 3.0), largura=2, **palha)
    anel(11, 8, 20, 12)
    anel(8, 13, 23, 17)
    anel(6, 18, 25, 22)
    anel(4, 23, 27, 27)
    t.bisel(t.m_ret(2, 27, 29, 29), rgb("9c6434"), rgb("cc9460"), rgb("5c381a"), largura=1)
    # a entrada: um arco escuro, com a borda de dentro iluminada
    arco = t.m_ret(13, 21, 18, 27) | t.m_elipse(15.5, 21.2, 3.0, 2.6)
    t.pintar(arco, rgb("2c1808"))
    t.pintar(t.m_ret(14, 25, 17, 27), rgb("6a3c10"))
    t.pintar(t.m_ret(15, 26, 16, 27), rgb("a8681c"))
    # a tabuinha de pouso
    t.bisel(t.m_ret(12, 28, 19, 29), rgb("b07840"), rgb("e0b078"), rgb("6c4420"), largura=1)
    for x, y in ((13, 9), (12, 14), (9, 19), (7, 24), (15, 5)):
        t.px(x, y, rgb("fff8d0"))
    t.contorno(CONTORNO_QUENTE)
    return t


def bandeira():
    t = Tela(TAM, TAM)
    t.bisel(t.m_ret(5, 4, 6, 29), rgb("b88a5a"), rgb("ecd0a0"), rgb("6c4224"), largura=1)
    t.bisel(t.m_elipse(5.5, 3.4, 2.6, 2.6), rgb("f8c83a"), rgb("fff2a0"), rgb("c88a12"), largura=1)
    # o pano ondulando: cada coluna sobe e desce um pouco
    pano = t.vazia()
    fase = lambda x: math.sin((x - 7) * 0.5) * 1.8
    for x in range(7, 29):
        topo = int(round(5 + fase(x)))
        base = int(round(17 + fase(x)))
        pano[topo:base + 1, x] = True
    # a ponta de andorinha: um corte em V na direita, que acompanha a onda
    for k in range(7):
        x = 28 - k
        meio = 11 + fase(x)
        metade = 3.6 - k * 0.55
        for y in range(t.h):
            if abs(y + 0.5 - meio) <= metade:
                pano[y, x] = False
    t.pintar(pano, rgb("d84038"))
    for x in range(7, 29):                                           # a luz e a sombra seguem a onda
        onda = math.cos((x - 7) * 0.5)
        ys = np.where(pano[:, x])[0]
        if len(ys) == 0:
            continue
        tom = rgb("ff7a60") if onda > 0.45 else rgb("a82a34") if onda < -0.45 else rgb("d84038")
        coluna = t.vazia()
        coluna[:, x] = True
        t.pintar(coluna & pano, tom)
    t.bisel(pano, None, rgb("ffb098"), rgb("781c2c"), largura=1)
    # o emblema: uma estrelinha amarela no meio
    est = []
    for i in range(10):
        raio = 3.6 if i % 2 == 0 else 1.5
        ang = -math.pi / 2 + i * math.pi / 5
        est.append((14.5 + math.cos(ang) * raio, 11.6 + math.sin(ang) * raio))
    e = t.m_poligono(est) & pano
    t.pintar(e, rgb("ffd23a"))
    t.px(13, 10, rgb("fff2a0"))
    t.px(13, 11, rgb("fff2a0"))
    t.pintar(t.m_elipse(5.5, 29.0, 4.4, 1.7), rgb("8a8a98"))
    t.pintar(t.m_ret(3, 28, 6, 28), rgb("c8c8d4"))
    t.contorno(CONTORNO_ROSA)
    return t


def sol():
    t = Tela(TAM, TAM)
    cx, cy = 16.0, 16.0
    raios = t.vazia()
    for i in range(8):
        ang = i * math.pi / 4
        c, s = math.cos(ang), math.sin(ang)
        base = 10.0
        largura = 2.4 if i % 2 == 0 else 1.9
        comprimento = 14.6 if i % 2 == 0 else 13.2
        raios |= t.m_poligono([(cx + c * base - s * largura, cy + s * base + c * largura),
                               (cx + c * base + s * largura, cy + s * base - c * largura),
                               (cx + c * comprimento, cy + s * comprimento)])
    t.bisel(raios, rgb("ffa626"), rgb("ffd870"), rgb("d46c0c"), largura=1)
    disco = t.m_elipse(cx, cy, 9.0, 9.0)
    t.bisel(disco, rgb("ffd23c"), rgb("fff0a0"), rgb("e8901c"), largura=3, claro2=rgb("ffe46a"), escuro2=rgb("f8b42c"))
    t.pintar(t.m_elipse(12.4, 11.6, 2.4, 2.0) & disco, rgb("fff8c8"))
    t.px(11, 11, rgb("ffffff"))
    t.px(12, 10, rgb("ffffff"))
    # a carinha serena
    for x, y in ((12, 15), (12, 16), (20, 15), (20, 16)):
        t.px(x, y, rgb("8a4a0c"))
    for x, y in ((13, 20), (14, 21), (15, 21), (16, 21), (17, 21), (18, 20)):
        t.px(x, y, rgb("b8620e"))
    for x, y in ((10, 18), (11, 18), (21, 18), (22, 18)):
        t.px(x, y, rgb("f08a54"))
    t.contorno(CONTORNO_QUENTE)
    return t


def flor():
    t = Tela(TAM, TAM)
    cx, cy = 16.0, 16.0
    petalas = t.vazia()
    for i in range(6):
        ang = -math.pi / 2 + i * math.pi / 3
        petalas |= t.m_elipse_rot(cx + math.cos(ang) * 8.2, cy + math.sin(ang) * 8.2, 6.0, 4.5, ang)
    t.bisel(petalas, rgb("ee6698"), rgb("ffb4d0"), rgb("a83468"), largura=2, claro2=rgb("f888b4"), escuro2=rgb("cc4c84"))
    # as divisas entre as pétalas
    for i in range(6):
        ang = -math.pi / 2 + i * math.pi / 3 + math.pi / 6
        for r in range(6, 14):
            x, y = int(cx + math.cos(ang) * r), int(cy + math.sin(ang) * r)
            if petalas[y, x]:
                t.px(x, y, rgb("b83c74"))
    miolo = t.m_elipse(cx, cy, 5.0, 5.0)
    t.bisel(miolo, rgb("ffd23c"), rgb("fff2a0"), rgb("d8821a"), largura=2, claro2=rgb("ffe262"), escuro2=rgb("f0a828"))
    for x, y in ((14, 14), (17, 15), (15, 17), (18, 18), (13, 17)):
        t.px(x, y, rgb("c8721a"))
    t.px(13, 13, rgb("ffffff"))
    t.px(14, 13, rgb("fff6c0"))
    for x, y in ((14, 3), (15, 3), (5, 11), (6, 10), (24, 8), (9, 6)):
        if petalas[y, x]:
            t.px(x, y, rgb("ffd8e8"))
    t.contorno(CONTORNO_ROSA)
    return t


def bomba():
    t = Tela(TAM, TAM)
    corpo = t.m_elipse(15.2, 19.6, 11.2, 11.2)
    t.bisel(corpo, rgb("3e3e54"), rgb("8a8aa8"), rgb("14141e"), largura=3, claro2=rgb("62627e"), escuro2=rgb("26263a"))
    t.pintar(t.m_elipse(10.8, 14.8, 3.0, 2.2) & corpo, rgb("c8c8e0"))
    t.pintar(t.m_elipse(10.4, 14.4, 1.6, 1.2) & corpo, rgb("ffffff"))
    t.px(13, 12, rgb("e0e0f4"))
    t.px(8, 18, rgb("b0b0cc"))
    t.px(9, 19, rgb("8a8aa8"))
    # o bocal metálico e o pavio com a faísca
    t.bisel(t.m_ret(18, 6, 25, 10), rgb("8a8296"), rgb("c8c0d8"), rgb("4a4458"), largura=1)
    t.pintar(t.m_ret(19, 7, 20, 8), rgb("e8e0f4"))
    for x, y in ((24, 5), (25, 4), (26, 4), (27, 3), (28, 3), (28, 4)):
        t.px(x, y, rgb("c8a468"))
        if x > 24:
            t.px(x, y + 1, rgb("8a6a3c"))
    t.pintar(t.m_poligono([(28.5, 0.4), (30, 2.6), (32, 3.2), (30, 4.2), (30.6, 6.4), (28.5, 5), (26.4, 6.4), (27, 4.2), (25, 3.2), (27, 2.6)]),
             rgb("ff9a22"))
    t.pintar(t.m_elipse(28.5, 3.4, 1.4, 1.4), rgb("fff2a0"))
    t.px(28, 3, rgb("ffffff"))
    t.contorno(CONTORNO_ESCURO)
    return t


def toco():
    """O toco que fica quando uma planta é podada (24x18)."""
    t = Tela(24, 18)
    t.bisel(t.m_ret_arredondado(4, 6, 19, 15, 2), rgb("8a5a30"), rgb("b8844e"), rgb("503018"), largura=2, claro2=rgb("a06c3c"), escuro2=rgb("6e4424"))
    for x in (8, 11, 15):
        for y in range(8, 15):
            if (x + y) % 3:
                t.px(x, y, rgb("5e3a1e"))
    topo = t.m_elipse(11.5, 6.4, 7.8, 3.6)
    t.bisel(topo, rgb("d8a868"), rgb("f0d09a"), rgb("a8743c"), largura=1)
    t.pintar(t.m_elipse(11.5, 6.4, 4.6, 2.0), rgb("c08848"))
    t.pintar(t.m_elipse(11.5, 6.4, 2.2, 0.9), rgb("e8c488"))
    t.px(10, 6, rgb("8a5a2c"))
    t.contorno(CONTORNO_QUENTE)
    return t


TODOS = {"estrela": estrela, "gota": gota, "pote_de_mel": pote_de_mel, "colmeia": colmeia, "bandeira": bandeira,
         "sol": sol, "flor": flor, "bomba": bomba, "toco": toco}
