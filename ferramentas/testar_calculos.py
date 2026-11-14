# -*- coding: utf-8 -*-
"""
TESTAR OS CÁLCULOS: joga todas as combinações pelo jogo de verdade e salva o resultado num .txt.

Rode na pasta do projeto (a do main.py), com o (venv) ativo:

    python ferramentas/testar_calculos.py

Ele NÃO muda nada nos seus arquivos. Usa a mesma conta do jogo (regras.resolver e o multiplicador do
minigame), então os números do .txt são os que você veria jogando. Gera o arquivo resultado_dos_testes.txt
na mesma pasta, com:

  PARTE 1  os 12 eventos com UMA conselheira só, na falha, no parcial e no sucesso (4 x 3 = 12 testes)
  PARTE 2  uma conselheira em CADA ESTAÇÃO (3 eventos), na falha, no parcial e no sucesso, começando
           de 100 / 100 / 60 em cada teste (4 conselheiras x 4 estações x 3 resultados = 48 testes)
  PARTE 3  a sequência Flora, Melina, Aurora, Nectar nos 12 eventos, na falha, no parcial e no sucesso
  PARTE 4  a tabela do desconto de cada escolha (o card e o que cada resultado cobra de verdade)
  RESUMO   o valor final e o MENOR valor de cada moeda em cada teste das partes 1 e 3

Em cada linha: o valor de cada moeda DEPOIS do evento. Entre colchetes: o que a escolha cobrou, a produção
da estação (só no fim de cada estação) e, nesse caso, o valor ANTES da produção.
"""
import datetime
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
PASTA = os.path.dirname(os.path.abspath(__file__))                       # esta pasta (ferramentas/)
sys.path.insert(0, os.path.dirname(PASTA))                              # a pasta do PROJETO (a de cima)

import catalogo  # noqa: E402
import config  # noqa: E402
import regras  # noqa: E402
from data.councilors import ORDEM  # noqa: E402
from minigames.jogos.base import BasePuzzle  # noqa: E402

ARQUIVO = os.path.join(PASTA, "resultado_dos_testes.txt")
MOEDAS = ("mel", "operarias", "relacao")
ROTULOS = {"mel": "mel", "operarias": "operárias", "relacao": "relação"}
RESULTADOS = ("falha", "parcial", "sucesso")
SEQUENCIA = ("Flora", "Melina", "Aurora", "Nectar")
NOMES_DAS_ESTACOES = {"Primavera": "primavera", "Verao": "verão", "Verão": "verão", "Outono": "outono", "Inverno": "inverno"}


class _Resultado:
    def __init__(self, resultado):
        self.result = resultado


def multiplicador(resultado):
    """O multiplicador que o jogo usa para sucesso / parcial / falha (a função do próprio minigame)."""
    return BasePuzzle.effect_multiplier(_Resultado(resultado))


def estado_inicial():
    return regras.Estado()


def valores(estado):
    return {m: getattr(estado, m) for m in MOEDAS}


def jogar_evento(estado, evento, conselheira, resultado):
    """Joga UM evento: devolve (valores depois, o que a escolha cobrou, a produção da estação)."""
    antes = valores(estado)
    opcao = next(o for o in evento["opcoes"] if o["conselheira"] == conselheira)
    res = regras.resolver(estado, evento, opcao, multiplicador(resultado))
    depois = valores(estado)
    renda = {m: v for m, v in (getattr(res, "renda", None) or {}).items() if v}
    escolha = {m: depois[m] - antes[m] - renda.get(m, 0) for m in MOEDAS}
    return depois, escolha, renda


def sinal(v):
    return f"{v:+d}"


def linha_do_evento(evento, depois, escolha, renda, conselheira=None):
    quem = f" ({conselheira})" if conselheira else ""
    base = (f"Evento {evento['id']}{quem} : mel {depois['mel']} | operárias {depois['operarias']} | "
            f"relação {depois['relacao']}")
    detalhe = "escolha: " + ", ".join(f"{ROTULOS[m]} {sinal(escolha[m])}" for m in MOEDAS)
    if renda:
        detalhe += " | produção da estação: " + ", ".join(f"{ROTULOS[m]} {sinal(v)}" for m, v in renda.items())
        antes_da_producao = {m: depois[m] - renda.get(m, 0) for m in MOEDAS}
        detalhe += (f" | antes da produção: mel {antes_da_producao['mel']} | operárias "
                    f"{antes_da_producao['operarias']} | relação {antes_da_producao['relacao']}")
    return f"{base}      [{detalhe}]"


def rodar(titulo, passos, resultado, mostrar_conselheira=False):
    """Joga uma sequência de (evento, conselheira) com o mesmo `resultado`, começando do estado inicial.
    Devolve (linhas de texto, valor final, menor valor de cada moeda, maior valor de cada moeda)."""
    estado = estado_inicial()
    linhas = [f"{titulo}:"]
    menor = valores(estado)
    maior = valores(estado)
    for evento, conselheira in passos:
        depois, escolha, renda = jogar_evento(estado, evento, conselheira, resultado)
        linhas.append(linha_do_evento(evento, depois, escolha, renda, conselheira if mostrar_conselheira else None))
        for m in MOEDAS:
            menor[m] = min(menor[m], depois[m])
            maior[m] = max(maior[m], depois[m])
    return linhas, valores(estado), menor, maior


def estacoes_na_ordem():
    vistas = []
    for evento in catalogo.EVENTOS:
        if evento["estacao"] not in vistas:
            vistas.append(evento["estacao"])
    return vistas


def tabela_dos_descontos():
    """Cada escolha de cada evento: o card e o que sucesso / parcial / falha cobram de verdade, num estado com
    FOLGA (60 / 60 / 50): longe do piso e do máximo de 100, para eles não esconderem nenhum desconto."""
    linhas = []
    for evento in catalogo.EVENTOS:
        for conselheira in ORDEM:
            card = next(o for o in evento["opcoes"] if o["conselheira"] == conselheira)["custo"]
            partes = ["card: " + ", ".join(f"{ROTULOS[m]} {card[m] if card[m] == 'tudo' else sinal(card[m])}"
                                           for m in MOEDAS)]
            for resultado in ("sucesso", "parcial", "falha"):
                estado = estado_inicial()
                estado.mel, estado.operarias, estado.relacao = 60, 60, 50
                _, escolha, _ = jogar_evento(estado, evento, conselheira, resultado)
                partes.append(f"{resultado}: " + ", ".join(f"{ROTULOS[m]} {sinal(escolha[m])}" for m in MOEDAS))
            linhas.append(f"Evento {evento['id']:>2} | {conselheira:7s} | " + " | ".join(partes))
    return linhas


def main():
    inicial = valores(estado_inicial())
    piso = getattr(config, "PISO_DAS_MOEDAS", None)
    saida = []

    def escrever(texto=""):
        saida.append(texto)

    escrever("RESULTADO DOS TESTES DE CÁLCULO")
    escrever(f"Gerado em {datetime.datetime.now():%d/%m/%Y %H:%M}")
    escrever(f"Começa em: mel {inicial['mel']} | operárias {inicial['operarias']} | relação {inicial['relacao']}")
    escrever(f"Fatores do custo: {dict(config.FATOR_DO_CUSTO)} | dos ganhos: {dict(config.FATOR_DO_GANHO)}")
    escrever(f"Produção da estação (depois dos eventos 3, 6, 9 e 12): {dict(config.RENDA_POR_ESTACAO)}")
    escrever(f"Piso das moedas: {piso} | máximo de cada moeda: {config.ESCALA_MAXIMA}")
    escrever("Resultados: sucesso = x1.0 | parcial = x0.5 | falha = x0.25 (o multiplicador do minigame)")
    ponte = [e["id"] for e in catalogo.EVENTOS
             if (catalogo.RESULTADOS[e["id"]].get("proximo") or {}).get("fator_custo")]
    escrever(f"Ponte de custo ativa nos resultados dos eventos: {ponte if ponte else 'nenhuma'}")
    escrever("")

    resumo = []

    escrever("=" * 100)
    escrever("PARTE 1: OS 12 EVENTOS COM UMA CONSELHEIRA SÓ")
    escrever("=" * 100)
    for resultado in RESULTADOS:
        for conselheira in ORDEM:
            passos = [(e, conselheira) for e in catalogo.EVENTOS]
            linhas, final, menor, maior = rodar(f"Só {conselheira} - {resultado}", passos, resultado)
            escrever("\n".join(linhas))
            escrever("")
            resumo.append((f"Só {conselheira} - {resultado}", final, menor, maior))

    escrever("=" * 100)
    escrever("PARTE 2: UMA CONSELHEIRA EM CADA ESTAÇÃO (cada teste começa de "
             f"{inicial['mel']} / {inicial['operarias']} / {inicial['relacao']})")
    escrever("=" * 100)
    for conselheira in ORDEM:
        for estacao in estacoes_na_ordem():
            eventos = [e for e in catalogo.EVENTOS if e["estacao"] == estacao]
            for resultado in RESULTADOS:
                nome = NOMES_DAS_ESTACOES.get(estacao, estacao.lower())
                linhas, _, _, _ = rodar(f"{conselheira} ({nome}) - {resultado}",
                                     [(e, conselheira) for e in eventos], resultado)
                escrever("\n".join(linhas))
                escrever("")

    escrever("=" * 100)
    escrever("PARTE 3: SEQUÊNCIA " + ", ".join(SEQUENCIA) + " (repetindo, do evento 1 ao 12)")
    escrever("=" * 100)
    for resultado in RESULTADOS:
        passos = [(e, SEQUENCIA[i % len(SEQUENCIA)]) for i, e in enumerate(catalogo.EVENTOS)]
        linhas, final, menor, maior = rodar(f"Sequência {' > '.join(SEQUENCIA)} - {resultado}", passos, resultado,
                                            mostrar_conselheira=True)
        escrever("\n".join(linhas))
        escrever("")
        resumo.append((f"Sequência - {resultado}", final, menor, maior))

    escrever("=" * 100)
    escrever("PARTE 4: O DESCONTO DE CADA ESCOLHA (o card e o que cada resultado cobra, num estado com folga: 60 / 60 / 50)")
    escrever("=" * 100)
    escrever("\n".join(tabela_dos_descontos()))
    escrever("")

    escrever("=" * 100)
    escrever("RESUMO (partes 1 e 3): como termina e o MENOR valor de cada moeda durante o jogo")
    escrever("=" * 100)
    for titulo, final, menor, maior in resumo:
        avisos = []
        for m in MOEDAS:
            if maior[m] > config.ESCALA_MAXIMA:
                avisos.append(f"{ROTULOS[m]} ACIMA DE {config.ESCALA_MAXIMA}")
            if menor[m] < 0:
                avisos.append(f"{ROTULOS[m]} NEGATIVA")
            elif piso is not None and menor[m] <= piso:
                avisos.append(f"{ROTULOS[m]} no piso")
        escrever(f"{titulo:34s} termina: mel {final['mel']:4d} | operárias {final['operarias']:4d} | "
                 f"relação {final['relacao']:4d}   menor: mel {menor['mel']:4d} | operárias {menor['operarias']:4d} | "
                 f"relação {menor['relacao']:4d}" + (f"   <-- {', '.join(avisos)}" if avisos else ""))

    texto = "\n".join(saida) + "\n"
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        f.write(texto)
    print(f"Pronto! Salvei {texto.count(chr(10))} linhas em: {ARQUIVO}")
    print("Mande esse arquivo (resultado_dos_testes.txt) aqui para eu avaliar.")
    for titulo, final, menor, maior in resumo:
        if any(menor[m] < 0 for m in MOEDAS):
            print(f"ATENÇÃO: {titulo}: alguma moeda ficou negativa.")
        if any(maior[m] > config.ESCALA_MAXIMA for m in MOEDAS):
            print(f"ATENÇÃO: {titulo}: alguma moeda passou de {config.ESCALA_MAXIMA}.")


if __name__ == "__main__":
    main()
