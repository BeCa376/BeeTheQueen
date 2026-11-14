# -*- coding: utf-8 -*-
"""Evento 5 — A Fazenda com Pesticidas (Verao).

A SITUAÇÃO: o texto de abertura e as opções, com o preço de cada uma.
  custo   {mel, operarias, relacao}: negativo paga, positivo ganha ("tudo" = todo o mel)

O jogo de cada conselheira está em minigames/e05_a_fazenda_com_pesticidas.py; os efeitos, em
resultados/e05_a_fazenda_com_pesticidas.py.
"""

EVENTO = {
    "id": 5,
    "estacao": "Verao",
    "titulo": "A Fazenda com Pesticidas",
    "contexto":
        "Uma fazenda vizinha começou a usar pesticidas. O Conselho se reúne com "
        "urgência! Cada conselheira vê o problema de um ângulo diferente.",
    "opcoes": [
        {
            "conselheira": "Flora",
            "acao":
                "Restaurar habitats alternativos, afastando a colônia da área "
                "contaminada",
            "custo": {"mel": -15, "operarias": 0, "relacao": 2},
        },
        {
            "conselheira": "Melina",
            "acao":
                "Aproveitar o campo intensamente antes da próxima pulverização",
            "custo": {"mel": 6, "operarias": -6, "relacao": -4},
        },
        {
            "conselheira": "Nectar",
            "acao":
                "Desenvolver novas rotas de forrageamento que evitem a área tratada",
            "custo": {"mel": -10, "operarias": 0, "relacao": -1},
        },
        {
            "conselheira": "Aurora",
            "acao":
                "Negociar diretamente com os agricultores por uma faixa livre de "
                "pesticidas",
            "custo": {"mel": -12, "operarias": 0, "relacao": 5},
        },
    ],
}
