# Bee the Queen

Jogo de decisões em Python e pygame. Você é a nova rainha de uma colmeia e governa por
quatro estações (12 eventos), apoiada por quatro conselheiras. Cada escolha tem um custo e
um minigame, e o desempenho nele define quanto a decisão custa e rende. Não existe final único: o
perfil do seu reinado sai da afinidade que você construiu com cada conselheira ao longo do ano.

## Só quero jogar

Dê dois cliques em `dist/BeeTheQueen.exe`. É um arquivo só, que roda **sem Python instalado**, em
Windows 64 bits. Para gerar o `.exe` (ou atualizá-lo depois de mexer no jogo), veja
[Gerar o executável](#gerar-o-executável-exe).

## Como rodar a partir do código

Use o **Python 3.13** (o projeto aceita 3.10 ou mais novo, mas o `pygame==2.6.1` pode não ter versão
pronta para um Python bem mais novo; veja "Problemas comuns" abaixo).

No PowerShell, dentro da pasta do projeto (a do `main.py`):

```powershell
python -m venv venv
./venv/Scripts/activate
pip install -r requirements.txt
python main.py
```

O ambiente se chama `venv` (sem ponto). No Linux e no macOS, ative com `source venv/bin/activate`.

### Problemas comuns

| O que aparece | O que é | O que fazer |
| --- | --- | --- |
| `.venv\Scripts\activate` não é reconhecido | O ambiente se chama `venv`, sem o ponto | `./venv/Scripts/activate` |
| `Failed to build 'pygame'` / `No module named 'distutils.msvccompiler'` | O Python é novo demais e o pygame 2.6.1 não tem versão pronta, então o `pip` tenta compilar e falha | Apague a pasta `venv` e recrie com o 3.13: `py -3.13 -m venv venv` |
| O PowerShell diz que a execução de scripts está desabilitada | A política do PowerShell bloqueia o `activate` | `Set-ExecutionPolicy -Scope Process Bypass` e ative de novo (vale só para esta janela) |
| `ModuleNotFoundError: pygame` | O ambiente não está ativo | Ative a `venv` (deve aparecer `(venv)` no começo da linha) |

## Como jogar

| Tecla ou ação | O que faz |
| --- | --- |
| `ENTER` | Avança a tela, começa o minigame (na tela de preparo e no popup "Iniciar") e passa do resultado |
| Clique em um card | Escolhe a proposta de uma conselheira |
| Seta amarela no card | Avança para a próxima tela |
| Seta amarela embaixo à esquerda | Volta ao menu inicial (pede confirmação; a partida não é salva) |
| Botão "Iniciar" (popup) | Começa o minigame. O tempo só conta depois do clique |
| Botão "Tentar de novo" | Na tela de resultado, só em **falha** ou **parcial**: desfaz o resultado e repete o mesmo minigame |
| Botão "Jogar de novo" | Na tela final, começa outra partida do começo, a partir da abertura |
| Mouse | Joga os minigames (as instruções aparecem antes de cada um) |

### O que você administra

- **Mel, Operárias e Relação com a Colmeia:** os recursos pagos em cada escolha. Começam em 100, 100 e 60.
  Nenhum cai abaixo de **5** nem passa de **100**.
- **Produção da estação:** no fim de cada estação (depois dos eventos 3, 6, 9 e 12) a colmeia produz
  **+12 de mel, +4 de operárias e +2 de Relação** (`RENDA_POR_ESTACAO`, no `config.py`).
- **Afinidade:** quanto cada conselheira confia em você (começa em 40). Cada escolha aumenta a da conselheira
  escolhida e costuma diminuir a das outras (os valores de cada evento estão em `resultados/eNN_*.py`). No fim, a conselheira com mais
  afinidade define o perfil do seu reinado; se a diferença entre a maior e a menor afinidade for menor que 15,
  o perfil é **Equilibrado**.

### O resultado do minigame muda o preço

Cada evento tem o custo e o ganho base de cada opção (`eventos/eNN_*.py`). O resultado do minigame multiplica os dois
(valores arredondados para baixo):

| Resultado | Custo | Ganho |
| --- | --- | --- |
| Sucesso | × 0,75 (mais barato) | × 1,25 |
| Parcial | × 1 (o do evento) | × 1 |
| Falha | × 1,25 (mais caro) | × 0,75 |

Os fatores estão em `FATOR_DO_CUSTO` e `FATOR_DO_GANHO`, no `config.py`. Cada minigame tem os limites de
sucesso, parcial e falha e o tempo no começo do próprio arquivo (`minigames/jogos/`).

### As conselheiras e os minigames

| Conselheira | Foco | Jogo (só sem o rodízio) |
| --- | --- | --- |
| Flora | Biodiversidade | Sob as Folhas |
| Melina | Produção | Rastro de Pólen |
| Nectar | Inovação | Rota de Voo |
| Aurora | Cooperação | Antes da Poda |

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

**Tentar de novo:** em falha ou parcial, o botão desfaz o resultado daquela tentativa (as moedas voltam ao que
eram) e começa o mesmo jogo outra vez. Por padrão não há limite. Para limitar, mude
`NOVAS_TENTATIVAS_POR_JOGO` no topo de `telas/popup.py` (`1` = uma nova tentativa, `0` = sem o botão).

### A pixel art dos minigames

Os desenhos (grama, terra, potes de mel, bomba, molduras...) ficam em `assets/pixel/*.png`. Abra no Aseprite,
retoque e salve por cima: o jogo usa o seu arquivo. Os mesmos desenhos também vão dentro do código
(`minigames/jogos/pixel_dados.py`), só como reserva: se a pasta `assets/pixel/` sumir, o jogo avisa no terminal e
continua com o visual certo. Para **refazer todos** os desenhos do zero há `assets/pixel/gerador/gerar_pixelart.py`
(precisa de `numpy` e `pillow`; rodar apaga os seus retoques).

## Estrutura do projeto

```text
main.py              orquestrador: a ordem das telas, as teclas e o laço do jogo
main_teste.py        testa UM minigame de cada vez, sem passar pelo jogo todo (veja "Testes")
config.py            números e ajustes: equilíbrio, tempos, fontes
regras.py            regras: custo, produção, afinidade, perfil final
catalogo.py          carrega os eventos e confere se os arquivos combinam entre si
eventos/             a situação de cada evento: texto, opções e preço
minigames/           o rodízio (rodizio.py) e qual jogo cada conselheira joga, no modo sem rodízio
  jogos/             o código de cada minigame (um arquivo por jogo) e o pixel.py, que desenha a pixel art
resultados/          o que acontece: afinidade, texto de abertura do próximo evento
introducao/          textos da abertura, das conselheiras e da Nova Rainha
data/                conselheiras e perfis finais
telas/               tudo que aparece na tela (layout.py, estilos.py, textos.py, popup.py...)
assets/              imagens e desenhos do Aseprite (.ase, lidos direto pelo jogo)
  pixel/             a pixel art dos minigames (PNG) e, em gerador/, os programas que a desenham
  icone.png          o ícone da janela e da barra de tarefas
  icone.ico          o ícone do arquivo .exe
testes/              testes que jogam o jogo inteiro sozinho
ferramentas/         scripts de apoio da economia: balancear custos, conferir e gerar o relatório de testes
requirements.txt     o que o jogo precisa (pygame) e o que gera o .exe (pyinstaller)
bee_the_queen.spec   a "receita" do .exe (veja "Gerar o executável")
gerar_exe.bat        dois cliques e o .exe é gerado (veja "Gerar o executável")
```

As pastas `build/` e `dist/` aparecem depois de gerar o `.exe` e não fazem parte do código.

### Onde mexer

| Quero mudar | Arquivo |
| --- | --- |
| Texto ou preço de uma opção | `eventos/eNN_*.py` |
| Qual jogo uma conselheira joga | `minigames/eNN_*.py` |
| Afinidade e texto de abertura do próximo evento | `resultados/eNN_*.py` |
| Texto da introdução | `introducao/` |
| Cor ou emoji de uma conselheira | `data/councilors.py` |
| Número do jogo, tempo das telas, fontes, fatores de custo e ganho, produção da estação | `config.py` |
| Tempo e limites de sucesso/parcial/falha de um minigame | o começo de `minigames/jogos/<jogo>.py` |
| Posição ou cor de algo na tela (os cards ficam no meio da tela) | `telas/layout.py` |
| Subir ou descer o card do jogo, ou trazer de volta a linha "propôs" | `MINIGAME_SOBE` e `MINIGAME_MOSTRA_A_PROPOSTA`, em `telas/layout.py` |
| Textos do popup "Iniciar" e do botão "Tentar de novo", e o limite de tentativas | `telas/popup.py` |
| Os desenhos dos minigames | `assets/pixel/*.png` |
| Alinhamento e estilo de cada texto | `telas/estilos.py` |
| Texto fixo de uma tela | `telas/textos.py` |
| Ordem das telas, o que uma tecla faz | `main.py` |
| O ícone do jogo | `assets/icone.png` e `assets/icone.ico` (veja "Ícone do jogo") |

### Adicionar um evento

1. Crie um arquivo com o mesmo nome em `eventos/`, `minigames/` e `resultados/` (copie os
   de outro evento).
2. Acrescente o nome em `NOMES_DOS_EVENTOS`, em `catalogo.py`, na ordem em que ele acontece.
3. Rode o teste abaixo. Ao abrir, o jogo também confere os arquivos e diz qual está errado.

### Pontes entre eventos

A chave `"proximo"` de um resultado pode trocar o texto de abertura do evento seguinte, conforme a
conselheira escolhida e o resultado do minigame. Use um dos arquivos de `resultados/` como modelo.

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

Esse confere a jogabilidade dos minigames mais novos: cria cada um em todas as dificuldades,
ganha jogando de verdade (clicando e arrastando), confere sucesso, parcial e falha nos limites,
que ficar parado nunca ganha, que tudo cabe na moldura e que o rodízio segue as estações.
**Atenção:** ele ainda compara com tempos e quantidades antigos de alguns jogos, então mostra uns 23 avisos
`FALHOU` que vêm disso (os tempos foram ajustados depois). Se a lista crescer depois de uma mudança sua, aí vale olhar.

```bash
python main_teste.py
```

Para testar **um minigame só**: abra o `main_teste.py`, mude o número da linha `jogo = ...` (de 1 a 12) e rode. Você escolhe
uma conselheira, joga e vê o resultado; a seta volta para as escolhas para testar de novo, e a partida é zerada a cada volta.

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

O `.exe` é um arquivo único que roda em outro computador **sem Python instalado**. Quem o gera é o **PyInstaller**
(já está no `requirements.txt`). São três peças:

| Peça | O que é |
| --- | --- |
| `bee_the_queen.spec` | A **receita**: diz ao PyInstaller qual é o arquivo principal (`main.py`), que a pasta `assets/` inteira entra no pacote, a lista de eventos, resultados e minigames (o `catalogo.py` os carrega pelo nome, então o PyInstaller não os enxerga sozinho), o nome do arquivo (`BeeTheQueen`), que não abre janela de terminal (`console=False`) e qual é o ícone. **Não apague.** |
| `gerar_exe.bat` | O atalho: ativa o ambiente, confere os pacotes e roda o PyInstaller com a receita |
| `dist/BeeTheQueen.exe` | O resultado |

### Passo a passo

1. Deixe a `venv` pronta (veja "Como rodar a partir do código"), com `pip install -r requirements.txt` feito.
2. Dê dois cliques no `gerar_exe.bat`, na pasta do projeto. Leva de 1 a 3 minutos, e os avisos amarelos podem ser ignorados.
   Quando termina, ele abre a pasta `dist` com o `BeeTheQueen.exe`.

Pelo terminal, com a `venv` ativa, o equivalente é:

```powershell
pyinstaller --noconfirm --clean bee_the_queen.spec
```

### Levar o jogo para outro computador

- Copie **só o `BeeTheQueen.exe`** (pen drive, Google Drive, e-mail). O computador precisa ser Windows 64 bits.
- Se o Windows mostrar "O Windows protegeu o computador", clique em **Mais informações** e depois em **Executar assim mesmo**.
  Os `.exe` de arquivo único feitos pelo PyInstaller costumam ser barrados assim, e o antivírus também pode reclamar sem motivo.
- Para levar o **código** em vez do `.exe`: suba para o GitHub e, na outra máquina, `git clone`, crie a `venv`, rode
  `pip install -r requirements.txt` e `python main.py` (com o Python 3.13). A pasta `venv` não vai no git.
- `dist/` e `build/` estão no `.gitignore`, então o `.exe` **não** vai pelo git. Para compartilhá-lo, use o Google Drive
  ou a aba "Releases" do GitHub.

### Manter o `.exe` atualizado

O `.exe` é uma foto do jogo no momento em que foi gerado: **não se atualiza sozinho**. Sempre que mudar alguma coisa
(texto, regra, desenho), rode o `gerar_exe.bat` de novo e troque o `.exe` na outra máquina pelo novo.

### Se o `.exe` fechar na hora

Como o jogo não abre terminal (`console=False`), um erro some sem mostrar nada. Para ver a mensagem, troque para
`console=True` no `bee_the_queen.spec`, gere de novo e rode o `.exe` pelo terminal. Depois volte para `False`.

### Quando mexer no `bee_the_queen.spec`

Só se você criar uma **pasta nova de arquivos que o jogo carrega pelo nome** (inclua-a na receita). Eventos novos nas
pastas atuais entram sozinhos. As pastas `build/` e `dist/` podem ser apagadas a qualquer hora (o `gerar_exe.bat` as
refaz); copie o `.exe` antes se ainda precisar dele.

## Ícone do jogo

São dois arquivos, em `assets/`, e cada um serve a uma coisa:

| Arquivo | Onde aparece | Quem usa |
| --- | --- | --- |
| `icone.png` | A janela do jogo e a barra de tarefas | `telas/visual.py` |
| `icone.ico` | O arquivo `BeeTheQueen.exe` (na pasta `dist` e onde você o copiar) | `bee_the_queen.spec` |

Os dois são a abelhinha (`bee_frame_0.png`). Para trocar o desenho:

1. Substitua os dois arquivos **mantendo os nomes**. O `icone.png` deve ser quadrado (64×64 funciona bem). O `icone.ico`
   deve ter vários tamanhos dentro (de 16 a 256 pixels); use um conversor de PNG para ICO, que há vários gratuitos.
2. Rode o `gerar_exe.bat`. O `.spec` pega o `icone.ico` sozinho (se o arquivo não existir, o `.exe` sai sem ícone, sem dar erro).

No Windows, o `telas/visual.py` também dá ao jogo uma identidade própria na barra de tarefas; sem isso, rodando por
`python main.py`, ela agruparia a janela sob o ícone do Python. Se o ícone **antigo** continuar aparecendo no `.exe`, é o
cache de ícones do Windows: copie o arquivo para outra pasta, renomeie-o ou reinicie o computador.

## Regras antigas que ainda estão no código (sem efeito no jogo)

Ficaram no código mas **não são aplicadas**, e podem ser limpas quando você quiser:

- a **Harmonia** (os cinco eixos), o **efeito-espelho** do último evento e a produção a 85% com Relação baixa: a função
  que os aplicava (`_aplicar_efeitos`, em `regras.py`) não é mais chamada;
- a **penalidade de falha** de cada conselheira: o código ainda existe, mas as penalidades foram apagadas de
  `data/councilors.py`, então nada acontece;
- o **bônus de 10% com Relação alta** (`BONUS_RELACAO_ALTA`): é multiplicado sempre e não muda nenhum resultado;
- o aviso "Relação baixa: produção com penalidade!" no painel de recursos (abaixo de 25) aparece, mas hoje não há penalidade.