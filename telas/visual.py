# -*- coding: utf-8 -*-
"""
O VISUAL: a janela, as fontes e as imagens que todas as telas usam.
(As fontes se ajustam em config.py; as imagens estão em assets/.)
"""
import os
import pygame

import config
from data.councilors import CONSELHEIRAS
from telas import layout

PASTA_DE_IMAGENS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")


class Visual:
    def __init__(self):
        pygame.init()
        # o ícone da janela e da barra de tarefas: a abelhinha (assets/icone.png)
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
        self.tela = pygame.display.set_mode((config.LARGURA, config.ALTURA))
        self.relogio = pygame.time.Clock()
        # usados pelos cards de escrita (veja componentes.card_de_texto): quando
        # `medindo`, o texto não é desenhado, só medido (em `tinta`); depois ele é
        # desenhado já deslocado em `deslocamento_y`
        self.medindo = False
        self.tinta = None
        self.deslocamento_y = 0

        self.fontes = {nome: pygame.font.SysFont(familia, tamanho, bold=negrito)
                       for nome, (familia, tamanho, negrito) in config.FONTES.items()}

        fundo = pygame.image.load(os.path.join(PASTA_DE_IMAGENS, "bg_scene.png")).convert()
        self.fundo = pygame.transform.scale(fundo, (config.LARGURA, config.ALTURA))
        self.seta_esquerda = self._carregar_seta("seta_esquerda.png")
        self.seta_direita = self._carregar_seta("seta_direita.png")
        self.seta_do_menu = self._carregar_seta("seta_esquerda.png", layout.SETA_DO_MENU_LARGURA)
        self.seta_apertada = None
        self.tempo_das_setas = 0.0
        self._setas_com_borda = {}       # cada seta já com a borda pronta (para quando o mouse está em cima)
        self.area_da_seta_do_card = None

        self.quadros_da_abelha = []
        for i in range(9):
            imagem = pygame.image.load(os.path.join(PASTA_DE_IMAGENS, f"bee_frame_{i}.png")).convert_alpha()
            self.quadros_da_abelha.append(pygame.transform.scale(imagem, (96, 96)))
        self.quadro_atual = 0
        self._tempo_do_quadro = 0.0

        # um emoji por conselheira (imagem: o pygame não desenha emoji de fonte)
        self.emojis = {}
        for nome, dados in CONSELHEIRAS.items():
            caminho = os.path.join(PASTA_DE_IMAGENS, "emoji", dados["arquivo_emoji"])
            if os.path.isfile(caminho):
                imagem = pygame.image.load(caminho).convert_alpha()
                self.emojis[nome] = pygame.transform.smoothscale(
                    imagem, (config.EMOJI_TAMANHO, config.EMOJI_TAMANHO))

    def atualizar(self, dt):
        self._tempo_do_quadro += dt
        if self._tempo_do_quadro >= config.ABELHA_SEGUNDOS_POR_QUADRO:
            self._tempo_do_quadro = 0.0
            self.quadro_atual = (self.quadro_atual + 1) % len(self.quadros_da_abelha)

    def _carregar_seta(self, nome, largura=None):
        largura = largura or layout.SETA_LARGURA
        imagem = pygame.image.load(os.path.join(PASTA_DE_IMAGENS, nome)).convert_alpha()
        altura = round(imagem.get_height() * largura / imagem.get_width())
        return pygame.transform.scale(imagem, (largura, altura))

    def retangulo_da_seta(self, qual):
        if qual == "esquerda":
            return self.seta_esquerda.get_rect(center=layout.SETA_ESQUERDA_CENTRO)
        return self.seta_direita.get_rect(center=layout.SETA_DIREITA_CENTRO)

    def _com_borda(self, imagem):
        """A seta com uma borda ao redor (cor e espessura em layout.py). Fica guardada."""
        if id(imagem) not in self._setas_com_borda:
            e = layout.SETA_BORDA_ESPESSURA
            silhueta = pygame.mask.from_surface(imagem).to_surface(setcolor=layout.SETA_BORDA_COR,
                                                                   unsetcolor=(0, 0, 0, 0))
            pronta = pygame.Surface((imagem.get_width() + 2 * e, imagem.get_height() + 2 * e), pygame.SRCALPHA)
            for dx in range(-e, e + 1):
                for dy in range(-e, e + 1):
                    if dx * dx + dy * dy <= e * e + 1:
                        pronta.blit(silhueta, (e + dx, e + dy))
            pronta.blit(imagem, (e, e))
            self._setas_com_borda[id(imagem)] = pronta
        return self._setas_com_borda[id(imagem)]

    def _desenhar_seta(self, imagem, area, qual, zona=None):
        """Desenha uma seta: com o mouse em cima (`zona`, onde o clique vale) ela ganha uma borda;
        no clique (`seta_apertada`) ela encolhe um pouquinho (layout.SETA_ENCOLHE_NO_CLIQUE)."""
        em_cima = (zona or area).collidepoint(pygame.mouse.get_pos())
        apertada = self.seta_apertada == qual
        figura = self._com_borda(imagem) if (em_cima or apertada) else imagem
        if apertada:
            figura = pygame.transform.scale(figura, (round(figura.get_width() * layout.SETA_ENCOLHE_NO_CLIQUE),
                                                     round(figura.get_height() * layout.SETA_ENCOLHE_NO_CLIQUE)))
        self.tela.blit(figura, figura.get_rect(center=area.center))

    def setas(self, voltar=True):
        self._desenhar_seta(self.seta_direita, self.retangulo_da_seta("direita"), "direita")
        if voltar:
            self._desenhar_seta(self.seta_esquerda, self.retangulo_da_seta("esquerda"), "esquerda")

    def retangulo_da_seta_do_menu(self):
        return self.seta_do_menu.get_rect(center=layout.SETA_DO_MENU_CENTRO)

    def seta_do_menu_foi_clicada(self, mouse):
        area = self.retangulo_da_seta_do_menu().inflate(layout.SETA_DO_MENU_FOLGA, layout.SETA_DO_MENU_FOLGA)
        return area.collidepoint(mouse)

    def seta_do_card(self, card):
        centro = (card.right - layout.SETA_DO_CARD_DA_DIREITA, card.bottom - layout.SETA_DO_CARD_DA_BASE)
        self.area_da_seta_do_card = self.seta_direita.get_rect(center=centro)
        self._desenhar_seta(self.seta_direita, self.area_da_seta_do_card, "card")

    def desenhar_seta_do_menu(self):
        area = self.retangulo_da_seta_do_menu()
        zona = area.inflate(layout.SETA_DO_MENU_FOLGA, layout.SETA_DO_MENU_FOLGA)
        self._desenhar_seta(self.seta_do_menu, area, "menu", zona)

    def abelha(self, posicao):
        self.tela.blit(self.quadros_da_abelha[self.quadro_atual], posicao)

    def desenhar_fundo(self):
        """O fundo, com um véu claro por cima (igual em todas as telas)."""
        self.tela.blit(self.fundo, (0, 0))
        veu = pygame.Surface((config.LARGURA, config.ALTURA), pygame.SRCALPHA)
        veu.fill(layout.VEU_BRANCO)
        self.tela.blit(veu, (0, 0))
