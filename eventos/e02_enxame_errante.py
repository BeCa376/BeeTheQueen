# -*- coding: utf-8 -*-
"""Evento 2 — Enxame Errante (Primavera).

A SITUAÇÃO: o texto de abertura e as opções, com o preço de cada uma.
  custo   {mel, operarias, relacao}: negativo paga, positivo ganha ("tudo" = todo o mel)

O jogo de cada conselheira está em minigames/e02_enxame_errante.py; os efeitos, em
resultados/e02_enxame_errante.py.
"""

EVENTO = {
    "id": 2,
    "estacao": "Primavera",
    "titulo": "Enxame Errante",
    "contexto":
        "Um enxame de abelhas selvagens sem colmeia pede abrigo. Aceitá-las muda a "
        "composição genética e social da colônia.",
    "opcoes": [
        {
            "conselheira": "Flora",
            "acao":
                "Acolher e integrar respeitando a diversidade genética do enxame",
            "custo": {"mel": -13, "operarias": 0, "relacao": 3},
        },
        {
            "conselheira": "Melina",
            "acao":
                "Recrutá-las como força de trabalho extra imediatamente",
            "custo": {"mel": -8, "operarias": 25, "relacao": -3},
        },
        {
            "conselheira": "Nectar",
            "acao":
                "Usar o encontro para testar uma nova técnica de comunicação entre "
                "colmeias",
            "custo": {"mel": -8, "operarias": 0, "relacao": 0},
        },
        {
            "conselheira": "Aurora",
            "acao":
                "Formar uma colmeia satélite aliada, sem anexação total",
            "custo": {"mel": -5, "operarias": 0, "relacao": 4},
        },
    ],
}
