# -*- coding: utf-8 -*-
"""Evento 8 — Excesso de Produção (Outono).

A SITUAÇÃO: o texto de abertura e as opções, com o preço de cada uma.
  custo   {mel, operarias, relacao}: negativo paga, positivo ganha ("tudo" = todo o mel)

O jogo de cada conselheira está em minigames/e08_excesso_de_producao.py; os efeitos, em
resultados/e08_excesso_de_producao.py.
"""

EVENTO = {
    "id": 8,
    "estacao": "Outono",
    "titulo": "Excesso de Produção",
    "contexto":
        "A colheita do ano rendeu mais mel do que a estrutura atual comporta, sem "
        "espaço, parte dele será perdido.",
    "opcoes": [
        {
            "conselheira": "Melina",
            "acao":
                "Expandir os favos às pressas para não perder nada",
            "custo": {"mel": -18, "operarias": 0, "relacao": -2},
        },
        {
            "conselheira": "Nectar",
            "acao":
                "Testar um novo formato hexagonal mais eficiente de armazenamento",
            "custo": {"mel": -10, "operarias": 0, "relacao": -1},
        },
        {
            "conselheira": "Flora",
            "acao":
                "Doar o excedente para polinizar áreas que precisam de recuperação",
            "custo": {"mel": -4, "operarias": 0, "relacao": 3},
        },
        {
            "conselheira": "Aurora",
            "acao":
                "Repartir o excedente com colmeias vizinhas em dificuldade",
            "custo": {"mel": -6, "operarias": 0, "relacao": 4},
        },
    ],
}
