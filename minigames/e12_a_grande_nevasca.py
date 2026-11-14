# -*- coding: utf-8 -*-
"""Minigames do Evento 12 — A Grande Nevasca.

Qual JOGO cada conselheira joga neste evento (None = ação direta, sem minigame).
Para forçar a dificuldade só deste evento, acrescente DIFICULDADE = n (1 a 5).
"""
from minigames.jogos.antes_da_poda import AntesDaPoda
from minigames.jogos.rastro_de_polen import RastroDePolen
from minigames.jogos.rota_de_voo import RotaDeVoo
from minigames.jogos.sob_as_folhas import SobAsFolhas

JOGOS = {
    "Melina": RastroDePolen,
    "Flora": SobAsFolhas,
    "Nectar": RotaDeVoo,
    "Aurora": AntesDaPoda,
}
