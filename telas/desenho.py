# -*- coding: utf-8 -*-
"""O ROTEADOR DAS TELAS: dado qual tela o jogo está mostrando, chama a função
que a desenha. Para uma tela nova: escreva a função (em introduction.py,
evento.py, minigame.py ou final.py) e acrescente uma linha aqui."""
import pygame

import config
from telas import introduction, evento, minigame, final, confirmacao, popup
from telas.componentes import barra_de_tempo


def desenhar(v, j, mouse):
    """Desenha a tela atual do jogo `j` (o que o main.py mantém)."""
    v.desenhar_fundo()
    tela = j.tela
    if tela == config.ABERTURA:
        introduction.abertura(v, j)
    elif tela == config.CONSELHEIRA:
        introduction.conselheira(v, j)
    elif tela == config.NOVA_RAINHA:
        introduction.nova_rainha(v, j)
    elif tela == config.ESTACAO:
        introduction.estacao(v, j)
    elif tela == config.CONTEXTO:
        evento.contexto(v, j)
    elif tela == config.ESCOLHA:
        evento.escolha(v, j, mouse)
    elif tela == config.PREPARO:
        minigame.preparo(v, j)
    elif tela == config.MINIGAME:
        minigame.jogo(v, j)
    elif tela == config.RESULTADO_DO_MINIGAME:
        minigame.resultado_do_minigame(v, j)
    elif tela == config.CONSEQUENCIA:
        final.consequencia(v, j)
    elif tela == config.FINAL:
        final.final(v, j, mouse)
    if tela in config.TELAS_COM_SETA_DO_MENU:
        v.desenhar_seta_do_menu()
    if config.MOSTRAR_BARRA_DE_TEMPO:
        barra_de_tempo(v, j)
    if j.confirmando_saida:                  # o popup "Voltar ao menu?", por cima de tudo
        confirmacao.desenhar(v, mouse)
    if j.aguardando_inicio and not j.confirmando_saida and tela == config.MINIGAME:    # o popup "Iniciar"
        popup.desenhar(v, mouse, j.nome_do_minigame, popup.MENSAGEM_DO_INICIO, popup.BOTOES_DO_INICIO)
    pygame.display.flip()
