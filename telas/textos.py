# -*- coding: utf-8 -*-
"""
OS TEXTOS FIXOS DAS TELAS: tudo que está escrito nas telas e não vem dos
eventos. (O texto de cada evento está em eventos/ e resultados/; o da abertura,
das conselheiras e da Nova Rainha, em introducao/; o dos perfis finais, em
data/profiles.py.)

O que vem entre chaves, como {titulo}, é preenchido pelo jogo: não apague a
palavra entre chaves, só mude o texto em volta dela. Para quebrar linha,
use \\n.
"""

# ------------------------------------------------------ as conselheiras
DICA_CONSELHEIRA = ""   # era: "Pressione ENTER para a próxima conselheira"

# ---------------------------------------------------------- Nova Rainha
DICA_NOVA_RAINHA = ""   # era: "Pressione ENTER para começar o reinado"

# ------------------------------------------------------------- estação
DICA_ESTACAO = ""   # era: "Pressione ENTER para continuar"
# como cada estação aparece escrita (a chave é o nome usado nos arquivos dos eventos)
NOMES_DAS_ESTACOES = {"Verao": "Verão"}

# --------------------------------------------------- texto e escolha
CABECALHO_DO_EVENTO = "{estacao} - Evento {id}: {titulo}"
DICA_CONTEXTO = ""   # era: "Pressione ENTER para reunir o Conselho"
CABECALHO_DA_ESCOLHA = "O Conselho se reúne: {titulo}"
# as moedas na linha de preço de cada card
CARD_CUSTO_MEL = "Mel {valor}"
CARD_CUSTO_MEL_TUDO = "Mel: tudo"
CARD_CUSTO_OPERARIAS = "Operárias {valor:+d}"
CARD_CUSTO_RELACAO = "Relação {valor:+d}"
CARD_SEM_CUSTO = "Sem custo direto"

# ------------------------------------------------------------ minigame
PREPARO_TITULO = "Preparando: {nome}"
PROPOSTA = "{conselheira} propôs: {acao}"
DICA_PREPARO = ""   # era: "Pressione ENTER para começar agora"
MINIGAME_TITULO = "Execução: {nome}"
MINIGAME_SEM_JOGO = "Ação direta"
DICA_MINIGAME = ""   # era: "Pressione ENTER para ver o resultado"

# o resultado do minigame ("sucesso", "parcial" ou "falha" -- como o jogo termina)
RESULTADO_TITULO = {
    "sucesso": "Execução bem-sucedida!",
    "parcial": "Execução parcial.",
    "falha": "A execução falhou.",
}
# a mensagem padrão de cada resultado (a mesma em todos os eventos e para todas as escolhas)
RESULTADO_DETALHE = {
    "sucesso": "A colmeia executou o plano com perfeição: tudo deu certo!",
    "parcial": "O plano deu certo só em parte: nem tudo saiu como o esperado.",
    "falha": "O plano não saiu como a colmeia esperava: desta vez deu errado.",
}
RESULTADO_EFEITOS = "Efeitos nesta rodada: {linhas}"
RESULTADO_SEM_EFEITOS = "(efeito condicional)"
RESULTADO_CUSTO = "Custo desta escolha: {linhas}"
RESULTADO_RENDA = "Produção da estação: {linhas}"
RESULTADO_PENALIDADE ="Penalidade extra de {conselheira}: {texto}"
DICA_RESULTADO_DO_MINIGAME = ""   # era: "Pressione ENTER para ver a consequência"

# a mesma moeda escrita nas listas de efeito/custo
NOMES_DAS_MOEDAS = {"mel": "Mel", "operarias": "Operárias", "relacao": "Relação"}

# -------------------------------------------------------- consequência
CONSEQUENCIA_TITULO = "Consequência: {titulo}"
CONSEQUENCIA_EFEITOS = "Efeitos: {linhas}"
AVISO_DE_DESEQUILIBRIO = (
    "O painel de Harmonia está muito desequilibrado -- em sprints futuros "
    "isso desencadeia eventos de correção automática (ex.: pragas por "
    "excesso de Produção sem Biodiversidade).")
DICA_CONSEQUENCIA = ""   # era: "Pressione ENTER para continuar"

# ---------------------------------------------------------------- HUD
HUD_MEL = "Mel: {valor}"
HUD_OPERARIAS = "Operárias: {valor}"
HUD_RELACAO = "Relação com a Colmeia: {valor}"
HUD_AVISO_DE_PRODUCAO = "Relação baixa: produção com penalidade!"
HUD_AFINIDADE = "Afinidade das Conselheiras"
HUD_RECURSOS = "Recursos da Colmeia"

# --------------------------------------------------------- tela final
FINAL_TITULO = "O Legado da Colmeia"
FINAL_RECURSOS = "Recursos finais"
FINAL_RELACAO = "Relação com a colmeia"
FINAL_AFINIDADE = "Afinidade final"
FINAL_LINHA_DE_AFINIDADE = "{nome}: {valor} ({situacao})"
FINAL_SITUACAO = {"aliada": "aliada próxima", "afastada": "afastada", "neutra": "neutra"}
FINAL_PERFIL = "Perfil: {nome}"
FINAL_JOGAR_DE_NOVO = "Jogar de novo"
