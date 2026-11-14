# -*- coding: utf-8 -*-
"""Evento 12 — A Grande Nevasca (Inverno).

A SITUAÇÃO: o texto de abertura e as opções, com o preço de cada uma.
  custo   {mel, operarias, relacao}: negativo paga, positivo ganha ("tudo" = todo o mel)

O jogo de cada conselheira está em minigames/e12_a_grande_nevasca.py; os efeitos, em
resultados/e12_a_grande_nevasca.py.
"""

EVENTO = {
    "id": 12,
    "estacao": "Inverno",
    "titulo": "A Grande Nevasca",
    "contexto":
        "O evento culminante do ano: uma nevasca severa ameaça tudo o que foi "
        "construído. A resposta da colônia reflete diretamente o equilíbrio (ou "
        "desequilíbrio) acumulado no painel de Harmonia e na Relação com a Colmeia.",
    "opcoes": [
        {
            "conselheira": "Melina",
            "acao":
                "Fechar a colmeia e sobreviver apenas com o que foi guardado",
            "custo": {"mel": -22, "operarias": 0, "relacao": 0},
        },
        {
            "conselheira": "Flora",
            "acao":
                "Confiar nos corredores ecológicos criados ao longo do ano para abrigo"
                " extra",
            "custo": {"mel": 0, "operarias": 0, "relacao": 0},
        },
        {
            "conselheira": "Nectar",
            "acao":
                "Ativar as inovações desenvolvidas ao longo do ano",
            "custo": {"mel": 0, "operarias": 0, "relacao": 0},
        },
        {
            "conselheira": "Aurora",
            "acao":
                "Pedir abrigo às colônias aliadas formadas durante o ano",
            "custo": {"mel": 0, "operarias": 0, "relacao": 0},
        },
    ],
}
