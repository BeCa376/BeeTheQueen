# -*- coding: utf-8 -*-
"""
CONFERIR A ECONOMIA: mostra os custos de cada evento e o que sobra de cada moeda no pior caso.

Rode na pasta do projeto (a do main.py), com o (venv) ativo:

    python ferramentas/conferir_economia.py

Ele NÃO muda nada nos seus arquivos. Usa as regras de verdade (regras.resolver) e os seus eventos, então os
números são os do jogo: o custo do card, os fatores do sucesso/parcial/falha, a produção da estação e o piso.

Mostra:
  1) o custo de cada opção em cada evento (o que aparece no card);
  2) jogando SEMPRE com a mesma conselheira, com tudo falha / tudo parcial / tudo sucesso: como cada moeda
     termina e o MENOR valor que ela chegou a ter, COM e SEM a produção da estação;
  3) o PIOR CAMINHO possível (em cada evento, a opção que mais gasta daquela moeda, e tudo falha).
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))     # a pasta do PROJETO (a de cima desta)

import catalogo  # noqa: E402
import config  # noqa: E402
import regras  # noqa: E402
from data.councilors import ORDEM  # noqa: E402

RESULTADOS = (("tudo FALHA", 0.25), ("tudo PARCIAL", 0.5), ("tudo SUCESSO", 1.0))
MOEDAS = ("mel", "operarias", "relacao")


def opcao_de(evento, conselheira):
    return next(o for o in evento["opcoes"] if o["conselheira"] == conselheira)


def jogar(escolher, multiplicador, com_producao=True):
    """Joga os 12 eventos com a regra `escolher(evento) -> conselheira` e devolve (final, menor de cada moeda)."""
    guardada = dict(config.RENDA_POR_ESTACAO)
    if not com_producao:
        for moeda in guardada:
            config.RENDA_POR_ESTACAO[moeda] = 0
    try:
        estado = regras.Estado()
        menor = {m: getattr(estado, m) for m in MOEDAS}
        for evento in catalogo.EVENTOS:
            regras.resolver(estado, evento, opcao_de(evento, escolher(evento)), multiplicador)
            for m in MOEDAS:
                menor[m] = min(menor[m], getattr(estado, m))
        return {m: getattr(estado, m) for m in MOEDAS}, menor
    finally:
        config.RENDA_POR_ESTACAO.clear()
        config.RENDA_POR_ESTACAO.update(guardada)


def custo_numerico(opcao, moeda):
    valor = opcao["custo"][moeda]
    return -10 ** 6 if valor == "tudo" else valor


def main():
    print(f"Produção da estação: {dict(config.RENDA_POR_ESTACAO)}  (uma vez por estação, depois do 3º evento dela)")
    print(f"Fatores do custo: {config.FATOR_DO_CUSTO} | do ganho: {config.FATOR_DO_GANHO}")
    print(f"Piso das moedas: {getattr(config, 'PISO_DAS_MOEDAS', '(não existe no config)')}\n")

    print("1) O CUSTO NO CARD de cada opção, por evento (mel / operárias / relação):")
    print("   evento | " + " | ".join(f"{c:^17s}" for c in ORDEM))
    for ev in catalogo.EVENTOS:
        celulas = []
        for c in ORDEM:
            o = opcao_de(ev, c)["custo"]
            celulas.append(f"{str(o['mel']):>5s} {o['operarias']:>4d} {o['relacao']:>+3d}")
        print(f"    {ev['id']:>3}   | " + " | ".join(f"{x:17s}" for x in celulas))

    print("\n2) JOGANDO SEMPRE COM A MESMA CONSELHEIRA, do evento 1 ao 12 (começa em 100 / 100 / 60):")
    print("   (final: mel / operárias / relação   |   o MENOR valor de cada moeda durante o jogo)")
    for nome, mult in RESULTADOS:
        print(f"\n   {nome}")
        for c in ORDEM:
            com, menor_com = jogar(lambda ev: c, mult, True)
            sem, menor_sem = jogar(lambda ev: c, mult, False)
            print(f"     {c:7s} COM produção: {com['mel']:4d} / {com['operarias']:4d} / {com['relacao']:3d}"
                  f"  (menor: {menor_com['mel']:4d} / {menor_com['operarias']:4d} / {menor_com['relacao']:3d})"
                  f"  |  SEM produção: {sem['mel']:4d} / {sem['operarias']:4d} / {sem['relacao']:3d}")

    print("\n3) O PIOR CAMINHO POSSÍVEL: em cada evento, a opção que mais gasta daquela moeda, e tudo FALHA:")
    for moeda in ("mel", "operarias"):
        def pior(ev, moeda=moeda):
            return min(ev["opcoes"], key=lambda o: custo_numerico(o, moeda))["conselheira"]
        com, menor_com = jogar(pior, 0.25, True)
        sem, menor_sem = jogar(pior, 0.25, False)
        caminho = ", ".join(pior(ev) for ev in catalogo.EVENTOS)
        print(f"   {moeda:9s}: termina em {com[moeda]:4d} COM produção (a menor foi {menor_com[moeda]:4d}), "
              f"{sem[moeda]:4d} SEM produção (a menor foi {menor_sem[moeda]:4d})")
        print(f"              caminho: {caminho}")
    print("\n(Se algum número ficar abaixo do piso ou negativo, o piso das moedas é o que segura no jogo.)")


if __name__ == "__main__":
    main()
