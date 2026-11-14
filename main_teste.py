# -*- coding: utf-8 -*-
"""
MAIN DE TESTE: para testar UM minigame de cada vez, sem passar pelo jogo todo.

    python main_teste.py

Só tem três coisas, do Evento 1:
    as 4 escolhas das conselheiras  ->  o minigame  ->  o resultado
Depois do resultado, a seta (ou o ENTER) volta para as escolhas, para você testar de novo.
A partida é zerada a cada volta (as moedas não acumulam). A seta de voltar ao menu, embaixo
à esquerda, também só recomeça o teste.

PARA ESCOLHER O JOGO, mude o número da linha  jogo = ...  logo abaixo e rode de novo.
Ao fim de cada minigame, o terminal mostra o resultado (sucesso, parcial ou falha).

Este arquivo usa o main.py do jogo como ele está: nada do jogo normal foi mexido.
"""
import sys

import pygame

import config
import main
from minigames import rodizio

# ============================================================
# AJUSTES DO TESTE
# ============================================================
jogo = 2                    # <<< O JOGO QUE VOCÊ QUER TESTAR (de 1 a 12), conforme minigames/rodizio.py:
#                               1 = Sob as Folhas          7 = Quebra-cabeça de Soma
#                               2 = Rastro de Pólen        8 = Campo Minado
#                               3 = Rota de Voo            9 = Comunicação em Símbolos
#                               4 = Antes da Poda         10 = Labirinto
#                               5 = Captura de Abelhas    11 = Dominó
#                               6 = Jogo da Memória       12 = Quebra-cabeça de Encaixe

DIFICULDADE = None          # None = a da estação do Evento 1 (Primavera = 1). Ou um número de 1 a 5 para forçar.
MOSTRAR_O_PREPARO = False   # True = mostra antes a tela com a explicação do jogo (a que tem a setinha de começar)


class JogoDeTeste(main.Jogo):
    """O jogo de sempre, só que preso ao Evento 1 e ao minigame escolhido acima."""

    def __init__(self):
        if not 1 <= jogo <= len(rodizio.ORDEM):
            lista = "\n".join(f"  {i} = {classe.name}" for i, classe in enumerate(rodizio.ORDEM, start=1))
            sys.exit(f"main_teste.py: não existe o jogo = {jogo}. Escolha um número de 1 a {len(rodizio.ORDEM)}:\n{lista}")
        super().__init__()
        self._recomecar()
        print(f"Testando o jogo {jogo}: {rodizio.ORDEM[jogo - 1].name}")

    def _recomecar(self):
        """Volta para as escolhas do Evento 1, com tudo zerado."""
        self._zerar_partida()
        self.indice_do_evento = 0
        self.estacao_atual = self.evento["estacao"]
        self.tela = config.ESCOLHA

    # ---------------------------------------------------------- o que muda no fluxo
    def escolher(self, opcao):
        """Escolheu uma conselheira: vai direto para o jogo escolhido lá em cima."""
        self.opcao = opcao
        self.minigames_jogados = jogo - 1          # o rodízio entrega exatamente este jogo
        self.escolher_no_rodizio()                 # (deixa a tela no preparo)
        if DIFICULDADE is not None:
            self.dificuldade = DIFICULDADE
        if not MOSTRAR_O_PREPARO:
            self.iniciar_minigame()

    def concluir_escolha(self, multiplicador):
        """O minigame terminou: mostra o resultado na tela e conta no terminal."""
        super().concluir_escolha(multiplicador)
        m = self.minigame
        tempo = getattr(m, "time_left", None)
        sobra = f" (sobraram {tempo:.1f} s)" if isinstance(tempo, (int, float)) and tempo > 0 else ""
        print(f"  jogo {jogo} ({self.nome_do_minigame}), dificuldade {self.dificuldade}: "
              f"{m.result.upper()}{sobra}")

    def continuar(self):
        """A seta do cartão do resultado volta para as escolhas, em vez de ir para a consequência."""
        if self.tela == config.RESULTADO_DO_MINIGAME:
            self._recomecar()
        else:
            super().continuar()

    def jogar_de_novo(self):
        """A seta de voltar ao menu: aqui só recomeça o teste."""
        self._recomecar()

    def tratar_evento(self, evento, mouse):
        enter = evento.type == pygame.KEYDOWN and evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER)
        if enter and self.tela == config.RESULTADO_DO_MINIGAME:
            self._recomecar()                      # o ENTER no resultado também volta para as escolhas
            return
        super().tratar_evento(evento, mouse)


if __name__ == "__main__":
    JogoDeTeste().rodar()
