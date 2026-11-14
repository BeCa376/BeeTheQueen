# -*- coding: utf-8 -*-
"""Molduras de 9 fatias (campo, cartas, caixas), o bloco neutro das peças, o pote grande da soma, a bolinha do
dominó e a gotinha pequena do Campo Minado."""
import random

import numpy as np

from pxart import Tela, rgb, mais_escuro

# nome -> (contorno, luz, sombra, linha de dentro)
ESTILOS_DE_BORDA = {
    "carta_creme": (rgb("5c4228"), rgb("fffcee"), rgb("cebc92"), rgb("ecdebc")),
    "carta_ambar": (rgb("52300a"), rgb("ffe078"), rgb("aa6612"), rgb("d69624")),
    "carta_verde": (rgb("28603a"), rgb("d2f8c8"), rgb("60a458"), rgb("aadea0")),
    "carta_osso": (rgb("54462e"), rgb("fffef6"), rgb("d6ccb6"), rgb("ece4ce")),
    "placa_madeira": (rgb("32200e"), rgb("d6a870"), rgb("6e4828"), rgb("96683e")),
    "caixa_funda": (rgb("6e5c3c"), rgb("96866a"), rgb("faf0d6"), rgb("beaa80")),
}


def borda(nome, lado=10, b=3):
    """A moldura de uma carta/caixa: contorno, luz em cima/esquerda, sombra embaixo/direita, uma linha de acabamento.
    O miolo é transparente (o jogo preenche com cor ou com um fundo)."""
    contorno, luz, sombra, linha = ESTILOS_DE_BORDA[nome]
    funda = nome == "caixa_funda"
    t = Tela(lado, lado)
    for y in range(lado):
        for x in range(lado):
            dt, dl, db, dr = y, x, lado - 1 - y, lado - 1 - x
            r = min(dt, dl, db, dr)
            if r >= b:
                continue
            canto = (min(dt, db) == r and min(dl, dr) == r and (dt == dl or dt == dr or db == dl or db == dr) and r == 0)
            if canto and ((dt == 0 and dl == 0) or (dt == 0 and dr == 0) or (db == 0 and dl == 0) or (db == 0 and dr == 0)):
                continue                                                      # o cantinho arredondado
            if r == 0:
                cor = contorno
            elif r == b - 1:
                cor = linha
            else:
                lado_claro = min(dt, dl) <= min(db, dr)
                cor = luz if lado_claro else sombra
                if funda:
                    cor = luz if lado_claro else sombra
            t.px(x, y, cor)
    # os cantos de dentro do contorno (para a curva fechar bonito)
    for (x, y) in ((1, 1), (lado - 2, 1), (1, lado - 2), (lado - 2, lado - 2)):
        t.px(x, y, contorno if r == 0 else (luz if (x, y) == (1, 1) else sombra))
    return t


def borda_do_campo(lado=12, b=4):
    """A moldura de madeira em volta do campo de cada minigame (fica POR FORA da área jogável)."""
    contorno = rgb("2e1e14")
    t = Tela(lado, lado)
    for y in range(lado):
        for x in range(lado):
            dt, dl, db, dr = y, x, lado - 1 - y, lado - 1 - x
            r = min(dt, dl, db, dr)
            if r >= b:
                continue
            if r == 0 and min(dt, db) == 0 and min(dl, dr) == 0:
                continue                                                      # cantinho arredondado
            claro_lado = min(dt, dl) < min(db, dr)
            escuro_lado = min(db, dr) < min(dt, dl)
            if r == 0:
                cor = contorno
            elif r == 1:
                cor = rgb("c8986a") if claro_lado else rgb("7a4e2c") if escuro_lado else rgb("a47448")
            elif r == 2:
                cor = rgb("a8764a") if claro_lado else rgb("62402a") if escuro_lado else rgb("86603c")
            else:                                                             # o filete de dentro: sombra em cima, luz embaixo
                cor = rgb("3a2818") if claro_lado else rgb("b88c5e") if escuro_lado else rgb("5e4228")
            t.px(x, y, cor)
    return t


def bloco_neutro():
    """Um quadradinho de peça (10x10), quase branco, com volume: o jogo pinta por cima multiplicando pela cor."""
    t = Tela(10, 10)
    t.bisel(t.m_ret(0, 0, 9, 9), rgb("ebebeb"), rgb("ffffff"), rgb("a8a8a8"), largura=1)
    rng = random.Random(4)
    for _ in range(10):
        t.px(rng.randrange(2, 8), rng.randrange(2, 8), rgb("e0e0e0") if rng.random() < 0.6 else rgb("f6f6f6"))
    for x, y in ((1, 1), (2, 1), (1, 2)):
        t.px(x, y, rgb("ffffff"))
    for x, y in ((8, 8), (7, 8), (8, 7)):
        t.px(x, y, rgb("c4c4c4"))
    return t


def pote_da_soma():
    """O pote de mel grande do jogo da soma (36x46). O rótulo fica vazio: o número é escrito por cima."""
    t = Tela(36, 46)
    corpo = t.m_ret_arredondado(3, 15, 32, 44, 4)
    ombro = t.m_ret(7, 11, 28, 15)
    vidro = corpo | ombro
    t.bisel(vidro, rgb("f4aa24"), rgb("ffd976"), rgb("a8620c"), largura=3, claro2=rgb("f8c04a"), escuro2=rgb("cc8218"))
    t.pintar(t.m_ret(7, 19, 28, 41), rgb("f2a226"))
    t.pintar(t.m_ret(7, 30, 28, 41), rgb("e8901c"))
    t.pintar(t.m_ret(7, 37, 28, 41), rgb("d07812"))
    t.pintar(t.m_ret(7, 19, 10, 38), rgb("ffe08a"))
    t.pintar(t.m_ret(7, 19, 8, 30), rgb("fff4c8"))
    for x, y in ((24, 22), (22, 36), (12, 40), (26, 32)):
        t.px(x, y, rgb("ffe9a0"))
    # o rótulo de pergaminho (o número vai aqui)
    t.bisel(t.m_ret_arredondado(11, 24, 25, 37, 1), rgb("fff2d2"), rgb("ffffff"), rgb("d6b476"), largura=1)
    # a tampa de madeira
    tampa = t.m_ret_arredondado(5, 3, 30, 11, 2)
    t.bisel(tampa, rgb("a86e3a"), rgb("d8a468"), rgb("68401e"), largura=2, claro2=rgb("c08850"), escuro2=rgb("864e28"))
    for x, y in ((9, 6), (10, 6), (11, 6), (12, 6), (17, 8), (18, 8), (19, 8), (24, 6), (25, 6)):
        t.px(x, y, rgb("8a5428"))
    t.pintar(t.m_ret(8, 5, 12, 5), rgb("dcb078"))
    # o mel escorrendo pelo ombro
    t.pintar(t.m_ret(25, 11, 27, 18), rgb("ffc232"))
    t.pintar(t.m_ret(26, 18, 27, 21), rgb("f0a824"))
    t.px(26, 22, rgb("ffd44a"))
    t.px(25, 11, rgb("ffe27a"))
    t.contorno(rgb("3a2214"))
    return t


def pinta_do_domino():
    """A bolinha azul do dominó (5x5), como uma pedrinha com brilho."""
    t = Tela(5, 5)
    t.pintar(t.m_ret(1, 0, 3, 0) | t.m_ret(0, 1, 4, 3) | t.m_ret(1, 4, 3, 4), rgb("2a5ca8"))
    t.pintar(t.m_ret(1, 1, 3, 3), rgb("4a8ae0"))
    t.px(1, 1, rgb("c4e2ff"))
    t.px(2, 1, rgb("8cc0f4"))
    t.px(1, 2, rgb("8cc0f4"))
    t.px(3, 3, rgb("2e68b8"))
    t.px(2, 3, rgb("3a78cc"))
    t.px(3, 2, rgb("3a78cc"))
    return t


def gota_pequena():
    """A gotinha do quadrado seguro do Campo Minado (12x12)."""
    t = Tela(12, 12)
    corpo = t.m_elipse(6, 7.6, 3.8, 3.8)
    ponta = t.m_poligono([(6, 1.0), (2.4, 6.4), (9.6, 6.4)])
    m = corpo | ponta
    t.bisel(m, rgb("3a8ae6"), rgb("8ad0ff"), rgb("1c56b4"), largura=1)
    t.px(4, 7, rgb("e0f4ff"))
    t.px(4, 8, rgb("b4e4ff"))
    t.px(5, 4, rgb("d8f2ff"))
    t.contorno(rgb("12204c"))
    return t


def brilho_do_pote():
    """O brilho dourado em volta do pote levantado (64x80, translúcido), para destacar o pote escolhido."""
    t = Tela(48, 64)
    for y in range(64):
        for x in range(48):
            d = ((x + 0.5 - 24) / 24.0) ** 2 + ((y + 0.5 - 34) / 30.0) ** 2
            if d < 1.0:
                a = int(130 * (1 - d) ** 1.4)
                t.px(x, y, rgb("ffd45a"), a)
    return t


MOLDURAS = {n: borda(n) for n in ESTILOS_DE_BORDA}
