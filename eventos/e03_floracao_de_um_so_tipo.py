# -*- coding: utf-8 -*-
"""Evento 3 — Floração de Um Só Tipo (Primavera).

A SITUAÇÃO: o texto de abertura e as opções, com o preço de cada uma.
  custo   {mel, operarias, relacao}: negativo paga, positivo ganha ("tudo" = todo o mel)

O jogo de cada conselheira está em minigames/e03_floracao_de_um_so_tipo.py; os efeitos, em
resultados/e03_floracao_de_um_so_tipo.py.
"""

EVENTO = {
    "id": 3,
    "estacao": "Primavera",
    "titulo": "Floração de Um Só Tipo",
    "contexto":
        "Um campo próximo floresce com uma única espécie, em grande quantidade! "
        "Tentador, mas uma monocultura empobrece o solo com o tempo.",
    "opcoes": [
        {
            "conselheira": "Flora",
            "acao":
                "Recusar o excesso e priorizar campos diversos, mesmo rendendo menos "
                "agora",
            "custo": {"mel": -6, "operarias": 0, "relacao": 2},
        },
        {
            "conselheira": "Melina",
            "acao":
                "Explorar ao máximo enquanto a floração dura",
            "custo": {"mel": 4, "operarias": 0, "relacao": -4},
        },
        {
            "conselheira": "Nectar",
            "acao":
                "Desenvolver uma técnica de estocagem para aproveitar picos sazonais",
            "custo": {"mel": -10, "operarias": 0, "relacao": -1},
        },
        {
            "conselheira": "Aurora",
            "acao":
                "Compartilhar a descoberta com colmeias vizinhas",
            "custo": {"mel": -5, "operarias": 0, "relacao": 3},
        },
    ],
}
