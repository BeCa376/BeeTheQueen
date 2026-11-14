# -*- coding: utf-8 -*-
"""Gera todos os PNGs de pixel art do jogo (por padrão, na pasta assets/pixel/, a de cima desta).

    pip install numpy pillow          (só é preciso para refazer os desenhos; o jogo NÃO precisa disso)
    python gerar_pixelart.py [pasta_de_destino]

Os desenhos já vêm prontos na pasta assets/pixel/. Cada PNG pode ser aberto e retocado no Aseprite: o jogo lê os
arquivos como estão. Rodar este script de novo REFAZ todos e apaga os retoques que você tiver feito."""
import base64
import os
import sys
import zlib

import molduras
import pxart
import sprites
import tiles


def gerar(destino):
    os.makedirs(destino, exist_ok=True)
    arquivos = {}
    for nome, fabrica in sprites.TODOS.items():
        arquivos[nome] = fabrica()
    arquivos["gota_mini"] = molduras.gota_pequena()
    arquivos["pinta"] = molduras.pinta_do_domino()
    arquivos["pote_soma"] = molduras.pote_da_soma()
    arquivos["brilho_pote"] = molduras.brilho_do_pote()
    for nome, fabrica in tiles.TILES.items():
        arquivos["fundo_" + nome] = fabrica()
    for nome, fabrica in tiles.BLOCOS.items():
        arquivos[nome] = fabrica()
    arquivos["bloco_neutro"] = molduras.bloco_neutro()
    arquivos["borda_campo"] = molduras.borda_do_campo()
    for nome in molduras.ESTILOS_DE_BORDA:
        arquivos["borda_" + nome] = molduras.borda(nome)
    for nome, tela in arquivos.items():
        tela.salvar(os.path.join(destino, nome + ".png"))
    return arquivos


def escrever_dados(arquivos, caminho):
    """Grava os mesmos desenhos DENTRO de um arquivo .py (pixel_dados.py): se a pasta assets/pixel sumir, o jogo
    continua com o visual certo, porque os desenhos também vão junto com o código."""
    linhas = ["# -*- coding: utf-8 -*-",
              '"""Os desenhos de assets/pixel/ guardados dentro do código (pixels crus, comprimidos).',
              "",
              "O jogo usa os PNGs da pasta assets/pixel/ quando eles existem (é assim que você retoca os desenhos) e",
              "estes dados quando não existem. GERADO por assets/pixel/gerador/gerar_pixelart.py: não edite à mão.",
              '"""',
              "", "DESENHOS = {"]
    for nome in sorted(arquivos):
        tela = arquivos[nome]
        texto = base64.b64encode(zlib.compress(tela.img.tobytes(), 9)).decode("ascii")
        pedacos = [texto[i:i + 96] for i in range(0, len(texto), 96)]
        linhas.append(f'    "{nome}": ({tela.w}, {tela.h},')
        linhas += [f'        "{p}"' for p in pedacos]
        linhas.append("    ),")
    linhas.append("}")
    with open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(linhas) + "\n")


if __name__ == "__main__":
    destino = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    arquivos = gerar(destino)
    print(f"{len(arquivos)} arquivos em {destino}")
    jogos = os.path.join(os.path.dirname(os.path.dirname(destino)), "minigames", "jogos")
    if os.path.isdir(jogos):
        escrever_dados(arquivos, os.path.join(jogos, "pixel_dados.py"))
        print("e os mesmos desenhos dentro de", os.path.join(jogos, "pixel_dados.py"))
