# -*- coding: utf-8 -*-
"""Evento 4 — A Seca Chega (Verao).

A SITUAÇÃO: o texto de abertura e as opções, com o preço de cada uma.
  custo   {mel, operarias, relacao}: negativo paga, positivo ganha ("tudo" = todo o mel)

O jogo de cada conselheira está em minigames/e04_a_seca_chega.py; os efeitos, em
resultados/e04_a_seca_chega.py.
"""

EVENTO = {
    "id": 4,
    "estacao": "Verao",
    "titulo": "A Seca Chega",
    "contexto":
        "Semanas sem chuva deixam flores murchando e reservas de água escassas.",
    "opcoes": [
        {
            "conselheira": "Flora",
            "acao":
                "Priorizar o resgate das flores nativas mais ameaçadas",
            "custo": {"mel": -12, "operarias": 0, "relacao": 2},
        },
        {
            "conselheira": "Melina",
            "acao":
                "Racionar as reservas de mel para garantir a sobrevivência da produção",
            "custo": {"mel": -20, "operarias": 0, "relacao": -5},
        },
        {
            "conselheira": "Nectar",
            "acao":
                "Pesquisar uma rota alternativa até fontes de água distantes",
            "custo": {"mel": -11, "operarias": 0, "relacao": -2},
        },
        {
            "conselheira": "Aurora",
            "acao":
                "Pedir ajuda e água a colmeias vizinhas",
            "custo": {"mel": -8, "operarias": 0, "relacao": 4},
        },
    ],
}
