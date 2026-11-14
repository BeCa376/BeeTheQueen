# -*- coding: utf-8 -*-
"""Resultado do Evento 12 — A Grande Nevasca.

O que ACONTECE depois da escolha e do minigame:
  consequencia  o texto da tela de consequência
  efeitos       por conselheira: o que muda na Harmonia ("harmonia"), a afinidade
                ("propria" = dela, "demais" = das outras) e um "extra" opcional
  proximo       o que este resultado muda no PRÓXIMO evento (texto, desconto, frase)

Os efeitos valem por inteiro num sucesso; no parcial e na falha são reduzidos
(multiplicador do minigame, em minigames/jogos/base.py).
O preço de cada opção está em eventos/e12_a_grande_nevasca.py.
"""

RESULTADO = {
    "consequencia":
        "Este é o evento-espelho do ano: cada opção só funciona bem se o jogador "
        "investiu naquele eixo ao longo das estações anteriores. É aqui que a "
        "'Harmonia da Colmeia' e a 'Relação com a Colmeia' deixam de ser números e "
        "viram sobrevivência real -- reforçando a mensagem central de que não existe "
        "atalho para o equilíbrio.",
    "efeitos": {
        "Melina": {
            "espelho": "reserva_mel",
            "afinidade": {"propria": 2, "demais": -1},
        },
        "Flora": {
            "espelho": "biodiversidade",
            "afinidade": {"propria": 2, "demais": -1},
        },
        "Nectar": {
            "espelho": "inovacao",
            "afinidade": {"propria": 2, "demais": -1},
        },
        "Aurora": {
            "espelho": "relacao",
            "afinidade": {"propria": 2, "demais": -1},
        },
    },
    "proximo": None,   # último evento: não há próximo
}
