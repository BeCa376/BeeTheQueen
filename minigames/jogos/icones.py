# -*- coding: utf-8 -*-
"""Peças comuns aos minigames: os ícones em pixel art, as fontes e a linha de texto + barra que fica embaixo da
área do jogo.

Os ícones são os desenhos de assets/pixel/ (flor, colmeia, bandeira, gota, sol, pote de mel, estrela) e os seus
próprios desenhos de assets/ (a abelha, a folha e a joaninha). Para trocar um, abra o PNG/.ase no Aseprite e salve
por cima: o jogo usa a versão nova. Os jogos chamam desenhar_icone("flor", ...), nunca o desenho direto.
"""
import functools

import pygame

from . import pixel

TEXTO = (40, 40, 40)
OURO = (214, 158, 46)
CINZA_CLARO = (230, 230, 230)
GRAMA = (170, 205, 130)
MEL = (240, 190, 70)
MEL_ESCURO = (200, 140, 30)
PAPEL = (250, 244, 226)
VERDE = (110, 175, 100)
VERMELHO = (205, 85, 80)
AZUL_AGUA = (95, 160, 215)

# os nomes dos ícones que existem (o jogo da memória sorteia entre eles)
NOMES_DOS_ICONES = ["flor", "colmeia", "bandeira", "gota", "animal", "sol", "folha", "pote", "estrela", "abelha"]


@functools.lru_cache(maxsize=None)
def fonte(tamanho=13, negrito=False):
    """A fonte dos textos de dentro dos jogos (a mesma família dos outros jogos)."""
    return pygame.font.SysFont("verdana", tamanho, bold=negrito)


def escrever(surface, texto, posicao, tamanho=13, cor=TEXTO, negrito=False, centro=False):
    """Escreve um texto; `posicao` é o canto de cima à esquerda (ou o centro, com centro=True)."""
    imagem = fonte(tamanho, negrito).render(str(texto), True, cor)
    retangulo = imagem.get_rect()
    if centro:
        retangulo.center = posicao
    else:
        retangulo.topleft = posicao
    surface.blit(imagem, retangulo)
    return retangulo


def linha_de_status(surface, area, texto, fracao):
    """O texto e a barrinha embaixo da área do jogo (o mesmo lugar dos jogos antigos).
    `fracao` (0 a 1) é quanto da barra está cheio."""
    escrever(surface, texto, (area.left, area.bottom + 10))
    pixel.barra(surface, pygame.Rect(area.left, area.bottom + 26, area.width, 10), fracao)


def desenhar_icone(nome, surface, centro, tamanho, sombra=True):
    """Desenha o ícone `nome` centrado em `centro`, cabendo (aproximadamente) num quadrado de lado `tamanho`.
    Tem uma sombrinha embaixo e à direita, como a luz vem de cima à esquerda."""
    pixel.colar(surface, pixel.icone(nome, tamanho), centro=centro, sombra=sombra)
