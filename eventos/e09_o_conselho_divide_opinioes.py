# -*- coding: utf-8 -*-
"""Evento 9 — O Conselho Divide Opiniões (Outono).

A SITUAÇÃO: o texto de abertura e as opções, com o preço de cada uma.
  custo   {mel, operarias, relacao}: negativo paga, positivo ganha ("tudo" = todo o mel)

O jogo de cada conselheira está em minigames/e09_o_conselho_divide_opinioes.py; os efeitos, em
resultados/e09_o_conselho_divide_opinioes.py.
"""

EVENTO = {
    "id": 9,
    "estacao": "Outono",
    "titulo": "O Conselho Divide Opiniões",
    "contexto":
        "Pela primeira vez, duas conselheiras discordam abertamente na frente da "
        "colônia sobre qual prioridade definirá o preparo para o inverno.",
    "opcoes": [
        {
            "conselheira": "Flora",
            "acao":
                "Dar prioridade total à recuperação do ecossistema antes do frio",
            "custo": {"mel": -10, "operarias": 0, "relacao": -1},
        },
        {
            "conselheira": "Melina",
            "acao":
                "Dar prioridade total ao acúmulo de reservas",
            "custo": {"mel": -8, "operarias": 0, "relacao": -3},
        },
        {
            "conselheira": "Nectar",
            "acao":
                "Propor uma solução técnica que tente equilibrar as duas demandas",
            "custo": {"mel": -10, "operarias": 0, "relacao": -1},
        },
        {
            "conselheira": "Aurora",
            "acao":
                "Mediar o debate publicamente e buscar consenso entre as conselheiras",
            "custo": {"mel": -5, "operarias": 0, "relacao": 5},
        },
    ],
}
