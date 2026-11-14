# -*- coding: utf-8 -*-
"""
LIMPA A PASTA DO PROJETO: tira o que não serve mais (versões antigas, scripts de uma vez só, pastas de
build...) e deixa cada coisa no seu lugar.

Rode na pasta do projeto (a mesma do main.py), com o (venv) ativo:

    python limpar_lixo.py              só MOSTRA o que sairia (não mexe em nada)
    python limpar_lixo.py --aplicar    move tudo isso para a pasta _lixo_removido/

Nada é apagado de verdade: as coisas vão para _lixo_removido/ (com o mesmo caminho de antes). Rode o jogo, e se
estiver tudo certo, apague a pasta _lixo_removido/ quando quiser. Se faltar alguma coisa, é só mover de volta.
(As pastas __pycache__ são apagadas mesmo: o Python recria sozinho.) O script também se move para lá no fim.

Nunca mexe em: venv/, .git/, eventos/, resultados/, introducao/, minigames/, telas/, assets/, data/, testes/,
ferramentas/ e nos arquivos principais do jogo.
"""
import fnmatch
import os
import shutil
import sys

PASTA = os.path.dirname(os.path.abspath(__file__))
LIXEIRA = "_lixo_removido"
NUNCA_ENTRAR = {"venv", ".venv", ".git", ".idea", LIXEIRA}

PASTAS_INUTEIS = [
    ("build", "pasta temporária do PyInstaller (o .spec gera de novo)"),
    ("dist", "o .exe antigo (gere de novo com: pyinstaller --noconfirm bee_the_queen.spec)"),
    ("legado", "código antigo, fora de uso (o README já dizia que podia apagar)"),
]
ARQUIVOS_DA_RAIZ = [
    ("aplicar_popup.py", "script de uma vez só (já aplicado)"),
    ("aplicar_inicio_e_retentar.py", "script de uma vez só (já aplicado)"),
    ("tirar_consequencia.py", "script de uma vez só (já aplicado)"),
    ("limitar_em_100.py", "script de uma vez só (já aplicado)"),
    ("mensagem_padrao.py", "script de uma vez só (já aplicado)"),
    ("diagnosticar_popup.py", "script de diagnóstico (o popup já está instalado)"),
    ("ajustar_custos.py", "simulação que não foi aplicada"),
]
# (as ferramentas que agora moram em ferramentas/ e os testes que moram em testes/: só saem da raiz se a cópia nova existir)
MOVIDOS_PARA = {
    "balancear_economia.py": "ferramentas", "conferir_economia.py": "ferramentas", "testar_calculos.py": "ferramentas",
    "jogar_tudo.py": "testes", "jogos_novos.py": "testes",
}
PADROES_DA_RAIZ = [
    ("*.zip", "zip de uma entrega antiga"),
    ("resultado_dos_testes*.txt", "relatório de teste antigo (o novo sai em ferramentas/)"),
    ("LEIA-ME*.txt", "leia-me de uma entrega antiga"),
]
PADROES_EM_QUALQUER_LUGAR = [("*.antes_*", "cópia de segurança de um script antigo")]


def tamanho(caminho):
    if os.path.isfile(caminho):
        total = os.path.getsize(caminho)
    else:
        total = sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(caminho) for f in fs)
    return f"{total / 1_000_000:.1f} MB" if total >= 100_000 else f"{max(1, total // 1000)} KB"


def achar():
    """A lista de (caminho relativo, motivo) do que sairia, e as pastas __pycache__."""
    achados, caches = [], []
    for nome, motivo in PASTAS_INUTEIS:
        if os.path.isdir(os.path.join(PASTA, nome)):
            achados.append((nome, motivo))
    for nome, motivo in ARQUIVOS_DA_RAIZ:
        if os.path.isfile(os.path.join(PASTA, nome)):
            achados.append((nome, motivo))
    for nome, destino in MOVIDOS_PARA.items():
        if os.path.isfile(os.path.join(PASTA, nome)) and os.path.isfile(os.path.join(PASTA, destino, nome)):
            achados.append((nome, f"agora mora em {destino}/{nome}"))
    for item in sorted(os.listdir(PASTA)):
        caminho = os.path.join(PASTA, item)
        if os.path.isfile(caminho):
            for padrao, motivo in PADROES_DA_RAIZ:
                if fnmatch.fnmatch(item, padrao) and item not in (os.path.basename(__file__),):
                    achados.append((item, motivo))
                    break
    ja = {a for a, _ in achados}
    for raiz, pastas, arquivos in os.walk(PASTA):
        pastas[:] = [p for p in pastas if p not in NUNCA_ENTRAR and os.path.relpath(os.path.join(raiz, p), PASTA) not in ja]
        if os.path.basename(raiz) == "__pycache__":
            caches.append(raiz)
            continue
        for arquivo in arquivos:
            for padrao, motivo in PADROES_EM_QUALQUER_LUGAR:
                relativo = os.path.relpath(os.path.join(raiz, arquivo), PASTA)
                if fnmatch.fnmatch(arquivo, padrao) and relativo not in ja:
                    achados.append((relativo, motivo))
    return sorted(achados), caches


def main():
    aplicar = "--aplicar" in sys.argv
    achados, caches = achar()
    if not achados and not caches:
        print("A pasta já está limpa. Nada a fazer.")
        return 0
    print("O que sai da pasta do projeto:\n" if achados else "")
    for relativo, motivo in achados:
        print(f"  {relativo:48s} {tamanho(os.path.join(PASTA, relativo)):>9}   {motivo}")
    if caches:
        print(f"  {len(caches)} pasta(s) __pycache__ (o Python recria sozinho)")
    if not aplicar:
        print("\n(Nada foi mexido. Para mover isso para a pasta _lixo_removido/, rode: python limpar_lixo.py --aplicar)")
        return 0
    for relativo, _ in achados:
        destino = os.path.join(PASTA, LIXEIRA, relativo)
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        shutil.move(os.path.join(PASTA, relativo), destino)
    for cache in caches:
        shutil.rmtree(cache, ignore_errors=True)
    meu = os.path.abspath(__file__)
    os.makedirs(os.path.join(PASTA, LIXEIRA), exist_ok=True)
    print(f"\nPronto! {len(achados)} item(ns) movidos para {LIXEIRA}/ (nada foi apagado). Rode o jogo para conferir;")
    print(f"se estiver tudo certo, apague a pasta {LIXEIRA}/. Este script também vai para lá agora.")
    shutil.move(meu, os.path.join(PASTA, LIXEIRA, os.path.basename(meu)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
