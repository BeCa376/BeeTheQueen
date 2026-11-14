# -*- coding: utf-8 -*-
"""Evento 10 — O Frio Chega (Inverno).

A SITUAÇÃO: o texto de abertura e as opções, com o preço de cada uma.
  custo   {mel, operarias, relacao}: negativo paga, positivo ganha ("tudo" = todo o mel)

O jogo de cada conselheira está em minigames/e10_o_frio_chega.py; os efeitos, em
resultados/e10_o_frio_chega.py.
"""

EVENTO = {
    "id": 10,
    "estacao": "Inverno",
    "titulo": "O Frio Chega",
    "contexto":
        "As primeiras geadas testam tudo o que foi construído no Outono. As reservas "
        "acumuladas, ou a falta delas, decidem o tom do inverno.",
    "opcoes": [
        {
            "conselheira": "Melina",
            "acao":
                "Consumir as reservas de forma controlada, priorizando a produção "
                "mínima",
            "custo": {"mel": -24, "operarias": 0, "relacao": -4},
        },
        {
            "conselheira": "Flora",
            "acao":
                "Manter parte da colônia ativa cuidando de plantas resistentes ao frio",
            "custo": {"mel": -7, "operarias": 0, "relacao": 2},
        },
        {
            "conselheira": "Nectar",
            "acao":
                "Testar um método de aquecimento coletivo mais eficiente",
            "custo": {"mel": -9, "operarias": 0, "relacao": -1},
        },
        {
            "conselheira": "Aurora",
            "acao":
                "Formar um círculo de aquecimento com todas as operárias disponíveis",
            "custo": {"mel": -5, "operarias": 0, "relacao": 4},
        },
    ],
}
