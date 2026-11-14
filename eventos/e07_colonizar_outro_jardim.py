# -*- coding: utf-8 -*-
"""Evento 7 — Colonizar Outro Jardim (Outono).

A SITUAÇÃO: o texto de abertura e as opções, com o preço de cada uma.
  custo   {mel, operarias, relacao}: negativo paga, positivo ganha ("tudo" = todo o mel)

O jogo de cada conselheira está em minigames/e07_colonizar_outro_jardim.py; os efeitos, em
resultados/e07_colonizar_outro_jardim.py.
"""

EVENTO = {
    "id": 7,
    "estacao": "Outono",
    "titulo": "Colonizar Outro Jardim",
    "contexto":
        "Um jardim vizinho, ainda livre, pode se tornar uma extensão da colônia antes "
        "do inverno.",
    "opcoes": [
        {
            "conselheira": "Melina",
            "acao":
                "Colonizar o jardim para garantir mais uma fonte de reservas",
            "custo": {"mel": -2, "operarias": -8, "relacao": -2},
        },
        {
            "conselheira": "Flora",
            "acao":
                "Colonizar de forma gradual, preservando a vegetação já existente",
            "custo": {"mel": -7, "operarias": 0, "relacao": 2},
        },
        {
            "conselheira": "Nectar",
            "acao":
                "Usar o novo jardim como posto avançado de pesquisa",
            "custo": {"mel": -10, "operarias": 0, "relacao": -1},
        },
        {
            "conselheira": "Aurora",
            "acao":
                "Propor a colonização conjunta com outra colmeia amiga",
            "custo": {"mel": -5, "operarias": 0, "relacao": 3},
        },
    ],
}
