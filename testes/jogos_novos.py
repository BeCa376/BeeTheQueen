# -*- coding: utf-8 -*-
"""
CONFERE AS REGRAS DOS 12 JOGOS, o rodízio e a ordem das conselheiras.

Rode depois de mexer em qualquer jogo (um número, uma regra, um texto):

    python testes/jogos_novos.py

Para cada jogo ele confere: que cria e desenha em todas as dificuldades, que ficar PARADO nunca
ganha, o tempo e as quantidades de cada um, que ele é GANHÁVEL (jogando de verdade, com o mouse),
e os resultados nos limites (sucesso / parcial / falha). Depois confere o rodízio dos 12 jogos
e que as conselheiras aparecem SEMPRE na mesma ordem (Flora, Melina, Nectar, Aurora).
"""
import itertools
import math
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")      # janela invisível
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

import catalogo
import config
import main
from data.councilors import ORDEM
from minigames import rodizio
from minigames.jogos import campo_minado as cm, labirinto as lab, quebra_cabeca_de_encaixe as qe
from minigames.jogos.antes_da_poda import AntesDaPoda
from minigames.jogos.campo_minado import CampoMinado
from minigames.jogos.captura_de_abelhas import CapturaDeAbelhas
from minigames.jogos.comunicacao_em_simbolos import ComunicacaoEmSimbolos
from minigames.jogos.domino import Domino
from minigames.jogos.jogo_da_memoria import JogoDaMemoria
from minigames.jogos.labirinto import Labirinto
from minigames.jogos.quebra_cabeca_de_encaixe import QuebraCabecaDeEncaixe
from minigames.jogos.quebra_cabeca_de_soma import QuebraCabecaDeSoma
from minigames.jogos.rastro_de_polen import RastroDePolen
from minigames.jogos.rota_de_voo import RotaDeVoo
from minigames.jogos.sob_as_folhas import SobAsFolhas
from telas import componentes, layout

DT = 1 / 60
RESULTADOS = ("sucesso", "parcial", "falha")
falhas = []


def conferir(condicao, mensagem):
    print(("  ok     " if condicao else "  FALHOU ") + mensagem)
    if not condicao:
        falhas.append(mensagem)


def area():
    return layout.area_do_minigame()


def avancar(jogo, segundos):
    for _ in range(max(1, round(segundos / DT))):
        if jogo.done:
            break
        jogo.update(DT)


def terminar_pelo_tempo(jogo):
    t = 0.0
    while not jogo.done and t < 400:
        jogo.update(1 / 30)
        t += 1 / 30
    return t


def resultado(classe, **ajustes):
    """Cria o jogo, ajusta o estado (atributos), fecha e devolve o resultado."""
    random.seed(1)
    g = classe(area(), difficulty=2)
    for nome, valor in ajustes.items():
        setattr(g, nome, valor)
    return g


# ============================================================ jogadores que GANHAM, jogando de verdade
def ganhar_sob_as_folhas(d, semente):
    random.seed(semente)
    g = SobAsFolhas(area(), difficulty=d)
    r = g.rect
    while not g.done:
        achou = False
        for y in range(r.top + 4, r.bottom, 8):
            for x in range(r.left + 4, r.right, 8):
                coisa = g._o_que_esta_em_cima((x, y))
                if coisa and coisa[0] == "folha":
                    g.handle_click((x, y))
                    achou = True
                    break
            if achou or g.done:
                break
        if not achou:
            break
        avancar(g, 0.1)
    return g


def ganhar_polen(d, semente, vel=500):
    random.seed(semente)
    g = RastroDePolen(area(), difficulty=d)
    r = g.rect
    passo = 3 * g.cell_size - 6
    pontos, y, i = [], r.top + g.cell_size, 0
    while y < r.bottom:
        xs = (r.left + 4, r.right - 4) if i % 2 == 0 else (r.right - 4, r.left + 4)
        pontos += [(xs[0], y), (xs[1], y)]
        y, i = y + passo, i + 1
    atual = pygame.Vector2(pontos[0])
    g.handle_click((int(atual.x), int(atual.y)))
    for alvo in pontos[1:]:
        alvo = pygame.Vector2(alvo)
        while (alvo - atual).length() > 1 and not g.done:
            mov = alvo - atual
            if mov.length() > vel * DT:
                mov.scale_to_length(vel * DT)
            atual += mov
            g.handle_drag((int(atual.x), int(atual.y)), True)
            g.update(DT)
    avancar(g, 20)
    return g


def ganhar_rota(d, semente):
    random.seed(semente)
    g = RotaDeVoo(area(), difficulty=d)
    pt = lambda c: tuple(map(int, g._cell_center(c)))
    g.handle_click(pt(g.path_solution[0]))
    for celula in g.path_solution[1:]:
        g.handle_drag(pt(celula), True)
        avancar(g, 0.3)
    return g


def ganhar_poda(d, semente):
    random.seed(semente)
    g = AntesDaPoda(area(), difficulty=d)
    for planta in sorted((p for p in g.plantas if p.doente), key=lambda p: p.rect.centerx):
        g.handle_click(planta.rect.center)
        avancar(g, 0.3)
    return g


def ganhar_captura(d, semente):
    """Pastoreia: leva cada abelha à frente da entrada e depois a empurra para dentro."""
    random.seed(semente)
    g = CapturaDeAbelhas(area(), difficulty=d)
    cursor = pygame.Vector2(g.rect.left + 20, g.rect.centery)
    dentro = pygame.Vector2(g.abrigo.left + 70, g.entrada.centery)
    frente = pygame.Vector2(g.abrigo.left - 55, g.entrada.centery)
    while not g.done:
        fora = [b for b in g.abelhas if not b["dentro"]]
        alvo = min(fora, key=lambda b: (b["pos"] - dentro).length())
        alinhada = abs(alvo["pos"].y - g.entrada.centery) < g.entrada.height / 2 - 12 \
            and alvo["pos"].x > g.abrigo.left - 95
        atras = alvo["pos"] + (alvo["pos"] - (dentro if alinhada else frente)).normalize() * 48
        atras.x = max(g.rect.left + 4, min(g.rect.right - 4, atras.x))
        atras.y = max(g.rect.top + 4, min(g.rect.bottom - 4, atras.y))
        passo = atras - cursor
        if passo.length() > 500 * DT:
            passo.scale_to_length(500 * DT)
        cursor += passo
        g.handle_drag((int(cursor.x), int(cursor.y)), True)
        g.update(DT)
    return g


def ganhar_memoria(d, semente):
    random.seed(semente)
    g = JogoDaMemoria(area(), difficulty=d)
    por_simbolo = {}
    for i, c in enumerate(g.cartas):
        por_simbolo.setdefault(c["simbolo"], []).append(i)
    for a, b in por_simbolo.values():
        g.handle_click(g.cartas[a]["area"].center)
        g.handle_click(g.cartas[b]["area"].center)
    return g


def ganhar_soma(d, semente):
    random.seed(semente)
    g = QuebraCabecaDeSoma(area(), difficulty=d)
    while not g.done:
        n = len(g.valores)
        certa = next(c for k in range(1, n + 1) for c in itertools.combinations(range(n), k)
                     if sum(g.valores[i] for i in c) == g.meta)
        avancar(g, 1.0)
        for i in certa:
            g.handle_click(g.areas[i].center)
            avancar(g, 0.3)
        while g.pausa > 0 and not g.done:
            avancar(g, 0.1)
    return g


def clicar_minado(g, x, y):
    g.handle_click((g.origem[0] + x * cm.LADO + 5, g.origem[1] + y * cm.LADO + 5))


def ganhar_minado(d, semente):
    """Sabe onde estão as bombas: clica só nas seguras, 0,2 s por clique."""
    random.seed(semente)
    g = CampoMinado(area(), difficulty=d)
    clicar_minado(g, cm.COLUNAS // 2, cm.LINHAS // 2)
    for y in range(cm.LINHAS):
        for x in range(cm.COLUNAS):
            if not g.mina[y][x] and not g.aberta[y][x] and not g.done:
                clicar_minado(g, x, y)
                avancar(g, 0.2)
    return g


def ganhar_simbolos(d, semente):
    random.seed(semente)
    g = ComunicacaoEmSimbolos(area(), difficulty=d)
    botoes = g._botoes()
    while not g.done:
        while g.fase != "responder" and not g.done:
            avancar(g, 0.05)
        for simbolo in list(g.sequencia):
            if not g.done:
                g.handle_click(botoes[g.paleta.index(simbolo)].center)
                avancar(g, 0.4)
    return g


def ganhar_labirinto(d, semente):
    random.seed(semente)
    g = Labirinto(area(), difficulty=d)
    for celula in g._caminho(g.inicio, g.agua):
        g.handle_click((g.origem[0] + celula[0] * lab.LADO + 20, g.origem[1] + celula[1] * lab.LADO + 20))
        avancar(g, 0.12)
    return g


def resolvivel(esq, dir_, mao):
    if not mao:
        return True
    for i, (a, b) in enumerate(mao):
        resto = mao[:i] + mao[i + 1:]
        if (a == dir_ and resolvivel(esq, b, resto)) or (b == dir_ and resolvivel(esq, a, resto)) \
                or (b == esq and resolvivel(a, dir_, resto)) or (a == esq and resolvivel(b, dir_, resto)):
            return True
    return False


def ganhar_domino(d, semente):
    random.seed(semente)
    g = Domino(area(), difficulty=d)
    while not g.done:
        esq, dir_ = g.pontas()
        for peca in list(g.mao):
            feito = False
            for ponta, girada in g.encaixes(peca).items():
                novas = (esq, girada[1]) if ponta == "dir" else (girada[0], dir_)
                if resolvivel(novas[0], novas[1], [p for p in g.mao if p != peca]):
                    g.handle_click(g._areas_da_mao()[g.mao.index(peca)].center)
                    if g.selecionada is not None:
                        g.handle_click(g._marcadores()[ponta].center)
                    feito = True
                    break
            if feito:
                break
        avancar(g, 1.5)
    return g


def arrastar_peca(g, peca, coluna, linha):
    g.handle_click(peca["casa"].center)
    alvo = (g.tabuleiro.left + coluna * qe.LADO + g.pega[0], g.tabuleiro.top + linha * qe.LADO + g.pega[1])
    g.handle_drag(alvo, True)
    g.handle_release(alvo)


def encaixar(d, semente, quantas=None):
    random.seed(semente)
    g = QuebraCabecaDeEncaixe(area(), difficulty=d)
    for peca in g.pecas[:quantas]:
        arrastar_peca(g, peca, *peca["solucao"])
        avancar(g, 0.5)
    return g


# ============================================================ as verificações
def testar_cada_jogo():
    tela = pygame.display.get_surface()
    print("\n=== 1) cada jogo: criar, desenhar, e o tempo passar sem a jogadora fazer nada ===")
    for classe in rodizio.ORDEM:
        problemas = []
        for d in range(1, 6):
            for relacao in (100, 10, None):
                random.seed(d)
                g = classe(area(), difficulty=d, relacao=relacao)
                g.draw(tela)
                terminar_pelo_tempo(g)
                g.draw(tela)
                if not g.done or g.result not in RESULTADOS:
                    problemas.append((d, relacao, g.done, g.result))
                if g.result == "sucesso":
                    problemas.append((d, relacao, "ficar parado ganhou"))
                if g.effect_multiplier() not in (1.0, 0.5, 0.25):
                    problemas.append((d, relacao, "effect_multiplier"))
        conferir(not problemas, f"{classe.name}: criou/desenhou/terminou em todos os níveis; parado nunca ganha {problemas[:2]}")

    print("\n=== 1b) com a Relação baixa no nível máximo, tudo continua dentro da moldura? ===")
    for relacao in (100, 10):
        for d in range(1, 6):
            random.seed(d)
            moldura = area()
            fora = []
            lb = Labirinto(moldura, difficulty=d, relacao=relacao)
            if not moldura.contains(pygame.Rect(lb.origem, (lb.colunas * lab.LADO, lb.linhas * lab.LADO))):
                fora.append("Labirinto")
            dm = Domino(moldura, difficulty=d, relacao=relacao)
            if dm.total * 64 > moldura.width:
                fora.append("Dominó")
            sm = QuebraCabecaDeSoma(moldura, difficulty=d, relacao=relacao)
            if not all(moldura.contains(a) for a in sm.areas):
                fora.append("Soma")
            en = QuebraCabecaDeEncaixe(moldura, difficulty=d, relacao=relacao)
            if not moldura.contains(en.tabuleiro) or not moldura.contains(en.bandeja):
                fora.append("Encaixe")
            me = JogoDaMemoria(moldura, difficulty=d, relacao=relacao)
            if not all(moldura.contains(c["area"]) for c in me.cartas):
                fora.append("Memória")
            mi = CampoMinado(moldura, difficulty=d, relacao=relacao)
            if not moldura.contains(pygame.Rect(mi.origem, (cm.COLUNAS * cm.LADO, cm.LINHAS * cm.LADO))):
                fora.append("Campo Minado")
            conferir(not fora, f"Relação {relacao:3d}, nível {d}: tudo dentro da moldura {fora}")


def testar_tempos_e_quantidades():
    print("\n=== 2) o tempo e as quantidades de cada jogo (os números que você pediu) ===")
    random.seed(2)
    for d in (1, 4):
        sob = SobAsFolhas(area(), difficulty=d)
        conferir(sob.time_left == 25, f"1 Sob as Folhas, nível {d}: 25 s [só vale depois da mudança à mão] ({sob.time_left})")
    for d in (1, 4):
        conferir(RastroDePolen(area(), difficulty=d).time_left == 8, f"2 Rastro de Pólen, nível {d}: 8 s")
        rv = RotaDeVoo(area(), difficulty=d)
        conferir(rv.time_left == 10 and rv.total_checkpoints == 10, f"3 Rota de Voo, nível {d}: 10 s e números de 1 a 10")
        ap = AntesDaPoda(area(), difficulty=d)
        conferir(ap.time_left == 6 and len(ap.plantas) == 20 and ap.doentes_total == 10,
                 f"4 Antes da Poda, nível {d}: 6 s, 20 plantas, 10 doentes")
        cp = CapturaDeAbelhas(area(), difficulty=d)
        conferir(cp.time_left == 12 and cp.total == 7, f"5 Captura de Abelhas, nível {d}: 12 s e 7 abelhas")
        jm = JogoDaMemoria(area(), difficulty=d)
        conferir(jm.time_left == 35 and len(jm.cartas) == 14, f"6 Memória, nível {d}: 35 s e 14 cartas")
        sm = QuebraCabecaDeSoma(area(), difficulty=d)
        conferir(sm.time_left == 10, f"7 Soma, nível {d}: 10 s")
        cmn = CampoMinado(area(), difficulty=d)
        conferir(cmn.time_left == 10, f"8 Campo Minado, nível {d}: 10 s")
        cs = ComunicacaoEmSimbolos(area(), difficulty=d)
        conferir(cs.time_left == 30, f"9 Decore as ordens, nível {d}: 30 s")
        lb = Labirinto(area(), difficulty=d)
        conferir(lb.time_left == 10, f"10 Labirinto, nível {d}: 10 s")
        dm = Domino(area(), difficulty=d)
        conferir(dm.time_left == 25 and dm.total == 8, f"11 Dominó, nível {d}: 25 s e 8 peças")
        en = QuebraCabecaDeEncaixe(area(), difficulty=d)
        conferir(en.time_left == 40 and len(en.pecas) == 10, f"12 Encaixe, nível {d}: 40 s e 10 peças")


def testar_se_sao_ganhaveis():
    print("\n=== 3) cada jogo é GANHÁVEL, jogando de verdade (e termina na hora quando completa) ===")
    for d in (1, 3, 4):
        for nome, funcao in (("1 Sob as Folhas", ganhar_sob_as_folhas), ("2 Rastro de Pólen", ganhar_polen),
                             ("3 Rota de Voo", ganhar_rota), ("4 Antes da Poda", ganhar_poda),
                             ("6 Memória", ganhar_memoria), ("7 Soma", ganhar_soma),
                             ("8 Campo Minado", ganhar_minado), ("9 Decore as ordens", ganhar_simbolos),
                             ("10 Labirinto", ganhar_labirinto), ("11 Dominó", ganhar_domino),
                             ("12 Encaixe", lambda dd, s: encaixar(dd, s))):
            r = [funcao(d, s) for s in range(6)]
            conferir({g.result for g in r} == {"sucesso"}, f"{nome:20s} nível {d}: 6 de 6 partidas dão sucesso {sorted({g.result for g in r})}")
    for d in (1, 2, 3):
        r = [ganhar_captura(d, s) for s in range(30)]
        suc = sum(g.result == "sucesso" for g in r)
        fal = sum(g.result == "falha" for g in r)
        conferir(suc >= 10 and fal == 0, f"5 Captura de Abelhas nível {d}: pastoreando direito, {suc} de 30 dão sucesso e {fal} falham")
    # termina na hora ao completar
    random.seed(0)
    g = RastroDePolen(area(), difficulty=1)
    for gy in range(g.rows):
        for gx in range(g.cols):
            g.handle_click((g.rect.left + gx * g.cell_size + 3, g.rect.top + gy * g.cell_size + 3))
    conferir(g.done and g.result == "sucesso" and g.time_left > 7.9,
             f"2 Rastro de Pólen: pintou o campo todo (100%) e terminou NA HORA, com {g.time_left:.1f} s sobrando")
    g = ganhar_rota(1, 0)
    conferir(g.result == "sucesso" and g.time_left > 0, f"3 Rota de Voo: completou e terminou com {g.time_left:.1f} s sobrando")
    g = ganhar_poda(1, 0)
    conferir(g.result == "sucesso" and g.time_left > 0, f"4 Antes da Poda: cortou as doentes e terminou com {g.time_left:.1f} s sobrando")
    g = ganhar_memoria(1, 0)
    conferir(g.result == "sucesso" and g.time_left > 30, "6 Memória: achou os 7 pares e terminou na hora")
    g = ganhar_labirinto(1, 0)
    conferir(g.result == "sucesso" and g.time_left > 0, f"10 Labirinto: chegou na água e terminou com {g.time_left:.1f} s sobrando")


def testar_os_limites():
    print("\n=== 4) os resultados nos limites de cada jogo ===")
    # 1 Sob as Folhas: [só vale depois da mudança à mão]
    for tiradas, bichos, esperado in ((10, 0, "falha"), (26, 0, "falha"), (27, 0, "sucesso"), (27, 2, "sucesso"),
                                      (27, 3, "parcial"), (30, 5, "parcial"), (26, 3, "falha")):
        g = resultado(SobAsFolhas)
        g.leaves_left, g.insects_hit = len(g.folhas) - tiradas, bichos
        g._finish()
        conferir(g.result == esperado, f"1 Sob as Folhas: {tiradas} folhas tiradas e {bichos} bichos -> {g.result} (esperado {esperado})")
    # 2 Rastro de Pólen
    for fracao, esperado in ((0.50, "falha"), (0.74, "falha"), (0.75, "parcial"), (0.79, "parcial"), (0.80, "sucesso"), (0.95, "sucesso")):
        g = resultado(RastroDePolen)
        g.covered_count = math.ceil(g.total_cells * fracao)
        g._finish()
        conferir(g.result == esperado, f"2 Rastro de Pólen: {fracao:.0%} coberto -> {g.result} (esperado {esperado})")
    # 3 Rota de Voo
    for numeros, esperado in ((10, "sucesso"), (9, "sucesso"), (8, "parcial"), (7, "parcial"), (6, "falha"), (1, "falha")):
        g = resultado(RotaDeVoo)
        g.next_checkpoint = numeros + 1
        g._finish_por_tempo()
        conferir(g.result == esperado, f"3 Rota de Voo: ligou até o {numeros} -> {g.result} (esperado {esperado})")
    # 4 Antes da Poda: pontos = doentes cortadas - saudaveis cortadas
    for doentes, saudaveis, esperado in ((10, 0, "sucesso"), (9, 0, "sucesso"), (8, 0, "parcial"), (7, 0, "parcial"),
                                         (6, 0, "falha"), (10, 2, "parcial"), (10, 4, "falha")):
        g = resultado(AntesDaPoda)
        sick = [p for p in g.plantas if p.doente][:doentes]
        sound = [p for p in g.plantas if not p.doente][:saudaveis]
        for p in sick + sound:
            g._cortar_em(p.area_do_corte.center)
        g._finish()
        conferir(g.result == esperado, f"4 Antes da Poda: {doentes} doentes e {saudaveis} saudáveis cortadas -> {g.result} (esperado {esperado})")
    # 5 Captura de Abelhas
    for dentro, esperado in ((7, "sucesso"), (6, "sucesso"), (5, "parcial"), (4, "parcial"), (3, "falha"), (0, "falha")):
        g = resultado(CapturaDeAbelhas)
        for i, b in enumerate(g.abelhas):
            b["dentro"] = i < dentro
        g._terminar()
        conferir(g.result == esperado, f"5 Captura de Abelhas: {dentro} dentro -> {g.result} (esperado {esperado})")
    # 6 Memória
    for pares, esperado in ((7, "sucesso"), (6, "sucesso"), (5, "parcial"), (4, "parcial"), (3, "falha"), (0, "falha")):
        g = resultado(JogoDaMemoria)
        g.achados = pares
        g._terminar()
        conferir(g.result == esperado, f"6 Memória: {pares} pares -> {g.result} (esperado {esperado})")
    # 7 Soma
    for fases, esperado in ((3, "sucesso"), (2, "parcial"), (1, "falha"), (0, "falha")):
        g = resultado(QuebraCabecaDeSoma)
        g.resolvidas = fases
        g._terminar()
        conferir(g.result == esperado, f"7 Soma: {fases} contas certas -> {g.result} (esperado {esperado})")
    # 8 Campo Minado: o PIOR entre bombas e cobertura
    for bombas, cobertura, esperado in ((0, 0.90, "sucesso"), (1, 0.85, "sucesso"), (1, 0.80, "sucesso"), (2, 0.90, "parcial"),
                                        (3, 1.00, "falha"), (0, 0.75, "parcial"), (0, 0.70, "parcial"), (0, 0.65, "falha"),
                                        (1, 0.72, "parcial"), (2, 0.72, "parcial"), (2, 0.60, "falha"), (0, 1.0, "sucesso")):
        g = resultado(CampoMinado)
        g.erros, g.reveladas = bombas, math.ceil(g.seguras_total * cobertura)
        g._terminar()
        conferir(g.result == esperado, f"8 Campo Minado: {bombas} bombas e {cobertura:.0%} revelado -> {g.result} (esperado {esperado})")
    # 9 Decore as ordens: 6 rodadas, +1 bloco a cada uma
    for acertos, esperado in ((6, "sucesso"), (5, "sucesso"), (4, "parcial"), (3, "falha"), (0, "falha")):
        g = resultado(ComunicacaoEmSimbolos)
        g.acertos = acertos
        g._terminar()
        conferir(g.result == esperado, f"9 Decore as ordens: {acertos} rodadas certas -> {g.result} (esperado {esperado})")
    random.seed(4)
    g = ComunicacaoEmSimbolos(area(), difficulty=2)
    tamanhos, botoes = [], g._botoes()
    for rodada in range(6):
        while g.fase != "responder":
            avancar(g, 0.05)
        tamanhos.append(len(g.sequencia))
        if rodada % 2 == 0:                                   # acerta
            for s in list(g.sequencia):
                g.handle_click(botoes[g.paleta.index(s)].center)
        else:                                                 # erra o primeiro: a rodada se perde
            errado = next(s for s in g.paleta if s != g.sequencia[0])
            g.handle_click(botoes[g.paleta.index(errado)].center)
        while g.fase == "pausa":
            avancar(g, 0.05)
    conferir(tamanhos == [2, 3, 4, 5, 6, 7], f"9 Decore as ordens: as 6 rodadas têm {tamanhos} blocos")
    conferir(g.done and g.acertos == 3, f"9 Decore as ordens: acertou 3 e errou 3 -> terminou depois da 6ª rodada com {g.acertos} acertos ({g.result})")
    # 10 Labirinto
    g = resultado(Labirinto)
    g.posicao = g.agua
    g._terminar()
    conferir(g.result == "sucesso", "10 Labirinto: chegou na água -> sucesso")
    for fracao, esperado in ((0.95, "parcial"), (0.75, "parcial"), (0.74, "falha"), (0.30, "falha")):
        g = resultado(Labirinto)
        g.melhor_progresso = math.ceil(g.mais_curta * fracao)
        g._terminar()
        conferir(g.result == esperado, f"10 Labirinto: andou {fracao:.0%} do caminho e não chegou -> {g.result} (esperado {esperado})")
    g = resultado(Labirinto)
    caminho = g._caminho(g.inicio, g.agua)
    for celula in caminho[:int(len(caminho) * 0.8)]:
        g.handle_click((g.origem[0] + celula[0] * lab.LADO + 20, g.origem[1] + celula[1] * lab.LADO + 20))
    for celula in caminho[:int(len(caminho) * 0.3)][::-1]:
        g.handle_click((g.origem[0] + celula[0] * lab.LADO + 20, g.origem[1] + celula[1] * lab.LADO + 20))
    avancar(g, 20)
    conferir(g.result == "parcial", f"10 Labirinto: andou 80%, voltou atrás e o tempo acabou -> {g.result} (o que já andou conta)")
    # 11 Dominó: peças na mesa (contando a que já vem)
    for na_mesa, esperado in ((8, "sucesso"), (7, "sucesso"), (6, "parcial"), (5, "parcial"), (4, "falha"), (1, "falha")):
        g = resultado(Domino)
        g.mao = g.mao[:g.total - na_mesa] if na_mesa < g.total else []
        g._terminar()
        conferir(g.result == esperado and g.na_mesa() == na_mesa, f"11 Dominó: {na_mesa} peças na mesa -> {g.result} (esperado {esperado})")
    # 12 Encaixe
    for n, esperado in ((10, "sucesso"), (9, "sucesso"), (8, "parcial"), (7, "parcial"), (6, "falha"), (0, "falha")):
        g = encaixar(3, 5, quantas=n)
        g.update(1000)
        conferir(g.result == esperado, f"12 Encaixe: {n} peças encaixadas -> {g.result} (esperado {esperado})")


def testar_rota_de_voo_desfazer():
    print("\n=== 5) Rota de Voo: desfazer ('dar ré'), sem a tecla R ===")
    random.seed(7)
    g = RotaDeVoo(area(), difficulty=2)
    pt = lambda c: tuple(map(int, g._cell_center(c)))
    sol = g.path_solution
    g.handle_click(pt(sol[0]))
    for c in sol[1:7]:
        g.handle_drag(pt(c), True)
    conferir(len(g.player_path) == 7, "andou 7 células pelo caminho certo")
    g.handle_drag(pt(sol[5]), True)
    conferir(len(g.player_path) == 6 and g.player_path[-1] == sol[5], "arrastou de volta uma célula: só ela foi desfeita (dar ré)")
    g.handle_drag(pt(sol[2]), True)
    conferir(len(g.player_path) == 3 and sol[3] not in g.visited and sol[2] in g.visited,
             "arrastou de volta até a 3ª célula: desfez até ali, e o que veio antes ficou")
    conferir(g.numeros_ligados() == sum(1 for c in sol[:3] if c in g.checkpoint_number_of_cell),
             f"os números ligados voltaram junto ({g.numeros_ligados()})")
    for c in sol[3:8]:
        g.handle_drag(pt(c), True)
    conferir(len(g.player_path) == 8, "depois de desfazer, seguiu pelo caminho de novo")
    g.handle_release(pt(sol[7]))
    g.handle_click(pt(sol[4]))
    conferir(len(g.player_path) == 5 and g.dragging, "clicar numa célula do próprio caminho desfaz até ela e continua dali")
    g.handle_key(pygame.K_r)
    conferir(len(g.player_path) == 5, "a tecla R não reinicia mais")
    conferir("[R]" not in RotaDeVoo.instrucao and "R reinicia" not in RotaDeVoo.instrucao, "o texto da instrução não fala mais da tecla R")
    avancar(g, 11)
    conferir(g.done, "o jogo termina quando os 10 segundos acabam")


def testar_o_rodizio_e_a_ordem():
    print("\n=== 6) o rodízio (12 jogos, instruções que cabem) e a ordem das conselheiras ===")
    j = main.Jogo()
    nomes = [c.name for c in rodizio.ORDEM]
    conferir(len(rodizio.ORDEM) == 12 and len(set(nomes)) == 12, f"o rodízio tem 12 jogos diferentes ({len(set(nomes))} nomes)")
    caixa = layout.retangulo(layout.PREPARO_INSTRUCAO)
    fonte = j.visual.fontes["corpo"]
    passo = fonte.get_height() + 6
    demais = [c.name for c in rodizio.ORDEM
              if len(componentes._linhas(c.instrucao, fonte, caixa.width)) * passo - 6 > caixa.height]
    conferir(not demais, f"a instrução de todos cabe na caixa do preparo {demais}")
    vistos = []
    j = main.Jogo()
    while j.tela != config.FINAL:
        tela = j.tela
        if tela in config.TELAS_QUE_AVANCAM:
            j.avancar_tela()
        elif tela == config.ESCOLHA:
            j.escolher(j.evento["opcoes"][0])
        elif tela == config.PREPARO:
            vistos.append((j.evento["estacao"], j.classe_do_minigame, j.dificuldade))
            j.iniciar_minigame()
            j.minigame.draw(pygame.display.get_surface())
        elif tela == config.MINIGAME:
            j.minigame.done, j.minigame.result = True, "sucesso"
            j.concluir_escolha(1.0)
        elif tela == config.RESULTADO_DO_MINIGAME:
            j.tela = config.CONSEQUENCIA
        elif tela == config.CONSEQUENCIA:
            j.proximo_evento()
    conferir([c for _, c, _ in vistos] == rodizio.ORDEM, "os 12 eventos jogam os 12 jogos, na ordem do rodízio")
    ordem_certa = [ev["id"] for ev in catalogo.EVENTOS if [o["conselheira"] for o in ev["opcoes"]] != list(ORDEM)]
    conferir(not ordem_certa, f"as conselheiras aparecem SEMPRE na mesma ordem {list(ORDEM)} (eventos fora da ordem: {ordem_certa})"
                              f"  [se falhar: falta a mudança no catalogo.py]")


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_mode((config.LARGURA, config.ALTURA))
    testar_cada_jogo()
    testar_tempos_e_quantidades()
    testar_se_sao_ganhaveis()
    testar_os_limites()
    testar_rota_de_voo_desfazer()
    testar_o_rodizio_e_a_ordem()
    print()
    if falhas:
        print(f"{len(falhas)} VERIFICAÇÃO(ÕES) FALHARAM:")
        for f in falhas:
            print("   -", f)
        sys.exit(1)
    print("tudo certo: as regras dos 12 jogos, o rodízio e a ordem das conselheiras passaram em todas as verificações")
