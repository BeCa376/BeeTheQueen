# -*- mode: python ; coding: utf-8 -*-
# Gera o executável do jogo:  pyinstaller --noconfirm bee_the_queen.spec
# O resultado sai em dist/BeeTheQueen.exe
import glob
import os

raiz = SPECPATH


def modulos(pasta, padrao="*.py"):
    """catalogo.py importa estes arquivos pelo nome, enquanto o jogo roda; o PyInstaller
    não enxerga isso sozinho, então a lista precisa estar aqui."""
    arquivos = glob.glob(os.path.join(raiz, pasta, padrao))
    return [f"{pasta}.{os.path.splitext(os.path.basename(a))[0]}" for a in sorted(arquivos)]


a = Analysis(
    ["main.py"],
    pathex=[raiz],
    datas=[("assets", "assets")],
    hiddenimports=(modulos("eventos") + modulos("resultados") + modulos("introducao")
                   + modulos("minigames", "e[0-9][0-9]_*.py")),
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name="BeeTheQueen",
    console=False,
    icon=os.path.join(raiz, "assets", "icone.ico") if os.path.exists(os.path.join(raiz, "assets", "icone.ico")) else None,   # o ícone do .exe: a abelhinha
)
