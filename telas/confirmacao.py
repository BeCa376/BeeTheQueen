# -*- coding: utf-8 -*-
"""O POPUP "Voltar ao menu inicial?": aparece ao clicar na seta do menu (embaixo, à esquerda).

O fundo escurece, e o popup avisa que o jogo não será salvo, com dois botões:
    OK        -> volta ao menu inicial (a partida é zerada)
    Cancelar  -> o popup some e o jogo continua de onde estava (o ESC também cancela)
Enquanto o popup está aberto, o jogo fica PARADO (o relógio do minigame não corre).

Quem decide o que cada botão faz é o main.py (tratar_confirmacao_de_saida); este arquivo só
DESENHA o popup e diz qual botão foi clicado.
"""
import pygame

from config import LARGURA, ALTURA
from telas import layout as L
from telas.componentes import painel, escrever, texto

# ============================================================
# AJUSTES -- os textos, o tamanho e as cores do popup
# ============================================================
TITULO = "Voltar ao menu inicial?"
MENSAGEM = "O jogo não será salvo: você perderá o progresso desta partida."
TEXTO_DO_CANCELAR = "Cancelar"
TEXTO_DO_OK = "OK"

FUNDO_ESCURO = (0, 0, 0, 165)            # a cor que escurece a tela (R, G, B, quão escuro: 0 a 255)
POPUP_TAMANHO = (460, 220)               # largura e altura do popup
POPUP_TITULO_DO_TOPO = 40                # distância do título até o topo do popup
POPUP_MENSAGEM_DO_TOPO = 84              # distância da mensagem até o topo do popup
POPUP_MARGEM_DA_MENSAGEM = 36            # a mensagem não encosta nas laterais por esta margem
BOTAO_TAMANHO = (150, 46)
BOTAO_DA_BASE = 30                       # distância dos botões até a base do popup
ESPACO_ENTRE_OS_BOTOES = 30


def retangulo_do_popup():
    r = pygame.Rect(0, 0, *POPUP_TAMANHO)
    r.center = (LARGURA // 2, ALTURA // 2)
    return r


def retangulo_do_botao(qual):
    """O retângulo do botão "cancelar" (esquerda) ou "ok" (direita)."""
    p = retangulo_do_popup()
    largura, altura = BOTAO_TAMANHO
    r = pygame.Rect(0, 0, largura, altura)
    r.bottom = p.bottom - BOTAO_DA_BASE
    deslocamento = (largura + ESPACO_ENTRE_OS_BOTOES) // 2
    r.centerx = p.centerx - deslocamento if qual == "cancelar" else p.centerx + deslocamento
    return r


def botao_em(posicao):
    """Qual botão está nesta posição do mouse: "ok", "cancelar" ou None."""
    for qual in ("cancelar", "ok"):
        if retangulo_do_botao(qual).collidepoint(posicao):
            return qual
    return None


def desenhar(v, mouse):
    """Escurece a tela e desenha o popup por cima de tudo."""
    veu = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    veu.fill(FUNDO_ESCURO)
    v.tela.blit(veu, (0, 0))

    p = retangulo_do_popup()
    painel(v.tela, p, alfa=255)
    escrever(v, TITULO, "subtitulo", L.ESCURO, topo_centro=(p.centerx, p.top + POPUP_TITULO_DO_TOPO))
    caixa = pygame.Rect(p.left + POPUP_MARGEM_DA_MENSAGEM, p.top + POPUP_MENSAGEM_DO_TOPO,
                        p.width - 2 * POPUP_MARGEM_DA_MENSAGEM, 60)
    texto(v, MENSAGEM, caixa, "corpo", alinhamento="centro")

    for qual, rotulo in (("cancelar", TEXTO_DO_CANCELAR), ("ok", TEXTO_DO_OK)):
        botao = retangulo_do_botao(qual)
        fundo = L.COR_CARD_COM_MOUSE if botao.collidepoint(mouse) else L.COR_CARD
        pygame.draw.rect(v.tela, fundo, botao, border_radius=L.CARD_RAIO)
        pygame.draw.rect(v.tela, L.DOURADO, botao, 3, border_radius=L.CARD_RAIO)
        escrever(v, rotulo, "botao", L.ESCURO, centro=botao.center)
