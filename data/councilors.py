# -*- coding: utf-8 -*-
"""As 4 conselheiras: cor, emoji, eixo da Harmonia e a penalidade de falha de cada uma.
(Os textos de apresentação ficam em introducao/conselheiras.py.)

O campo 'emoji' continua aqui só como referência/texto alternativo (por
exemplo para logs ou um eventual modo texto). Para DESENHAR o emoji na
tela, o jogo usa o campo 'arquivo_emoji', que aponta para um PNG em
assets/emoji/ -- o pygame não consegue renderizar emoji colorido a partir
de fonte de texto, então usamos imagens prontas (Twemoji, licença CC-BY 4.0).
Se quiser trocar o emoji de uma conselheira, troque o PNG em assets/emoji/
com o mesmo nome de arquivo (ou aponte 'arquivo_emoji' para um novo arquivo).
"""

CONSELHEIRAS = {
    "Flora": {
        "emoji": "🌼",
        "arquivo_emoji": "flora.png",
        "eixo": "biodiversidade",
        "cor": (110, 179, 92),
    },
    "Melina": {
        "emoji": "🍯",
        "arquivo_emoji": "melina.png",
        "eixo": "producao",
        "cor": (214, 158, 46),
    },
    "Nectar": {
        "emoji": "🚀",
        "arquivo_emoji": "nectar.png",
        "eixo": "inovacao",
        "cor": (86, 130, 214),
    },
    "Aurora": {
        "emoji": "🤝",
        "arquivo_emoji": "aurora.png",
        "eixo": "cooperacao",
        "cor": (196, 108, 196),
    },
}

# a ordem em que elas se apresentam na introdução
ORDEM = ["Flora", "Melina", "Nectar", "Aurora"]
