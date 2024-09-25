#!/bin/bash

# Crea un ambiente virtuale se non esiste
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Attiva l'ambiente virtuale
source venv/bin/activate

# Installa i pacchetti da requirements.txt, ignorando quelli di sistema
pip install --ignore-installed -r requirements.txt

# Esegui il file main.py
python3 main.py

# Disattiva l'ambiente virtuale
deactivate
