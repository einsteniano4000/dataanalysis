@echo off
REM Crea un ambiente virtuale se non esiste
if not exist venv (
    python -m venv venv
)

REM Attiva l'ambiente virtuale
call venv\Scripts\activate.bat

REM Installa i pacchetti da requirements.txt, ignorando quelli di sistema
python -m pip install --ignore-installed -r requirements.txt

REM Esegui il file main.py
python main.py

REM Disattiva l'ambiente virtuale
deactivate
