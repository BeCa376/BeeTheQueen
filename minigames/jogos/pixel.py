# -*- coding: utf-8 -*-
"""A PIXEL ART dos minigames: carrega os desenhos de assets/pixel/ e desenha fundos, molduras, cartas e ícones.

Todos os desenhos são em pixel art (a mesma densidade da sua abelha, de 32x32) e são ampliados SEM suavizar, então
os pixels ficam nítidos. Para mudar um desenho, abra o PNG em assets/pixel/ no Aseprite e salve por cima: o jogo
usa a versão nova na próxima vez que abrir. (Os PNGs são feitos por assets/pixel/gerar_pixelart.py, se você quiser
refazer todos.)

O que os jogos usam:
    campo(surface, rect, "grama")       fundo repetido + moldura de madeira POR FORA do rect
    carta(surface, rect, "creme")       uma carta/caixa com borda em relevo e miolo texturizado
    desenhar_icone("flor", ...)         (em icones.py) o ícone com sombra
    colar(surface, imagem, centro=...)  uma imagem com sombra embaixo
    texto(surface, "7", centro, ...)    texto com contorno
    barra(surface, rect, 0.5)           a barra de tempo
"""
import base64
import functools
import os
import zlib

import pygame

from . import aseprite

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PASTA_DOS_DESENHOS = os.path.join(RAIZ, "assets")
PASTA = os.path.join(PASTA_DOS_DESENHOS, "pixel")

ESCALA = 2                      # cada pixel dos desenhos vira ESCALA x ESCALA pixels na tela
LADO_DO_ICONE = 32              # o tamanho dos desenhos dos ícones (o mesmo da abelha)
COR_DO_CONTORNO = (46, 30, 20)

_AVISADOS = set()
_ALIAS = {"favo": "colmeia", "escudo": "bandeira", "ovo": "animal"}      # nomes antigos dos ícones


# ---------------------------------------------------------------------------- carregar
_AVISOU_DA_PASTA = []


def _do_codigo(nome):
    """O desenho `nome` guardado dentro do código (pixel_dados.py), ou None se não houver."""
    try:
        from . import pixel_dados
        largura, altura, texto = pixel_dados.DESENHOS[nome]
        dados = zlib.decompress(base64.b64decode(texto))
        return pygame.image.frombuffer(dados, (largura, altura), "RGBA").copy().convert_alpha()
    except Exception:                      # (sem o arquivo de dados, ou sem esse desenho)
        return None


@functools.lru_cache(maxsize=None)
def _carregar(nome):
    """O desenho como está no PNG de assets/pixel/ (assim você pode retocar no Aseprite). Se o PNG não existir ou
    não carregar, usa a cópia que vem dentro do código, então o visual é o mesmo. Só se nem isso existir,
    um quadriculado rosa avisa."""
    caminho = os.path.join(PASTA, nome + ".png")
    try:
        return pygame.image.load(caminho).convert_alpha()
    except (pygame.error, FileNotFoundError, OSError):
        pass
    embutido = _do_codigo(nome)
    if embutido is not None:
        if not _AVISOU_DA_PASTA:
            _AVISOU_DA_PASTA.append(True)
            print(f"AVISO: não achei (ou não consegui ler) os desenhos em {PASTA}. O jogo está usando a cópia que vai "
                  f"dentro do código, então o visual é o mesmo. Para poder retocar os desenhos, copie a pasta assets/pixel/ "
                  f"do zip para essa pasta.")
        return embutido
    if nome not in _AVISADOS:
        _AVISADOS.add(nome)
        print(f"AVISO: não achei o desenho {nome} (nem em {caminho}, nem dentro do código); usando um quadriculado.")
    quadro = pygame.Surface((32, 32), pygame.SRCALPHA)
    for y in range(0, 32, 8):
        for x in range(0, 32, 8):
            quadro.fill((255, 0, 200) if (x + y) // 8 % 2 else (60, 20, 60), (x, y, 8, 8))
    return quadro


@functools.lru_cache(maxsize=None)
def imagem(nome, fator=ESCALA):
    """O desenho `nome` ampliado `fator` vezes, sem suavizar."""
    img = _carregar(nome)
    if fator == 1:
        return img
    return pygame.transform.scale(img, (img.get_width() * fator, img.get_height() * fator))


def tingir(img, cor):
    """Uma cópia da imagem multiplicada por `cor` (o branco vira a cor; o cinza vira uma versão mais escura)."""
    nova = img.copy()
    nova.fill(tuple(cor) + (255,), special_flags=pygame.BLEND_RGBA_MULT)
    return nova


# ---------------------------------------------------------------------------- sombra e colagem
_SOMBRAS = {}


def sombra_de(img, alfa=80):
    chave = (id(img), alfa)
    if chave not in _SOMBRAS:
        mascara = pygame.mask.from_surface(img, 40)
        _SOMBRAS[chave] = (mascara.to_surface(setcolor=(20, 12, 4, alfa), unsetcolor=(0, 0, 0, 0)), img)
    return _SOMBRAS[chave][0]


def colar(surface, img, centro=None, canto=None, sombra=True, deslocamento=(2, 3)):
    """Cola a imagem (centrada em `centro`, ou com o canto de cima à esquerda em `canto`), com a sombra embaixo."""
    ret = img.get_rect()
    if centro is not None:
        ret.center = (int(centro[0]), int(centro[1]))
    else:
        ret.topleft = (int(canto[0]), int(canto[1]))
    if sombra:
        surface.blit(sombra_de(img), ret.move(deslocamento))
    surface.blit(img, ret)
    return ret


# ---------------------------------------------------------------------------- os ícones
@functools.lru_cache(maxsize=None)
def _desenho_do_aseprite(arquivo):
    return aseprite.carregar(os.path.join(PASTA_DOS_DESENHOS, arquivo)).recortada().quadros[0]


def _ajustada(img, lado):
    """A imagem encolhida/ampliada para caber num quadrado de `lado` pixels (mantendo a proporção)."""
    razao = lado / max(img.get_size())
    return pygame.transform.smoothscale(img, (max(1, round(img.get_width() * razao)), max(1, round(img.get_height() * razao))))


@functools.lru_cache(maxsize=None)
def icone(nome, tamanho):
    """O ícone `nome` cabendo (aproximadamente) num quadrado de `tamanho` pixels. Os desenhos têm 32x32: de 28 pixels
    para cima eles são ampliados em números inteiros (32, 64...), sem suavizar; menores que isso, são encolhidos."""
    nome = _ALIAS.get(nome, nome)
    tamanho = int(tamanho)
    if nome == "folha":
        return _ajustada(_desenho_do_aseprite("Folha.ase"), max(12, tamanho))
    if nome == "animal":
        return _ajustada(_desenho_do_aseprite("Joaninha.ase"), max(12, tamanho))
    if nome == "abelha":
        base = pygame.image.load(os.path.join(PASTA_DOS_DESENHOS, "bee_frame_0.png")).convert_alpha()
    else:
        base = _carregar("pote_de_mel" if nome == "pote" else nome)
    if tamanho < 28:
        return _ajustada(base, max(8, tamanho))
    fator = max(1, int(tamanho / LADO_DO_ICONE + 0.45))
    return base if fator == 1 else pygame.transform.scale(base, (base.get_width() * fator, base.get_height() * fator))


# ---------------------------------------------------------------------------- as abelhas animadas
@functools.lru_cache(maxsize=None)
def quadros_da_abelha(fator=1):
    quadros = []
    for i in range(9):
        q = pygame.image.load(os.path.join(PASTA_DOS_DESENHOS, f"bee_frame_{i}.png")).convert_alpha()
        quadros.append(q if fator == 1 else pygame.transform.scale(q, (q.get_width() * fator, q.get_height() * fator)))
    return quadros


@functools.lru_cache(maxsize=None)
def _abelha_virada(fator, indice):
    return pygame.transform.flip(quadros_da_abelha(fator)[indice], True, False)


def abelha(tempo, fator=1, para_a_esquerda=False, fase=0.0):
    """O quadro da abelha batendo as asas no instante `tempo` (segundos); `fase` desencontra as abelhas."""
    indice = int((tempo + fase) * 14) % 9
    return _abelha_virada(fator, indice) if para_a_esquerda else quadros_da_abelha(fator)[indice]


# ---------------------------------------------------------------------------- fundos repetidos
@functools.lru_cache(maxsize=64)
def fundo_pronto(nome, largura, altura, escala=ESCALA, tinta=None):
    """Uma imagem de `largura` x `altura` coberta com o fundo `nome` repetido (e tingida, se houver `tinta`)."""
    tile = imagem("fundo_" + nome, escala)
    if tinta:
        tile = tingir(tile, tinta)
    tela = pygame.Surface((largura, altura))
    for y in range(0, altura, tile.get_height()):
        for x in range(0, largura, tile.get_width()):
            tela.blit(tile, (x, y))
    return tela


@functools.lru_cache(maxsize=32)
def _vinheta(largura, altura):
    """Um escurecido leve nas bordas (dá a sensação de profundidade, como a luz do dia sobre o campo)."""
    folha = pygame.Surface((largura, altura), pygame.SRCALPHA)
    for i in range(7):
        alfa = int(64 * (1 - i / 7) ** 1.5)
        pygame.draw.rect(folha, (10, 20, 10, alfa), pygame.Rect(0, 0, largura, altura).inflate(-2 * i * 2, -2 * i * 2), 4)
    return folha


@functools.lru_cache(maxsize=64)
def nove_fatias(nome, largura, altura, b, escala=ESCALA):
    """Uma moldura de `largura` x `altura` feita com o desenho `nome` (as bordas esticam, os cantos não)."""
    src = _carregar(nome)
    lado = src.get_width()
    bw = b * escala
    meio = lado - 2 * b
    saida = pygame.Surface((largura, altura), pygame.SRCALPHA)

    def parte(x, y, w, h, tw, th):
        return pygame.transform.scale(src.subsurface((x, y, w, h)), (max(1, tw), max(1, th)))

    saida.blit(parte(0, 0, b, b, bw, bw), (0, 0))
    saida.blit(parte(lado - b, 0, b, b, bw, bw), (largura - bw, 0))
    saida.blit(parte(0, lado - b, b, b, bw, bw), (0, altura - bw))
    saida.blit(parte(lado - b, lado - b, b, b, bw, bw), (largura - bw, altura - bw))
    saida.blit(parte(b, 0, meio, b, largura - 2 * bw, bw), (bw, 0))
    saida.blit(parte(b, lado - b, meio, b, largura - 2 * bw, bw), (bw, altura - bw))
    saida.blit(parte(0, b, b, meio, bw, altura - 2 * bw), (0, bw))
    saida.blit(parte(lado - b, b, b, meio, bw, altura - 2 * bw), (largura - bw, bw))
    return saida


# ---------------------------------------------------------------------------- o campo do minigame
LARGURA_DA_MOLDURA = 4 * ESCALA


def campo(surface, rect, fundo="grama", tinta=None, vinheta=True):
    """O campo de um minigame: o fundo repetido dentro do `rect` e a moldura de madeira POR FORA dele
    (o rect inteiro continua sendo área de jogo). Com vinheta=False, chame vinheta(surface, rect) DEPOIS de
    desenhar o que fica em cima do fundo."""
    surface.blit(fundo_pronto(fundo, rect.width, rect.height, ESCALA, tinta), rect.topleft)
    if vinheta:
        surface.blit(_vinheta(rect.width, rect.height), rect.topleft)
    moldura = rect.inflate(2 * LARGURA_DA_MOLDURA, 2 * LARGURA_DA_MOLDURA)
    surface.blit(nove_fatias("borda_campo", moldura.width, moldura.height, 4), moldura.topleft)


def vinheta(surface, rect):
    """O escurecido leve das bordas do campo, por cima de tudo o que já foi desenhado nele."""
    surface.blit(_vinheta(rect.width, rect.height), rect.topleft)


# ---------------------------------------------------------------------------- cartas, placas e caixas
# estilo -> (borda, fundo do miolo, tinta do miolo)
ESTILOS = {
    "creme": ("borda_carta_creme", "pergaminho", None),
    "ambar": ("borda_carta_ambar", "favo", None),
    "verde": ("borda_carta_verde", "pergaminho", (196, 236, 188)),
    "osso": ("borda_carta_osso", "osso", None),
    "madeira": ("borda_placa_madeira", "madeira", None),
    "funda": ("borda_caixa_funda", "areia", (206, 192, 156)),
    "cinza": ("borda_carta_osso", "osso", (214, 214, 220)),
}


def carta(surface, rect, estilo="creme", destaque=None):
    """Desenha uma carta/placa/caixa: miolo texturizado e borda em relevo. `destaque` (uma cor) põe um brilho em volta."""
    borda, fundo, tinta = ESTILOS[estilo]
    rect = pygame.Rect(rect)
    if destaque:
        brilho = pygame.Surface((rect.width + 12, rect.height + 12), pygame.SRCALPHA)
        for i in range(6):
            pygame.draw.rect(brilho, tuple(destaque) + (46,), pygame.Rect(0, 0, rect.width + 12, rect.height + 12).inflate(-2 * i, -2 * i),
                             border_radius=6)
        surface.blit(brilho, (rect.left - 6, rect.top - 6))
    miolo = rect.inflate(-2 * ESCALA, -2 * ESCALA)
    surface.blit(fundo_pronto(fundo, miolo.width, miolo.height, ESCALA, tinta), miolo.topleft)
    surface.blit(nove_fatias(borda, rect.width, rect.height, 3), rect.topleft)


# ---------------------------------------------------------------------------- texto e barra
@functools.lru_cache(maxsize=None)
def _fonte(tamanho, negrito):
    return pygame.font.SysFont("verdana", tamanho, bold=negrito)


def texto(surface, conteudo, centro, tamanho=18, cor=(255, 255, 255), contorno=COR_DO_CONTORNO, negrito=True):
    """Texto com contorno de 2 pixels (legível sobre qualquer fundo). O `centro` é o centro do texto."""
    fonte = _fonte(tamanho, negrito)
    miolo = fonte.render(str(conteudo), True, cor)
    borda = fonte.render(str(conteudo), True, contorno)
    ret = miolo.get_rect(center=(int(centro[0]), int(centro[1])))
    for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 3)):
        surface.blit(borda, ret.move(dx, dy))
    surface.blit(miolo, ret)
    return ret


def barra(surface, rect, fracao, cor=None):
    """A barra de progresso/tempo em pixel art: trilho fundo de madeira e mel brilhante que vai enchendo."""
    rect = pygame.Rect(rect)
    fracao = max(0.0, min(1.0, fracao))
    pygame.draw.rect(surface, (46, 30, 20), rect)
    trilho = rect.inflate(-4, -4)
    pygame.draw.rect(surface, (96, 66, 40), trilho)
    pygame.draw.line(surface, (60, 40, 24), trilho.topleft, (trilho.right - 1, trilho.top), 2)
    cheio = int(trilho.width * fracao)
    if cheio > 0:
        principal, luz, sombra = cor or ((240, 170, 40), (255, 226, 120), (196, 116, 18))
        faixa = pygame.Rect(trilho.left, trilho.top, cheio, trilho.height)
        pygame.draw.rect(surface, principal, faixa)
        pygame.draw.rect(surface, luz, (faixa.left, faixa.top, faixa.width, max(1, faixa.height // 3)))
        pygame.draw.rect(surface, sombra, (faixa.left, faixa.bottom - max(1, faixa.height // 3), faixa.width, max(1, faixa.height // 3)))
        for x in range(faixa.left + 12, faixa.right - 2, 12):
            pygame.draw.line(surface, sombra, (x, faixa.top), (x, faixa.bottom - 1), 1)
        pygame.draw.line(surface, (255, 246, 200), (faixa.right - 1, faixa.top), (faixa.right - 1, faixa.bottom - 1), 1)
    pygame.draw.rect(surface, (46, 30, 20), rect, 2)
