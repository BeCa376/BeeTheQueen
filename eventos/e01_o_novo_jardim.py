# -*- coding: utf-8 -*-
"""Evento 1 — O Novo Jardim (Primavera).

A SITUAÇÃO: o texto de abertura e as opções, com o preço de cada uma.
  custo   {mel, operarias, relacao}: negativo paga, positivo ganha ("tudo" = todo o mel)

O jogo de cada conselheira está em minigames/e01_o_novo_jardim.py; os efeitos, em
resultados/e01_o_novo_jardim.py.
"""

EVENTO = {
    "id": 1,
    "estacao": "Primavera",
    "titulo": "O Novo Jardim",
    "contexto":
        "Exploradoras encontram um jardim particular ainda não polinizado por ninguém,"
        " mas outros insetos também o notaram.",
    "opcoes": [
        {
            "conselheira": "Flora",
            "acao":
                "Mapear com cuidado, respeitando as espécies nativas antes de "
                "polinizar",
            "custo": {"mel": -11, "operarias": 0, "relacao": 3},
        },
        {
            "conselheira": "Melina",
            "acao":
                "Polinizar tudo!! Antes que outra espécie tome o jardim",
            "custo": {"mel": -5, "operarias": -12, "relacao": -4},
        },
        {
            "conselheira": "Nectar",
            "acao":
                "Testar uma rota de voo experimental mais eficiente",
            "custo": {"mel": -10, "operarias": 0, "relacao": 0},
        },
        {
            "conselheira": "Aurora",
            "acao":
                "Negociar com o jardineiro humano um plantio em conjunto",
            "custo": {"mel": -5, "operarias": 0, "relacao": 5},
        },
    ],
}
