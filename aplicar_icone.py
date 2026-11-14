# -*- coding: utf-8 -*-
"""
COLOCA A ABELHINHA COMO ÍCONE DO JOGO:
  - da JANELA e da BARRA DE TAREFAS (telas/visual.py usa assets/icone.png);
  - do ARQUIVO .exe (bee_the_queen.spec usa assets/icone.ico), tanto na pasta dist quanto onde você copiar o jogo.

Rode UMA vez, na pasta do projeto (a mesma do main.py), com o (venv) ativo:

    python aplicar_icone.py

Depois gere o .exe de novo (gerar_exe.bat). Ele confere os pontos antes de mexer (se algum não for achado, não muda
NADA e diz qual), guarda cópias (final .antes_do_icone) e, se rodar de novo, percebe que já está aplicado.
(Para trocar o desenho do ícone, troque os arquivos assets/icone.png e assets/icone.ico.)
"""
import os
import shutil
import sys

PASTA = os.path.dirname(os.path.abspath(__file__))
VISUAL = os.path.join(PASTA, "telas", "visual.py")
SPEC = os.path.join(PASTA, "bee_the_queen.spec")
ARQUIVOS_DO_ICONE = [os.path.join(PASTA, "assets", "icone.png"), os.path.join(PASTA, "assets", "icone.ico")]

VISUAL_VELHO = "        pygame.display.set_caption(config.TITULO_DA_JANELA)\n"
VISUAL_NOVO = '''        # o ícone da janela e da barra de tarefas: a abelhinha (assets/icone.png)
        if os.name == "nt":      # sem isto, no Windows a barra de tarefas agrupa o jogo sob o ícone do Python
            try:
                import ctypes
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("BeeTheQueen.Jogo")
            except Exception:
                pass
        try:
            pygame.display.set_icon(pygame.image.load(os.path.join(PASTA_DE_IMAGENS, "icone.png")))
        except (pygame.error, FileNotFoundError):
            pass                 # sem o arquivo, a janela fica com o ícone padrão
        pygame.display.set_caption(config.TITULO_DA_JANELA)
'''
SPEC_VELHO = '    name="BeeTheQueen",\n    console=False,\n)'
SPEC_NOVO = ('    name="BeeTheQueen",\n    console=False,\n'
             '    icon=os.path.join(raiz, "assets", "icone.ico") if os.path.exists(os.path.join(raiz, "assets", "icone.ico")) else None,'
             '   # o ícone do .exe: a abelhinha\n)')


def ler(caminho):
    dados = open(caminho, "rb").read().decode("utf-8")
    return dados.replace("\r\n", "\n"), "\r\n" in dados


def gravar(caminho, texto, crlf):
    open(caminho, "wb").write((texto.replace("\n", "\r\n") if crlf else texto).encode("utf-8"))


def trocar(texto, velho, novo, onde):
    if texto.count(velho) != 1:
        raise ValueError(f"não achei {onde} do jeito esperado (apareceu {texto.count(velho)} vez(es))")
    return texto.replace(velho, novo)


def main():
    faltando = [os.path.relpath(c, PASTA) for c in ARQUIVOS_DO_ICONE + [VISUAL, SPEC] if not os.path.exists(c)]
    if faltando:
        print("ERRO: não achei " + ", ".join(faltando) + ". Descompacte o zip inteiro NA PASTA DO PROJETO e rode de novo.")
        return 1
    visual, crlf_visual = ler(VISUAL)
    spec, crlf_spec = ler(SPEC)
    if "icone.png" in visual and "icone.ico" in spec:
        print("Já está aplicado. Nada foi mudado.")
        return 0
    try:
        novo_visual = visual if "icone.png" in visual else trocar(visual, VISUAL_VELHO, VISUAL_NOVO, "a linha do título da janela em telas/visual.py")
        novo_spec = spec if "icone.ico" in spec else trocar(spec, SPEC_VELHO, SPEC_NOVO, "o bloco EXE em bee_the_queen.spec")
    except ValueError as erro:
        print(f"ERRO: {erro}.")
        print("NADA foi mudado nos seus arquivos. Me mande o telas/visual.py e o bee_the_queen.spec que eu ajusto.")
        return 1
    for caminho in (VISUAL, SPEC):
        shutil.copyfile(caminho, caminho + ".antes_do_icone")
    gravar(VISUAL, novo_visual, crlf_visual)
    gravar(SPEC, novo_spec, crlf_spec)
    print("Pronto! A janela e a barra de tarefas já usam a abelhinha. Para o .exe também, gere de novo (gerar_exe.bat).")
    print("(As cópias de antes ficaram com o final .antes_do_icone.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
