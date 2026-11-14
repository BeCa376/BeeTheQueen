# -*- coding: utf-8 -*-
"""
Bee the Queen

ESTE ARQUIVO É SÓ O ORQUESTRADOR: decide a ORDEM das coisas. Para cada
evento ele faz, em sequência:

    1. puxa o EVENTO         eventos/eNN_*.py     e mostra o texto e as 4 opções
    2. puxa o MINIGAME       minigames/eNN_*.py   do que a jogadora escolheu
    3. puxa o RESULTADO      resultados/eNN_*.py  efeitos, consequência e o que
                                                  muda no próximo evento
    4. volta ao passo 1 com o próximo evento

Ele não calcula número nenhum e não desenha nada: chama quem faz isso.

QUEM FAZ O QUE
    main.py          orquestrador: a ordem das telas, as teclas, o laço do jogo
    config.py        todos os números e ajustes (equilíbrio, tempos, fontes)
    regras.py        as regras: custo, efeitos, penalidade, a ponte entre eventos
    catalogo.py      a lista de eventos (carrega os 3 arquivos de cada um)
    eventos/         a SITUAÇÃO: texto, 4 opções, preço
    minigames/       qual JOGO cada conselheira joga em cada evento
      jogos/         o código de cada jogo
    resultados/      o que ACONTECE: efeitos, consequência, o que muda no próximo
    introducao/      os textos da abertura, das conselheiras e da Nova Rainha
    data/            conselheiras, eixos da Harmonia, perfis finais
    telas/           tudo que aparece na tela (layout.py = posições,
                     textos.py = textos fixos, o resto = uma tela por função)

ONDE MEXER
    texto ou preço de uma opção                 eventos/eNN_*.py
    qual jogo uma conselheira joga              minigames/eNN_*.py
    efeitos, consequência, ponte p/ o próximo   resultados/eNN_*.py
    um número do jogo (mel inicial, bônus...)   config.py
    tempo das telas, letras                     config.py
    posição/cor de algo na tela                 telas/layout.py
    texto fixo de uma tela                      telas/textos.py
    ordem das telas / o que uma tecla faz       este arquivo
    adicionar um evento                         os 3 arquivos + catalogo.py

Como rodar:
    pip install -r requirements.txt
    python main.py
"""
import copy
import sys

import pygame

import catalogo
import config
import regras
from data.councilors import ORDEM
from minigames import rodizio
from telas import confirmacao, desenho, layout, popup
from telas.visual import Visual


# As telas do JOGO (o que vem depois da introdução). Nelas a tela nunca passa sozinha, e o
TELAS_DO_JOGO = (config.CONTEXTO, config.PREPARO, config.MINIGAME,
                 config.RESULTADO_DO_MINIGAME, config.CONSEQUENCIA)


class Jogo:

    def __init__(self):
        config.verificar()
        catalogo.verificar()
        self.visual = Visual()           # janela, fontes, imagens (telas/visual.py)
        self._zerar_partida()
        self.tela = config.ABERTURA
        self.acao_da_seta = None
        self.tempo_da_seta = 0.0

    def _zerar_partida(self):
        self.estado = regras.Estado()    # os números do jogo      (regras.py)

        # --- onde o jogo está: só o orquestrador mexe nisto ---
        self.indice_do_evento = 0
        self.estacao_atual = None
        self.indice_conselheira = 0
        self.opcao = None                # a opção que a jogadora escolheu
        self.classe_do_minigame = None
        self.minigame = None             # o jogo em andamento
        self.teve_minigame = False       # a escolha tinha minigame? (ação direta = não)
        self.nome_do_minigame = ""
        self.instrucao_do_minigame = ""
        self.dificuldade = 1
        self.minigames_jogados = 0       # quantos já saíram do rodízio (minigames/rodizio.py)
        self.tempo_de_preparo = config.TEMPO_DE_PREPARO_DO_MINIGAME
        self.resolucao = None            # o que a escolha produziu (regras.resolver)
        self.tempo_da_tela = 0.0         # há quantos segundos esta tela está aí
        self._chave_da_tela = None
        self.confirmando_saida = False   # o popup "Voltar ao menu?" está aberto? (telas/confirmacao.py)
        self.aguardando_inicio = False   # o popup "Iniciar" está aberto? (telas/popup.py)
        self.tentativas_feitas = 0       # quantas vezes ela já usou o "Tentar de novo" neste jogo
        self._estado_antes_do_resultado = None   # as moedas de antes do resultado (para desfazer)

    # ---------------------------------------------------------- o que as telas leem
    @property
    def evento(self):
        return catalogo.EVENTOS[self.indice_do_evento]

    @property
    def dica_visivel(self):
        """Já passou o tempo de espera? (a dica "Pressione ENTER..." só aparece depois).
        Nas telas do jogo a espera é o ATRASO_DA_DICA_NO_JOGO; na introdução, o ATRASO_DA_DICA."""
        if self.tela in TELAS_DO_JOGO:
            atraso = config.ATRASO_DA_DICA_NO_JOGO
        else:
            atraso = config.ATRASO_DA_DICA
        return self.tempo_da_tela >= atraso

    def texto_de_abertura(self):
        """O texto de abertura do evento (pode vir trocado pela ponte do anterior)."""
        return regras.texto_de_abertura(self.evento, self.estado)

    def segundos_ate_avancar(self):
        return config.AVANCO_AUTOMATICO.get(self.tela)

    # ============================================================
    # A ORDEM DAS TELAS
    # ============================================================
    def avancar_tela(self):
        """Passa para a próxima tela de apresentação. É o que o ENTER faz e
        também o que acontece sozinho quando o tempo da tela acaba (veja
        AVANCO_AUTOMATICO em config.py)."""
        if self.tela == config.ABERTURA:
            self.tela = config.CONSELHEIRA
            self.indice_conselheira = 0
        elif self.tela == config.CONSELHEIRA:
            if self.indice_conselheira < len(ORDEM) - 1:
                self.indice_conselheira += 1
            else:
                self.tela = config.NOVA_RAINHA
        elif self.tela == config.NOVA_RAINHA:
            self.iniciar_evento()
        elif self.tela == config.ESTACAO:
            self.tela = config.CONTEXTO
        elif self.tela == config.CONTEXTO:
            self.tela = config.ESCOLHA

    def voltar_tela(self):
        if self.tela == config.CONSELHEIRA:
            if self.indice_conselheira > 0:
                self.indice_conselheira -= 1
            else:
                self.tela = config.ABERTURA
        elif self.tela == config.NOVA_RAINHA:
            self.tela = config.CONSELHEIRA
            self.indice_conselheira = len(ORDEM) - 1

    def continuar(self):
        if self.tela == config.PREPARO:
            self.iniciar_minigame()
        elif self.tela == config.RESULTADO_DO_MINIGAME:
            self.proximo_evento()
        elif self.tela == config.CONSEQUENCIA:
            self.proximo_evento()
        else:
            self.avancar_tela()

    def apertar_seta(self, qual, acao):
        if self.acao_da_seta is None:
            self.acao_da_seta = (acao, (self.tela, self.indice_conselheira))
            self.tempo_da_seta = 0.0
            self.visual.seta_apertada = qual

    def andar_o_clique_da_seta(self, dt):
        if self.acao_da_seta is None:
            return
        self.tempo_da_seta += dt
        if self.tempo_da_seta >= config.SEGUNDOS_DO_CLIQUE_DA_SETA:
            acao, onde_estava = self.acao_da_seta
            self.acao_da_seta = None
            self.visual.seta_apertada = None
            if (self.tela, self.indice_conselheira) == onde_estava:
                acao()

    def iniciar_evento(self):
        """1. O EVENTO: mostra o cartão da estação (se mudou) e o texto."""
        if self.evento["estacao"] != self.estacao_atual:
            self.estacao_atual = self.evento["estacao"]
            self.tela = config.ESTACAO
        else:
            self.tela = config.CONTEXTO

    def escolher(self, opcao):
        """2. O MINIGAME: a jogadora escolheu uma opção. Com minigame, vai para
        o preparo; sem minigame (ação direta), resolve na hora.
        Com o rodízio ligado (config.MINIGAMES_EM_RODIZIO), toda decisão tem
        minigame: o próximo da ordem 1-2-3-4, cada volta mais difícil."""
        self.opcao = opcao
        self.tentativas_feitas = 0
        evento = self.evento
        if config.MINIGAMES_EM_RODIZIO:
            self.escolher_no_rodizio()
            return
        classe = catalogo.JOGOS[evento["id"]][opcao["conselheira"]]
        self.classe_do_minigame = classe
        self.teve_minigame = classe is not None
        self.minigame = None
        if classe is None:
            self.concluir_escolha(1.0)
            return
        self.nome_do_minigame = classe.name
        self.instrucao_do_minigame = classe.instrucao
        self.dificuldade = (catalogo.DIFICULDADES[evento["id"]]
                            or config.DIFICULDADE_POR_ESTACAO.get(evento["estacao"], 1))
        self.tempo_de_preparo = config.TEMPO_DE_PREPARO_DO_MINIGAME
        self.tela = config.PREPARO

    def escolher_no_rodizio(self):
        """O próximo jogo do rodízio, na ordem de minigames/rodizio.py. Com um jogo para cada
        evento a dificuldade é a da estação; com menos jogos que eventos, a lista recomeça do
        1 e cada volta é mais difícil."""
        posicao = self.minigames_jogados % len(rodizio.ORDEM)
        volta = self.minigames_jogados // len(rodizio.ORDEM)
        self.minigames_jogados += 1
        classe = rodizio.ORDEM[posicao]
        self.classe_do_minigame = classe
        self.teve_minigame = True
        self.minigame = None
        self.nome_do_minigame = classe.name
        self.instrucao_do_minigame = classe.instrucao
        if len(rodizio.ORDEM) >= len(catalogo.EVENTOS):
            self.dificuldade = config.DIFICULDADE_POR_ESTACAO.get(self.evento["estacao"], 1)
        else:
            voltas = config.DIFICULDADE_POR_VOLTA
            self.dificuldade = voltas[min(volta, len(voltas) - 1)]
        self.tempo_de_preparo = config.TEMPO_DE_PREPARO_DO_MINIGAME
        self.tela = config.PREPARO

    def iniciar_minigame(self):
        """Acabou o preparo: cria o minigame e começa."""
        self.minigame = self.classe_do_minigame(
            layout.area_do_minigame(), difficulty=self.dificuldade, relacao=self.estado.relacao)
        self.tela = config.MINIGAME
        self.aguardando_inicio = True      # o jogo espera o clique em "Iniciar" (telas/popup.py)

    def concluir_escolha(self, multiplicador):
        self.aguardando_inicio = False                                  # (o minigame acabou: sem popup)
        self._estado_antes_do_resultado = copy.deepcopy(self.estado)    # (para o "Tentar de novo" poder desfazer)
        self.resolucao = regras.resolver(self.estado, self.evento, self.opcao, multiplicador)
        self.tela = config.RESULTADO_DO_MINIGAME

    def proximo_evento(self):
        """4. Próximo evento (ou a tela final, se acabaram)."""
        self.indice_do_evento += 1
        if self.indice_do_evento >= len(catalogo.EVENTOS):
            self.tela = config.FINAL
        else:
            self.iniciar_evento()

    def jogar_de_novo(self):
        """O botão da tela final: partida nova, do começo (a abertura)."""
        self._zerar_partida()
        self.tela = config.ABERTURA

    # ============================================================
    # O POPUP "VOLTAR AO MENU INICIAL?"   (quem desenha é telas/confirmacao.py)
    # ============================================================
    def pedir_confirmacao_de_saida(self):
        """A seta do menu foi clicada: abre o popup. Enquanto ele estiver aberto, o jogo fica parado."""
        if self.tela == config.MINIGAME and self.minigame is not None and not self.minigame.done:
            self.minigame.handle_release(pygame.mouse.get_pos())      # solta o traço, se estava arrastando
        self.confirmando_saida = True

    def tratar_confirmacao_de_saida(self, evento):
        """Com o popup aberto, só os dois botões (e o ESC) fazem alguma coisa."""
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self.confirmando_saida = False                             # ESC = Cancelar
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            botao = confirmacao.botao_em(evento.pos)
            if botao == "ok":
                self.confirmando_saida = False
                self.jogar_de_novo()                                   # volta ao menu inicial (e zera a partida)
            elif botao == "cancelar":
                self.confirmando_saida = False                         # continua de onde estava

    # ============================================================
    # O POPUP "INICIAR" E O "TENTAR DE NOVO"   (quem desenha é telas/popup.py)
    # ============================================================
    def tratar_inicio_do_minigame(self, evento):
        """Com o popup "Iniciar" aberto, só o botão (ou o ENTER) faz alguma coisa: o tempo começa a contar."""
        enter = evento.type == pygame.KEYDOWN and evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER)
        clicou = (evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1
                  and popup.botao_em(evento.pos, popup.BOTOES_DO_INICIO) == "iniciar")
        if enter or clicou:
            self.aguardando_inicio = False

    def pode_tentar_de_novo(self):
        """Dá para tentar este minigame outra vez? (deu falha ou parcial, e ainda há tentativas)"""
        limite = popup.NOVAS_TENTATIVAS_POR_JOGO
        return (self.tela == config.RESULTADO_DO_MINIGAME and self.minigame is not None
                and self.minigame.result in ("falha", "parcial")
                and self._estado_antes_do_resultado is not None
                and (limite is None or self.tentativas_feitas < limite))

    def tentativas_restantes(self):
        """Quantas novas tentativas ainda restam (None = sem limite)."""
        limite = popup.NOVAS_TENTATIVAS_POR_JOGO
        return None if limite is None else max(0, limite - self.tentativas_feitas)

    def tentar_de_novo(self):
        """Desfaz o resultado desta tentativa (as moedas voltam ao que eram) e começa o MESMO minigame outra vez."""
        if not self.pode_tentar_de_novo():
            return
        self.estado = copy.deepcopy(self._estado_antes_do_resultado)
        self.tentativas_feitas += 1
        self.iniciar_minigame()                        # (de novo com o popup "Iniciar")

    # ============================================================
    # TECLADO E MOUSE
    # ============================================================
    def tratar_evento(self, evento, mouse):
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if self.confirmando_saida:         # popup aberto: só ele recebe o mouse e o teclado
            self.tratar_confirmacao_de_saida(evento)
            return

        if self.aguardando_inicio:         # popup "Iniciar": só ele recebe o mouse e o teclado
            self.tratar_inicio_do_minigame(evento)
            return

        if evento.type == pygame.KEYDOWN:
            enter = evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER)
            if enter and self.tela in config.TELAS_QUE_AVANCAM and self.tela not in config.TELAS_COM_SETAS:
                self.avancar_tela()
            elif enter and self.tela == config.PREPARO:
                self.iniciar_minigame()
            elif self.tela == config.MINIGAME and self.minigame is not None:
                if not self.minigame.done:
                    self.minigame.handle_key(evento.key)
                elif enter:
                    self.concluir_escolha(self.minigame.effect_multiplier())
            elif enter and self.tela == config.RESULTADO_DO_MINIGAME:
                self.proximo_evento()
            elif enter and self.tela == config.CONSEQUENCIA:
                self.proximo_evento()

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.tela in config.TELAS_COM_SETA_DO_MENU and self.visual.seta_do_menu_foi_clicada(mouse):
                self.apertar_seta("menu", self.pedir_confirmacao_de_saida)      # abre o popup "Voltar ao menu?"
            elif (self.tela in config.TELAS_COM_SETA_NO_CARD and self.visual.area_da_seta_do_card is not None
                  and self.visual.area_da_seta_do_card.collidepoint(mouse)):
                self.apertar_seta("card", self.continuar)
            elif (self.tela == config.RESULTADO_DO_MINIGAME and getattr(self.visual, "area_do_botao_de_novo", None) is not None
                  and self.visual.area_do_botao_de_novo.collidepoint(mouse)):
                self.tentar_de_novo()                                     # o botão "Tentar de novo"
            elif self.tela == config.ESCOLHA:
                opcoes = self.evento["opcoes"]
                for opcao, card in zip(opcoes, layout.retangulos_dos_cards(len(opcoes))):
                    if card.collidepoint(mouse):
                        self.escolher(opcao)
                        break
            elif self.tela == config.MINIGAME and self.minigame is not None and not self.minigame.done:
                self.minigame.handle_click(mouse)
            elif self.tela in config.TELAS_COM_SETAS:
                if self.visual.retangulo_da_seta("direita").collidepoint(mouse):
                    self.apertar_seta("direita", self.avancar_tela)
                elif self.tela != config.ABERTURA and self.visual.retangulo_da_seta("esquerda").collidepoint(mouse):
                    self.apertar_seta("esquerda", self.voltar_tela)
            elif self.tela == config.FINAL and layout.retangulo(layout.FINAL_BOTAO).collidepoint(mouse):
                self.jogar_de_novo()

        if evento.type == pygame.MOUSEMOTION:
            if self.tela == config.MINIGAME and self.minigame is not None and not self.minigame.done:
                self.minigame.handle_drag(mouse, bool(evento.buttons[0]))

        if evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            if self.tela == config.MINIGAME and self.minigame is not None and not self.minigame.done:
                self.minigame.handle_release(mouse)

    # ============================================================
    # O RELÓGIO DAS TELAS E O LAÇO DO JOGO
    # ============================================================
    def medir_tempo_da_tela(self, dt):
        """Conta há quanto tempo a tela atual está aí (a dica do ENTER usa isso)
        e, passado o AVANCO_AUTOMATICO dela, avança (o mesmo que o ENTER)."""
        # (na tela do minigame, o relógio recomeça quando o jogo termina: a dica de "ver o
        #  resultado" espera o mesmo tempo depois do fim)
        terminou = self.tela == config.MINIGAME and self.minigame is not None and self.minigame.done
        chave = (self.tela, self.indice_conselheira, terminou)
        if chave != self._chave_da_tela:          # mudou de tela (por ENTER ou sozinha)
            self._chave_da_tela = chave
            self.tempo_da_tela = 0.0
        self.tempo_da_tela += min(dt, 0.25)       # um engasgo do jogo não pula a tela
        limite = config.AVANCO_AUTOMATICO.get(self.tela)
        if limite and self.tempo_da_tela >= limite:
            self.tempo_da_tela = 0.0
            self.avancar_tela()

    def rodar(self):
        while True:
            dt = self.visual.relogio.tick(config.FPS) / 1000.0
            mouse = pygame.mouse.get_pos()
            for evento in pygame.event.get():
                self.tratar_evento(evento, mouse)

            self.visual.atualizar(dt)
            self.andar_o_clique_da_seta(dt)
            if self.confirmando_saida or self.aguardando_inicio:     # popup aberto: o jogo fica parado (o relógio não corre)
                desenho.desenhar(self.visual, self, mouse)
                continue
            self.medir_tempo_da_tela(dt)

            if self.tela == config.PREPARO and config.COMECAR_O_MINIGAME_SOZINHO:
                # (contagem do preparo: só se o jogo começa sozinho; senão espera o ENTER)
                self.tempo_de_preparo -= dt
                if self.tempo_de_preparo <= 0:
                    self.iniciar_minigame()

            if self.tela == config.MINIGAME and self.minigame is not None:
                self.minigame.update(dt)
                if self.minigame.done and self.tempo_da_tela >= config.SEGUNDOS_ATE_O_RESULTADO:
                        self.concluir_escolha(self.minigame.effect_multiplier())

            desenho.desenhar(self.visual, self, mouse)   # desenha a tela atual


if __name__ == "__main__":
    Jogo().rodar()
