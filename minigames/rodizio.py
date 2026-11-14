# -*- coding: utf-8 -*-
"""O RODÍZIO DOS MINIGAMES.

Depois de cada decisão a jogadora joga UM minigame, sempre na ordem abaixo,
qualquer que seja a conselheira escolhida:

    decisão 1 -> jogo 1, decisão 2 -> jogo 2, ... decisão 12 -> jogo 12.

Com um jogo para cada um dos 12 eventos, cada jogo aparece uma vez só e a dificuldade vem da
ESTAÇÃO do evento (DIFICULDADE_POR_ESTACAO, em config.py): Primavera 1, Verão 2, Outono 3,
Inverno 4. Para mudar a ordem, é só trocar as linhas de lugar na lista.

Se a lista tiver MENOS jogos que eventos, ela recomeça do jogo 1 (uma nova "volta") e a
dificuldade passa a vir de DIFICULDADE_POR_VOLTA (config.py).

Para desligar o rodízio e voltar ao jogo de cada conselheira (minigames/eNN_*.py), use
MINIGAMES_EM_RODIZIO = False em config.py.
"""
from minigames.jogos.antes_da_poda import AntesDaPoda
from minigames.jogos.campo_minado import CampoMinado
from minigames.jogos.captura_de_abelhas import CapturaDeAbelhas
from minigames.jogos.comunicacao_em_simbolos import ComunicacaoEmSimbolos
from minigames.jogos.domino import Domino
from minigames.jogos.jogo_da_memoria import JogoDaMemoria
from minigames.jogos.labirinto import Labirinto
from minigames.jogos.quebra_cabeca_de_encaixe import QuebraCabecaDeEncaixe
from minigames.jogos.quebra_cabeca_de_soma import QuebraCabecaDeSoma
from minigames.jogos.rastro_de_polen import RastroDePolen
from minigames.jogos.rota_de_voo import RotaDeVoo
from minigames.jogos.sob_as_folhas import SobAsFolhas

# a ordem dos jogos (1 a 12), um por evento
ORDEM = [
    SobAsFolhas,             # 1   Primavera
    RastroDePolen,           # 2
    RotaDeVoo,               # 3
    AntesDaPoda,             # 4   Verão
    CapturaDeAbelhas,        # 5
    JogoDaMemoria,           # 6
    QuebraCabecaDeSoma,      # 7   Outono
    CampoMinado,             # 8
    ComunicacaoEmSimbolos,   # 9
    Labirinto,               # 10  Inverno
    Domino,                  # 11
    QuebraCabecaDeEncaixe,   # 12
]
