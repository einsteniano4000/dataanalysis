# Applicazione per Analisi Dati e Grafici

Questa applicazione è progettata per eseguire diverse operazioni matematiche e statistiche, tra cui:

- Creazione di grafici di funzioni
- Fitting di funzioni
- Statistica di una variabile
- Calcolo dell'errore propagato in una misura indiretta (propagazione di errori massimi)

## Dipendenze

Il programma utilizza le seguenti librerie Python:

- numpy
- matplotlib
- pandas
- scipy
- sympy
- PyQt5

## Installazione e Avvio

### Metodo Automatico

Per semplificare il processo di installazione e avvio, abbiamo creato script di lancio per i principali sistemi operativi.

#### Per Windows:
1. Fai doppio clic sul file `launch.bat` nella cartella del progetto.

#### Per Linux:
1. Apri un terminale nella cartella del progetto.
2. Rendi lo script eseguibile con il comando:
   ```
   chmod +x launch.sh
   ```
3. Esegui lo script:
   ```
   ./launch.sh
   ```

#### Per macOS:
1. Apri un terminale nella cartella del progetto.
2. Rendi lo script eseguibile con il comando:
   ```
   chmod +x launch_mac.sh
   ```
3. Esegui lo script:
   ```
   ./launch_mac.sh
   ```

Questi script automatizzeranno l'intero processo di creazione dell'ambiente virtuale, installazione delle dipendenze e avvio dell'applicazione.

### Metodo Manuale

Se preferisci l'installazione manuale, segui questi passaggi:

#### 1. Crea un ambiente virtuale

##### Per Windows:
```
python -m venv venv
```

##### Per Linux/macOS:
```
python3 -m venv venv
```

#### 2. Attiva l'ambiente virtuale

##### Per Windows:
```
.\venv\Scripts\activate
```

##### Per Linux/macOS:
```
source venv/bin/activate
```

#### 3. Installa le dipendenze

Con l'ambiente virtuale attivato, esegui:

```
pip install -r requirements.txt
```

#### 4. Avvia l'applicazione

```
python main.py
```

## Contribuire

Le istruzioni per contribuire al progetto verranno aggiunte in futuro.

## Licenza

Questo progetto è rilasciato sotto la licenza MIT. Vedi il file `LICENSE` per i dettagli completi.
