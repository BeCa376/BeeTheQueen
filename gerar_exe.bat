@echo off
rem ------------------------------------------------------------------------------------------------
rem  GERA O EXECUTAVEL DO JOGO (dist\BeeTheQueen.exe). De dois cliques neste arquivo.
rem  Coloque-o na pasta do projeto (a do main.py). Rode de novo toda vez que mudar o jogo.
rem ------------------------------------------------------------------------------------------------
cd /d "%~dp0"

if not exist venv\Scripts\activate.bat (
  echo Nao achei a pasta venv aqui. Crie com os comandos:
  echo     py -3.13 -m venv venv
  echo     venv\Scripts\activate
  echo     pip install -r requirements.txt
  pause
  exit /b 1
)

call venv\Scripts\activate.bat

python -c "import pygame, PyInstaller" 2>nul
if errorlevel 1 (
  echo Faltam pacotes na venv. Rode:  pip install -r requirements.txt
  echo Se o pygame der erro ao instalar, a venv foi criada com um Python novo demais: recrie com o 3.13.
  pause
  exit /b 1
)

echo Gerando o jogo... (leva de 1 a 3 minutos; os avisos amarelos podem ser ignorados)
pyinstaller --noconfirm --clean bee_the_queen.spec
if errorlevel 1 (
  echo.
  echo DEU ERRO. Copie a mensagem de cima e me mande.
  pause
  exit /b 1
)

echo.
echo PRONTO: dist\BeeTheQueen.exe
echo E so copiar esse UM arquivo para o outro computador (nao precisa instalar o Python la).
explorer dist
pause
