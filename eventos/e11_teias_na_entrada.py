# -*- coding: utf-8 -*-
"""Evento 11 — Teias na Entrada (Inverno).

A SITUAÇÃO: o texto de abertura e as opções, com o preço de cada uma.
  custo   {mel, operarias, relacao}: negativo paga, positivo ganha ("tudo" = todo o mel)

O jogo de cada conselheira está em minigames/e11_teias_na_entrada.py; os efeitos, em
resultados/e11_teias_na_entrada.py.
"""

EVENTO = {
    "id": 11,
    "estacao": "Inverno",
    "titulo": "Teias na Entrada",
    "contexto":
        "Uma aranha construiu teias perto da entrada da colmeia. Operárias "
        "forrageadoras estão presas.",
    "opcoes": [
        {
            "conselheira": "Aurora",
            "acao":
                "Organizar um resgate coletivo, evitando as teias",
            "custo": {"mel": -10, "operarias": 0, "relacao": 4},
        },
        {
            "conselheira": "Melina",
            "acao":
                "Sacrificar as presas e seguir em frente para não perder mais recursos",
            "custo": {"mel": 0, "operarias": -10, "relacao": -5},
        },
        {
            "conselheira": "Nectar",
            "acao":
                "Testar uma rota alternativa de entrada que evite a área da teia",
            "custo": {"mel": -8, "operarias": 0, "relacao": -1},
        },
        {
            "conselheira": "Flora",
            "acao":
                "Deixar a aranha em paz e replantar arbustos que naturalmente a "
                "afastem",
            "custo": {"mel": -7, "operarias": 0, "relacao": 2},
        },
    ],
}
