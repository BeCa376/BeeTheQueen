# -*- coding: utf-8 -*-
"""Evento 6 — Incêndio nas Redondezas (Verao).

A SITUAÇÃO: o texto de abertura e as opções, com o preço de cada uma.
  custo   {mel, operarias, relacao}: negativo paga, positivo ganha ("tudo" = todo o mel)

O jogo de cada conselheira está em minigames/e06_incendio_nas_redondezas.py; os efeitos, em
resultados/e06_incendio_nas_redondezas.py.
"""

EVENTO = {
    "id": 6,
    "estacao": "Verao",
    "titulo": "Incêndio nas Redondezas",
    "contexto":
        "Fumaça no horizonte!! um incêndio se aproxima da colmeia. É preciso decidir "
        "agora.",
    "opcoes": [
        {
            "conselheira": "Melina",
            "acao":
                "Apagar o fogo agora com o que houver disponível",
            "custo": {"mel": -5, "operarias": -35, "relacao": -6},
        },
        {
            "conselheira": "Aurora",
            "acao":
                "Salvar as operárias do local, abandonando parte do território",
            "custo": {"mel": -15, "operarias": -5, "relacao": 3},
        },
        {
            "conselheira": "Nectar",
            "acao":
                "Investir em colmeias à prova de fogo para o futuro",
            "custo": {"mel": -11, "operarias": -8, "relacao": -2},
        },
        {
            "conselheira": "Flora",
            "acao":
                "Restaurar a área queimada depois, criando uma barreira verde natural",
            "custo": {"mel": -11, "operarias": 0, "relacao": 2},
        },
    ],
}
