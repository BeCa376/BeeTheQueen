# -*- coding: utf-8 -*-
"""
CONFIG: todos os números e ajustes do jogo, num lugar só.

  1) JANELA E TEMPO       tamanho da janela, velocidade
  2) EQUILÍBRIO           os números que balanceiam o jogo
  3) RITMO DAS TELAS      quanto cada tela dura, quando a dica do ENTER aparece
  4) FONTES               família e tamanho das letras
  5) NOMES DAS TELAS e VOCABULÁRIO   (estes não se mexe)

O PREÇO de cada opção fica em eventos/; o desconto de um evento pro outro,
em resultados/; a penalidade de cada conselheira, em data/councilors.py.
"""

# ============================================================
# 1) JANELA E TEMPO
# ============================================================
TITULO_DA_JANELA = "Bee the Queen"
LARGURA, ALTURA = 1000, 650
FPS = 60

# ============================================================
# 2) EQUILÍBRIO
# ============================================================
# --- como o jogo começa ---
MEL_INICIAL = 100
OPERARIAS_INICIAIS = 100
RELACAO_INICIAL = 60            # moral/confiança da colmeia
HARMONIA_INICIAL = 50           # cada um dos 5 eixos
AFINIDADE_INICIAL = 40          # de cada conselheira
ESCALA_MAXIMA = 100             # Relação, Harmonia e Afinidade vão de 0 a isto

# --- a colmeia nunca zera ---
# Produção da estação: depois de cada evento a colmeia trabalha -- fabrica mel,
# nascem operárias e a confiança se recupera um pouco. É o que sustenta o ano.
RENDA_POR_ESTACAO = {"mel": 12, "operarias": 4, "relacao": 2}
# Rede de segurança: nenhuma PERDA (custo, penalidade) leva Mel, Operárias ou
# Relação abaixo disto. Com os números atuais, o pior caminho possível termina
# acima deste piso (confira com testes/jogar_tudo.py).
PISO_DAS_MOEDAS = 5

# --- o que a Relação com a colmeia faz ---
RELACAO_BAIXA = 25              # abaixo disso a colmeia está desmotivada:
PRODUCAO_COM_RELACAO_BAIXA = 0.85    # ...só 85% de todo ganho de Produção
RELACAO_ALTA = 80               # acima disso, escolhas bem-sucedidas rendem mais:
BONUS_RELACAO_ALTA = 1.1        # ...10% a mais no efeito

# --- avisos e perfil final ---
DESEQUILIBRIO_HARMONIA = 45     # diferença entre o maior e o menor eixo que dispara o aviso
MARGEM_PERFIL_EQUILIBRADO = 15  # afinidades mais próximas que isso -> perfil "Equilibrado"

# --- na tela final: afinidade igual ou acima disto = "aliada próxima"; igual ou abaixo = "afastada" ---
AFINIDADE_ALIADA = 70
AFINIDADE_AFASTADA = 20

# --- como o resultado do minigame vira "super_sucesso / sucesso / falha" ---
# (o multiplicador do minigame é 1.0, 0.5 ou 0.25; o +10% da Relação alta
#  também cai em "super_sucesso")
LIMITE_SUPER_SUCESSO = 0.9
LIMITE_SUCESSO = 0.4
FATOR_DO_CUSTO = {"sucesso": 0.75, "parcial": 1.0, "falha": 1.25}
FATOR_DO_GANHO = {"sucesso": 1.25, "parcial": 1.0, "falha": 0.75}

# --- rodízio dos minigames (minigames/rodizio.py) ---
# True = depois de cada decisão vem UM minigame, sempre na ordem 1, 2, 3, 4; terminados
# os 4, recomeça do 1 com a dificuldade da volta seguinte (qualquer que seja a conselheira).
# False = cada conselheira joga o seu jogo (minigames/eNN_*.py), com a dificuldade da estação.
MINIGAMES_EM_RODIZIO = True
# dificuldade (1 a 5) de cada volta pelos 4 jogos: 1ª volta, 2ª volta, 3ª volta...
# (se houver mais voltas que números aqui, as que sobram usam o último)
DIFICULDADE_POR_VOLTA = (1, 2, 3)

# --- dificuldade do minigame por estação (1 a 5); só vale com MINIGAMES_EM_RODIZIO = False ---
# (um evento pode forçar a sua em minigames/eNN_*.py, com DIFICULDADE = n)
DIFICULDADE_POR_ESTACAO = {"Primavera": 1, "Verao": 2, "Outono": 3, "Inverno": 4}

# --- evento-espelho (o último): o efeito depende do que foi acumulado ---
ESPELHO_MEL_MINIMO = 40                  # Melina: mel guardado >= isso
ESPELHO_RELACAO_MINIMA = 60              # Aurora: Relação >= isso
ESPELHO_EFEITO_RESERVA_OU_RELACAO = 20   # +20 (ou -20) de População
ESPELHO_EIXO_ALTO = 60                   # Flora/Nectar: eixo >= isso
ESPELHO_EIXO_BAIXO = 40                  # eixo < isso
ESPELHO_EFEITO_EIXO = 15                 # +15 se alto, -15 se baixo
ESPELHO_EFEITO_EIXO_NEUTRO = 3           # no meio

# ============================================================
# 3) RITMO DAS TELAS
# ============================================================
TEMPO_DE_PREPARO_DO_MINIGAME = 5.0   # segundos de contagem antes de cada minigame

# {tela: segundos}. Passado esse tempo, a tela avança sozinha, como numa
# animação; apertar ENTER avança na hora. Tela que NÃO está aqui só avança
# com ENTER. (os nomes das telas estão na seção 5)
AVANCO_AUTOMATICO = { "estacao": 1.5}

ATRASO_DA_DICA = 0
# O mesmo, nas telas do jogo (texto do evento, preparo, resultado, consequência).
# Nelas a tela nunca passa sozinha.
ATRASO_DA_DICA_NO_JOGO = 0

# True = o preparo conta TEMPO_DE_PREPARO_DO_MINIGAME e o jogo começa sozinho;
# False = o minigame só começa no ENTER.
COMECAR_O_MINIGAME_SOZINHO = False

# Barrinha no pé da tela mostrando quanto falta pra tela passar sozinha.
MOSTRAR_BARRA_DE_TEMPO = False

# ============================================================
# 4) FONTES  --  "nome": (família, tamanho, negrito)
# ============================================================
FONTES = {
    "titulo":        ("georgia", 30, True),    # títulos grandes
    "subtitulo":     ("georgia", 22, True),    # subtítulos
    "corpo":         ("verdana", 16, False),   # texto corrido
    "corpo_negrito": ("verdana", 16, True),    # texto corrido em negrito
    "pequena":       ("verdana", 13, False),   # textos pequenos e dicas
    "botao":         ("verdana", 15, True),    # nome nos cards
}
CENTRALIZAR_TEXTO_DOS_CARDS = True
ABELHA_SEGUNDOS_POR_QUADRO = 0.15   # velocidade do bater de asas
EMOJI_TAMANHO = 48                  # emoji de cada conselheira

# ============================================================
# 5) NOMES DAS TELAS e VOCABULÁRIO  (não mexa)
# ============================================================
ABERTURA = "abertura"
CONSELHEIRA = "conselheira"
NOVA_RAINHA = "nova_rainha"
ESTACAO = "estacao"
CONTEXTO = "contexto"
ESCOLHA = "escolha"
PREPARO = "preparo"
MINIGAME = "minigame"
RESULTADO_DO_MINIGAME = "resultado_do_minigame"
CONSEQUENCIA = "consequencia"
FINAL = "final"

# telas que o ENTER (e o relógio) sabem avançar
TELAS_QUE_AVANCAM = (ABERTURA, CONSELHEIRA, NOVA_RAINHA, ESTACAO, CONTEXTO)

TELAS_COM_SETAS = (ABERTURA, CONSELHEIRA, NOVA_RAINHA)

TELAS_COM_SETA_DO_MENU = (CONTEXTO, ESCOLHA, PREPARO, MINIGAME, RESULTADO_DO_MINIGAME, CONSEQUENCIA)

SEGUNDOS_DO_CLIQUE_DA_SETA = 0.15

TELAS_COM_SETA_NO_CARD = (CONTEXTO, PREPARO, RESULTADO_DO_MINIGAME, CONSEQUENCIA)

SEGUNDOS_ATE_O_RESULTADO = 0.8

NOMES_DE_RESULTADO = ("super_sucesso", "sucesso", "falha")

MOEDAS = ("mel", "operarias", "relacao")


def verificar():
    """Confere os ajustes acima ao abrir o jogo (erro de digitação para tudo,
    com uma mensagem dizendo o que está errado)."""
    for tela, segundos in AVANCO_AUTOMATICO.items():
        if tela not in TELAS_QUE_AVANCAM:
            raise ValueError(f"config.py: AVANCO_AUTOMATICO: a tela {tela!r} não pode passar "
                             f"sozinha. As válidas são: {', '.join(TELAS_QUE_AVANCAM)}.")
        if not isinstance(segundos, (int, float)) or segundos <= 0:
            raise ValueError(f"config.py: AVANCO_AUTOMATICO: o tempo de {tela!r} precisa ser um "
                             f"número maior que zero (veio {segundos!r}).")
    if not isinstance(ATRASO_DA_DICA, (int, float)) or ATRASO_DA_DICA < 0:
        raise ValueError(f"config.py: ATRASO_DA_DICA precisa ser um número (0 ou mais), "
                         f"veio {ATRASO_DA_DICA!r}.")
    if not DIFICULDADE_POR_VOLTA:
        raise ValueError("config.py: DIFICULDADE_POR_VOLTA precisa ter pelo menos um número.")
    for volta, dificuldade in enumerate(DIFICULDADE_POR_VOLTA, start=1):
        if dificuldade not in (1, 2, 3, 4, 5):
            raise ValueError(f"config.py: DIFICULDADE_POR_VOLTA: a da {volta}ª volta precisa "
                             f"ser de 1 a 5 (veio {dificuldade!r}).")
    for estacao, dificuldade in DIFICULDADE_POR_ESTACAO.items():
        if dificuldade not in (1, 2, 3, 4, 5):
            raise ValueError(f"config.py: DIFICULDADE_POR_ESTACAO: a de {estacao!r} precisa "
                             f"ser de 1 a 5 (veio {dificuldade!r}).")
