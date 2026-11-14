# -*- coding: utf-8 -*-
"""O POPUP DO INÍCIO DO MINIGAME e o botão "Tentar de novo" da tela de resultado.

  - Antes de cada minigame começar, a tela do jogo aparece com o fundo escurecido e um popup com o nome do jogo
    e o botão "Iniciar". O jogo fica PARADO (o tempo só começa a contar quando você clica em Iniciar; o ENTER
    também inicia).
  - Na tela de resultado, quando deu FALHA ou PARCIAL, aparece o botão "Tentar de novo": ele desfaz o resultado
    daquela tentativa (as moedas voltam ao que eram) e começa o MESMO jogo outra vez.

Quem decide o que cada botão faz é o main.py; este arquivo só DESENHA e diz qual botão foi clicado.
O estilo é o mesmo do popup de "Voltar ao menu inicial?" (telas/confirmacao.py).
"""
import pygame

from config import LARGURA, ALTURA
from telas import layout as L
from telas.componentes import painel, escrever, texto

# ============================================================
# AJUSTES -- os textos, o tamanho e as regras
# ============================================================
NOVAS_TENTATIVAS_POR_JOGO = None         # None = quantas vezes a jogadora quiser | 1 = só uma nova tentativa | 0 = sem o botão
TEXTO_DO_INICIAR = "Iniciar"
MENSAGEM_DO_INICIO = "Tudo pronto? O tempo só começa a contar quando você clicar em Iniciar."
TEXTO_DO_TENTAR_DE_NOVO = "Tentar de novo"
BOTOES_DO_INICIO = [(TEXTO_DO_INICIAR, "iniciar")]

FUNDO_ESCURO = (0, 0, 0, 165)            # a cor que escurece a tela (R, G, B, quão escuro: 0 a 255)
POPUP_TAMANHO = (460, 220)               # largura e altura do popup
POPUP_TITULO_DO_TOPO = 40                # distância do título até o topo do popup
POPUP_MENSAGEM_DO_TOPO = 84              # distância da mensagem até o topo do popup
POPUP_MARGEM_DA_MENSAGEM = 36            # a mensagem não encosta nas laterais por esta margem
BOTAO_TAMANHO = (170, 46)
BOTAO_DA_BASE = 30                       # distância dos botões até a base do popup
ESPACO_ENTRE_OS_BOTOES = 30
BOTAO_DE_NOVO_TAMANHO = (210, 46)        # o botão "Tentar de novo" da tela de resultado
BOTAO_DE_NOVO_DA_BASE = 28               # distância dele até a base do card do resultado


def retangulo_do_popup():
    r = pygame.Rect(0, 0, *POPUP_TAMANHO)
    r.center = (LARGURA // 2, ALTURA // 2)
    return r


def retangulos_dos_botoes(botoes):
    """Os retângulos dos botões do popup, da esquerda para a direita, centralizados."""
    p = retangulo_do_popup()
    largura, altura = BOTAO_TAMANHO
    total = len(botoes) * largura + (len(botoes) - 1) * ESPACO_ENTRE_OS_BOTOES
    x = p.centerx - total // 2
    retangulos = []
    for _ in botoes:
        r = pygame.Rect(x, 0, largura, altura)
        r.bottom = p.bottom - BOTAO_DA_BASE
        retangulos.append(r)
        x += largura + ESPACO_ENTRE_OS_BOTOES
    return retangulos


def botao_em(posicao, botoes):
    """A chave do botão (a segunda parte de cada par) que está nesta posição do mouse, ou None."""
    for (_, chave), r in zip(botoes, retangulos_dos_botoes(botoes)):
        if r.collidepoint(posicao):
            return chave
    return None


def _botao(v, r, rotulo, mouse):
    fundo = L.COR_CARD_COM_MOUSE if r.collidepoint(mouse) else L.COR_CARD
    pygame.draw.rect(v.tela, fundo, r, border_radius=L.CARD_RAIO)
    pygame.draw.rect(v.tela, L.DOURADO, r, 3, border_radius=L.CARD_RAIO)
    escrever(v, rotulo, "botao", L.ESCURO, centro=r.center)


def desenhar(v, mouse, titulo, mensagem, botoes):
    """Escurece a tela e desenha o popup (título, mensagem e botões) por cima de tudo."""
    veu = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    veu.fill(FUNDO_ESCURO)
    v.tela.blit(veu, (0, 0))

    p = retangulo_do_popup()
    painel(v.tela, p, alfa=255)
    escrever(v, titulo, "subtitulo", L.ESCURO, topo_centro=(p.centerx, p.top + POPUP_TITULO_DO_TOPO))
    caixa = pygame.Rect(p.left + POPUP_MARGEM_DA_MENSAGEM, p.top + POPUP_MENSAGEM_DO_TOPO,
                        p.width - 2 * POPUP_MARGEM_DA_MENSAGEM, 60)
    texto(v, mensagem, caixa, "corpo", alinhamento="centro")
    for (rotulo, _), r in zip(botoes, retangulos_dos_botoes(botoes)):
        _botao(v, r, rotulo, mouse)


def retangulo_do_botao_de_novo(card):
    """Onde fica o botão "Tentar de novo": embaixo, no meio do card do resultado."""
    r = pygame.Rect(0, 0, *BOTAO_DE_NOVO_TAMANHO)
    r.midbottom = (card.centerx, card.bottom - BOTAO_DE_NOVO_DA_BASE)
    return r


def desenhar_botao_de_novo(v, card, restantes=None):
    """Desenha o botão "Tentar de novo" no card do resultado e devolve o retângulo dele (para o clique)."""
    r = retangulo_do_botao_de_novo(card)
    rotulo = TEXTO_DO_TENTAR_DE_NOVO if restantes is None else f"{TEXTO_DO_TENTAR_DE_NOVO} ({restantes})"
    _botao(v, r, rotulo, pygame.mouse.get_pos())
    return r
