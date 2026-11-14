# Bee the Queen

Jogo de decisões em Python e pygame. Você é a nova rainha de uma colmeia e governa por
quatro estações (12 eventos), apoiada por quatro conselheiras. Cada escolha tem um custo e
um minigame, e o desempenho nele define quanto da decisão vale. Não existe final único: o
perfil do seu reinado sai do que você acumulou ao longo do ano.

## Como jogar

Dentro dos arquivos tem a pasta dist/BeeTheQueen, só executar esse arquivo q é o .exe do jogo

## Como rodar

Requer Python 3.10 ou mais novo (testado com 3.13).

```bash
python -m venv .venv 
```

```bash
./venv/Scripts/activate
```

```bash
pip install -r requirements.txt
```

```bash
python main.py
```

No Linux e no macOS, ative o ambiente com `source .venv/bin/activate`.

## Como jogar

| Tecla ou ação | O que faz |
| --- | --- |
| `ENTER` | Avança a tela ou começa o minigame |
| Clique em um card | Escolhe a proposta de uma conselheira |
| Botão "Jogar de novo" | Na tela final, começa outra partida do começo, a partir da abertura |
| Mouse | Joga os minigames (as instruções aparecem antes de cada um) |
| `R` | Reinicia a tentativa na Rota de Voo |

### O que você administra

- **Mel, Operárias e Relação com a Colmeia:** os recursos pagos em cada escolha. Com a
  Relação abaixo de 25, a produção rende menos; acima de 80, as escolhas bem-sucedidas
  rendem 10% a mais.
- **Harmonia:** cinco eixos: Biodiversidade, Produção, População, Cooperação e Inovação.
- **Afinidade:** quanto cada conselheira confia em você. Ela define o perfil final.

### As conselheiras e os minigames

| Conselheira | Eixo | Jogo (só sem o rodízio) | Penalidade quando falha |
| --- | --- | --- | --- |
| Flora | Biodiversidade | Sob as Folhas | -10 de mel |
| Melina | Produção | Rastro de Pólen | -10 operárias |
| Nectar | Inovação | Rota de Voo | -8 de Relação |
| Aurora | Cooperação | Antes da Poda | -4 de Relação e o próximo ganho de Cooperação vale metade |

**Rodízio dos minigames:** depois de cada decisão vem um minigame, sempre na mesma ordem,
qualquer que seja a conselheira escolhida. São 12 jogos, um para cada evento:

| Evento | Jogo | Evento | Jogo |
| --- | --- | --- | --- |
| 1 | Sob as Folhas | 7 | Quebra-cabeça de Soma |
| 2 | Rastro de Pólen | 8 | Campo Minado |
| 3 | Rota de Voo | 9 | Comunicação em Símbolos |
| 4 | Antes da Poda | 10 | Labirinto |
| 5 | Captura de Abelhas | 11 | Dominó |
| 6 | Jogo da Memória | 12 | Quebra-cabeça de Encaixe |

A dificuldade vem da estação do evento (Primavera 1, Verão 2, Outono 3, Inverno 4; ajuste em
`DIFICULDADE_POR_ESTACAO`, no `config.py`). A ordem fica em `minigames/rodizio.py`: para trocar um
jogo de lugar, é só trocar as linhas da lista. Se a lista tiver menos jogos que eventos, ela
recomeça do 1 e a dificuldade passa a vir de `DIFICULDADE_POR_VOLTA`. Com
`MINIGAMES_EM_RODIZIO = False` volta o modo antigo, em que cada conselheira joga o jogo dela
(tabela acima) e a escolha de Melina no evento 11 é ação direta.

O minigame termina em sucesso (100% do efeito), parcial (50%) ou falha (25%). O último evento é o "evento-espelho":
o efeito de cada opção depende do que você acumulou durante o ano.

## Estrutura do projeto

```text
main.py          orquestrador: a ordem das telas, as teclas e o laço do jogo
config.py        números e ajustes: equilíbrio, tempos, fontes
regras.py        regras: custo, efeitos, penalidade, ponte entre eventos
catalogo.py      carrega os eventos e confere se os arquivos combinam entre si
eventos/         a situação de cada evento: texto, opções e preço
minigames/       o rodízio (rodizio.py) e qual jogo cada conselheira joga, no modo sem rodízio
  jogos/         o código de cada minigame (um arquivo por jogo)
resultados/      o que acontece: efeitos, consequência e ponte para o próximo evento
introducao/      textos da abertura, das conselheiras e da Nova Rainha
data/            conselheiras, eixos da Harmonia e perfis finais
telas/           tudo que aparece na tela
assets/          imagens e desenhos do Aseprite (.ase, lidos direto pelo jogo)
  pixel/         a pixel art dos minigames (PNG: dá para retocar no Aseprite)
testes/          testes que jogam o jogo inteiro sozinho
ferramentas/     scripts de apoio da economia: balancear custos, conferir e gerar o relatório de testes
```

### Onde mexer

| Quero mudar | Arquivo |
| --- | --- |
| Texto ou preço de uma opção | `eventos/eNN_*.py` |
| Qual jogo uma conselheira joga | `minigames/eNN_*.py` |
| Efeitos, consequência, ponte para o próximo evento | `resultados/eNN_*.py` |
| Texto da introdução | `introducao/` |
| Cor, emoji ou penalidade de uma conselheira | `data/councilors.py` |
| Número do jogo, tempo das telas, fontes | `config.py` |
| Posição ou cor de algo na tela (inclusive a posição dos cards, sempre no meio da tela) | `telas/layout.py` |
| Textos e regras do popup "Iniciar" e do botão "Tentar de novo" (inclusive o limite de tentativas) | `telas/popup.py` |
| Os desenhos dos minigames (grama, terra, potes, bombas...) | `assets/pixel/*.png` |
| Alinhamento e estilo de cada texto | `telas/estilos.py` |
| Texto fixo de uma tela | `telas/textos.py` |
| Ordem das telas, o que uma tecla faz | `main.py` |

### Adicionar um evento

1. Crie um arquivo com o mesmo nome em `eventos/`, `minigames/` e `resultados/` (copie os
   de outro evento).
2. Acrescente o nome em `NOMES_DOS_EVENTOS`, em `catalogo.py`, na ordem em que ele acontece.
3. Rode o teste abaixo. Ao abrir, o jogo também confere os arquivos e diz qual está errado.

### Pontes entre eventos

A chave `"proximo"` de um resultado muda o evento seguinte: troca o texto de abertura e
barateia ou encarece o custo, conforme a conselheira escolhida e o resultado do minigame.
Hoje só `resultados/e01_o_novo_jardim.py` tem uma ponte; ele serve de modelo para as outras.

## Testes

```bash
python testes/jogar_tudo.py
```

Abre o jogo em uma janela invisível e joga 62 partidas do começo ao fim, desenhando cada
tela do caminho. O teste marca o resultado de cada minigame direto, sem jogá-lo: ele
confere o fluxo e as telas, não a jogabilidade dos minigames.

```bash
python testes/jogos_novos.py
```

Esse confere a jogabilidade dos 8 minigames mais novos: cria cada um em todas as dificuldades,
ganha jogando de verdade (clicando e arrastando), confere sucesso, parcial e falha nos limites,
que ficar parado nunca ganha, que tudo cabe na moldura e que o rodízio segue as estações.

## Ferramentas da economia

```bash
python ferramentas/balancear_economia.py
```

Mostra a conta dos custos de mel de cada conselheira e o que mudaria para nenhuma delas derrubar uma moeda
abaixo do mínimo (só mostra; com `--aplicar` grava nos eventos). Com os custos atuais deve dizer "Nada a mudar".

```bash
python ferramentas/conferir_economia.py
python ferramentas/testar_calculos.py
```

O primeiro confere a economia de ponta a ponta; o segundo gera `ferramentas/resultado_dos_testes.txt` com os
números do jogo para avaliar.

## Gerar o executável (.exe)

Precisa ser gerado no Windows, com o ambiente ativado:

```bash
pip install -r requirements.txt
```

```bash
pyinstaller --noconfirm bee_the_queen.spec
```

O jogo sai em `dist/BeeTheQueen.exe`, um arquivo só, que roda sem Python instalado. Se você
criar uma pasta nova de arquivos que o jogo carrega pelo nome, inclua-a em
`bee_the_queen.spec`. Eventos novos nas pastas atuais entram sozinhos.

## Créditos

Os emojis das conselheiras são do [Twemoji](https://github.com/twitter/twemoji), sob licença
CC-BY 4.0.
