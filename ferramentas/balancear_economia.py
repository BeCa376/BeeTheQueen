# -*- coding: utf-8 -*-
"""
BALANCEAR A ECONOMIA: nenhuma moeda pode chegar a -1, nem no pior caso.

A REGRA: jogando os 12 eventos SEMPRE com a mesma conselheira (a Flora nos 12, a Melina nos 12, a Nectar
nos 12 e a Aurora nos 12) e com FALHA em todos os jogos, nenhuma das três moedas (MEL, OPERÁRIAS e
RELAÇÃO COM A COLMEIA) pode ficar abaixo de MINIMO_PERMITIDO (0 = nunca chega a -1). A produção da estação
(config.RENDA_POR_ESTACAO, depois dos eventos 3, 6, 9 e 12) entra na conta, como no jogo.

Se alguma conselheira derruba uma moeda abaixo disso, o script diminui os custos DAQUELA moeda NAQUELA
conselheira, todos na mesma proporção (a diferença entre os eventos se mantém), o mínimo possível. Ganhos
não são mexidos. Quem não viola a regra não é tocado.

Rode na pasta do projeto (a do main.py), com o (venv) ativo:

    python ferramentas/balancear_economia.py             só MOSTRA a conta e o que mudaria (não grava nada)
    python ferramentas/balancear_economia.py --aplicar   grava nos arquivos eventos/eNN_*.py (cópia: .antes_do_balanco)

Os números (fatores da falha, produção, valores iniciais) são os do seu jogo (config.py e regras.Estado).
"""
import glob
import math
import os
import re
import shutil
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
PASTA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))     # a pasta do PROJETO (a de cima desta)
sys.path.insert(0, PASTA)

import catalogo  # noqa: E402
import config  # noqa: E402
import regras  # noqa: E402
from data.councilors import ORDEM  # noqa: E402

# ============================================================
# AJUSTES
# ============================================================
MINIMO_PERMITIDO = 5        # a menor quantidade que uma moeda pode ter (0 = nunca chega a -1).
#                             Para o piso das moedas nunca precisar agir, use config.PISO_DAS_MOEDAS (5).
MOEDAS = ("mel", "operarias", "relacao")
NOMES = {"mel": "mel", "operarias": "operárias", "relacao": "relação"}
EVENTOS_POR_ESTACAO = 3


def custo_da_falha(valor):
    """O que a falha aplica a um valor do card: custo (negativo) x fator, pra menos desconto; ganho x fator, pra baixo."""
    if valor < 0:
        return -math.floor(abs(valor) * config.FATOR_DO_CUSTO["falha"] + 1e-9)
    return math.floor(valor * config.FATOR_DO_GANHO["falha"] + 1e-9)


def opcao_de(evento, conselheira):
    return next(o for o in evento["opcoes"] if o["conselheira"] == conselheira)


def inicial(moeda):
    return getattr(regras.Estado(), moeda)


def trajetoria(moeda, conselheira, custos=None):
    """Joga os 12 eventos com `conselheira`, tudo FALHA. Devolve (menor valor depois de um custo, valor final).
    `custos` ({(evento, conselheira, moeda): valor}) troca os custos de hoje pelos novos."""
    custos = custos or {}
    valor = inicial(moeda)
    menor = valor
    producao = config.RENDA_POR_ESTACAO.get(moeda, 0)
    for i, evento in enumerate(catalogo.EVENTOS):
        card = custos.get((evento["id"], conselheira, moeda), opcao_de(evento, conselheira)["custo"][moeda])
        if card == "tudo":
            valor = 0                                            # o custo "tudo" (evento 12): zera o mel
        else:
            valor += custo_da_falha(card)
        valor = min(valor, config.ESCALA_MAXIMA)                 # o máximo de cada moeda (100)
        menor = min(menor, valor)                                # o ponto mais baixo: depois do custo, ANTES da produção
        if (i + 1) % EVENTOS_POR_ESTACAO == 0:
            valor = min(valor + producao, config.ESCALA_MAXIMA)
    return menor, valor


def reduzir(moeda, conselheira):
    """Os novos custos de `conselheira` nessa moeda: o menor corte (mesma proporção) que respeita o mínimo.
    Devolve ({(evento, conselheira, moeda): novo}, fator) ou (None, None) se nenhum corte resolve."""
    originais = {}
    for evento in catalogo.EVENTOS:
        card = opcao_de(evento, conselheira)["custo"][moeda]
        if isinstance(card, (int, float)) and card < 0:
            originais[(evento["id"], conselheira, moeda)] = card
    for passo in range(99, 0, -1):
        fator = passo / 100
        novos = {k: -max(1, math.floor(-v * fator + 0.5)) for k, v in originais.items()}
        if trajetoria(moeda, conselheira, novos)[0] >= MINIMO_PERMITIDO:
            return {k: v for k, v in novos.items() if v != originais[k]}, fator
    return None, None


def calcular():
    """Confere as 12 trajetórias (4 conselheiras x 3 moedas) e calcula as correções. Devolve (linhas, correções, sem_saída)."""
    linhas, correcoes, sem_saida = [], {}, []
    for moeda in MOEDAS:
        for conselheira in ORDEM:
            menor, final = trajetoria(moeda, conselheira)
            ok = menor >= MINIMO_PERMITIDO
            linhas.append((moeda, conselheira, menor, final, ok))
            if not ok:
                novos, fator = reduzir(moeda, conselheira)
                if novos is None:
                    sem_saida.append((moeda, conselheira))
                else:
                    correcoes.update(novos)
    return linhas, correcoes, sem_saida


def avisar_se_tem_ponte():
    """A conta daqui NÃO considera a "ponte" (um custo que muda conforme o resultado do evento anterior)."""
    ativas = [e["id"] for e in catalogo.EVENTOS
              if (catalogo.RESULTADOS[e["id"]].get("proximo") or {}).get("fator_custo")]
    if ativas:
        print(f"ATENÇÃO: o resultado do(s) evento(s) {ativas} tem uma PONTE que muda o custo do evento seguinte "
              f"(\"fator_custo\").\n         Esta conta NÃO considera a ponte, então os números do jogo podem ser "
              f"diferentes. Apague \"fator_custo\", \"moedas_afetadas\"\n         e \"notas\" desse resultado "
              f"(em resultados/eNN_*.py) para a ponte não mexer nos custos.\n")


def mostrar(linhas, correcoes, sem_saida):
    avisar_se_tem_ponte()
    print(f"Regra: com FALHA em todos os jogos e sempre a mesma conselheira, nenhuma moeda fica abaixo de "
          f"{MINIMO_PERMITIDO}.")
    print(f"Começa em: mel {inicial('mel')}, operárias {inicial('operarias')}, relação {inicial('relacao')} | "
          f"produção por estação: {dict(config.RENDA_POR_ESTACAO)} | falha: custo x{config.FATOR_DO_CUSTO['falha']}, "
          f"ganho x{config.FATOR_DO_GANHO['falha']}\n")
    print("COMO ESTÁ HOJE (o MENOR valor que a moeda chega a ter, e como termina o jogo):")
    for moeda in MOEDAS:
        print(f"   {NOMES[moeda]}")
        for m, conselheira, menor, final, ok in linhas:
            if m == moeda:
                marca = "ok " if ok else "VIOLA"
                print(f"      {conselheira:7s} {marca:5s} menor: {menor:5d}   termina em: {final:4d}")
    if not correcoes and not sem_saida:
        print("\nTudo certo: nenhuma conselheira derruba nenhuma moeda abaixo do mínimo. Nada a mudar.")
        return
    if correcoes:
        print("\nO QUE MUDA (custo de hoje -> custo novo), por conselheira e moeda:")
        agrupado = {}
        for (evento_id, conselheira, moeda), novo in sorted(correcoes.items()):
            antigo = opcao_de(next(e for e in catalogo.EVENTOS if e["id"] == evento_id), conselheira)["custo"][moeda]
            agrupado.setdefault((moeda, conselheira), []).append(f"ev{evento_id}: {antigo}->{novo}")
        for (moeda, conselheira), itens in agrupado.items():
            print(f"   {NOMES[moeda]:9s} {conselheira:7s} " + "  ".join(itens))
        print("\nDEPOIS DA MUDANÇA:")
        for moeda in MOEDAS:
            for conselheira in ORDEM:
                if any(k[1] == conselheira and k[2] == moeda for k in correcoes):
                    menor, final = trajetoria(moeda, conselheira, correcoes)
                    print(f"   {NOMES[moeda]:9s} {conselheira:7s} menor: {menor:5d}   termina em: {final:4d}")
    for moeda, conselheira in sem_saida:
        print(f"\nNÃO CONSEGUI resolver {NOMES[moeda]} de {conselheira} só diminuindo os custos: a moeda cai abaixo do "
              f"mínimo mesmo com custos mínimos (veja o custo \"tudo\" ou a produção).")


def pior_caminho_misto():
    """Só informação: em cada evento a opção que mais gasta daquela moeda (conselheiras misturadas), tudo falha."""
    print("\nPARA SABER (não é exigido pela regra): o pior caminho possível MISTURANDO conselheiras "
          "(em cada evento, a opção que mais gasta daquela moeda):")
    for moeda in MOEDAS:
        valor = inicial(moeda)
        menor = valor
        producao = config.RENDA_POR_ESTACAO.get(moeda, 0)
        for i, evento in enumerate(catalogo.EVENTOS):
            efeitos = []
            for c in ORDEM:
                card = opcao_de(evento, c)["custo"][moeda]
                efeitos.append(-valor if card == "tudo" else custo_da_falha(card))
            valor = min(valor + min(efeitos), config.ESCALA_MAXIMA)
            menor = min(menor, valor)
            if (i + 1) % EVENTOS_POR_ESTACAO == 0:
                valor = min(valor + producao, config.ESCALA_MAXIMA)
        print(f"   {NOMES[moeda]:9s} menor valor: {menor:5d}   termina em: {valor:4d}")


# ------------------------------------------------------------ gravar
def ler_evento(caminho):
    """Lê o EVENTO direto do texto do arquivo (sem o cache __pycache__, que pode estar velho)."""
    escopo = {}
    exec(compile(open(caminho, "rb").read().decode("utf-8"), caminho, "exec"), escopo)
    return escopo["EVENTO"]


def apagar_cache(caminho):
    """Apaga o cache (.pyc) do arquivo, para o jogo ler os números novos."""
    pasta, arquivo = os.path.split(caminho)
    for pyc in glob.glob(os.path.join(pasta, "__pycache__", arquivo[:-3] + ".*.pyc")):
        os.remove(pyc)


def trocar_no_arquivo(texto, conselheira, moeda, novo):
    padrao = re.compile(r'("conselheira":\s*"' + conselheira + r'".*?"custo":\s*\{[^}]*?"' + moeda + r'":\s*)(-?\d+)', re.S)
    achados = padrao.findall(texto)
    if len(achados) != 1:
        raise ValueError(f"não achei o custo de {moeda} de {conselheira} (apareceu {len(achados)} vez(es))")
    return padrao.sub(lambda m: m.group(1) + str(novo), texto, count=1)


def aplicar(correcoes):
    por_arquivo = {}
    for (evento_id, conselheira, moeda), novo in correcoes.items():
        por_arquivo.setdefault(evento_id, []).append((conselheira, moeda, novo))
    novos_textos = {}
    for evento_id, itens in por_arquivo.items():
        arquivos = glob.glob(os.path.join(PASTA, "eventos", f"e{evento_id:02d}_*.py"))
        if len(arquivos) != 1:
            raise ValueError(f"não achei o arquivo do evento {evento_id} em eventos/")
        bruto = open(arquivos[0], "rb").read().decode("utf-8")
        crlf, texto = "\r\n" in bruto, bruto.replace("\r\n", "\n")
        for conselheira, moeda, novo in itens:
            texto = trocar_no_arquivo(texto, conselheira, moeda, novo)
        novos_textos[arquivos[0]] = texto.replace("\n", "\r\n") if crlf else texto
    for caminho, texto in novos_textos.items():
        shutil.copyfile(caminho, caminho + ".antes_do_balanco")
        open(caminho, "wb").write(texto.encode("utf-8"))
        apagar_cache(caminho)
    for (evento_id, conselheira, moeda), novo in correcoes.items():          # confere relendo o que foi gravado
        caminho = glob.glob(os.path.join(PASTA, "eventos", f"e{evento_id:02d}_*.py"))[0]
        lido = opcao_de(ler_evento(caminho), conselheira)["custo"][moeda]
        if lido != novo:
            raise ValueError(f"conferência falhou no evento {evento_id}, {conselheira}, {moeda}: gravei {novo}, li {lido}")
    return len(novos_textos)


def main():
    linhas, correcoes, sem_saida = calcular()
    mostrar(linhas, correcoes, sem_saida)
    pior_caminho_misto()
    if not correcoes:
        return 0 if not sem_saida else 1
    if "--aplicar" not in sys.argv:
        print(f"\n{len(correcoes)} custos mudariam. (Nada foi gravado. Para gravar: python ferramentas/balancear_economia.py --aplicar)")
        return 0
    try:
        arquivos = aplicar(correcoes)
    except ValueError as erro:
        print(f"\nERRO: {erro}.\nPode ter sobrado algum arquivo alterado; as cópias de antes estão em eventos/*.antes_do_balanco.")
        return 1
    print(f"\nGravei {len(correcoes)} custos em {arquivos} arquivos de eventos/ (as cópias de antes ficaram com o final "
          f".antes_do_balanco).")
    print("Rode de novo (python ferramentas/balancear_economia.py) para conferir: tem que dizer \"Nada a mudar\".")
    return 0


if __name__ == "__main__":
    sys.exit(main())
