# Manuale d'uso — Analisi Dati e Visualizzazione

Applicazione per l'analisi dati di laboratorio: caricamento serie di dati con errori, fit (lineare, polinomiale, esponenziale) con χ², analisi statistica di base e propagazione degli errori.

## Indice

1. [Avvio dell'applicazione](#1-avvio-dellapplicazione)
2. [Tab "Visualizzazione Dati"](#2-tab-visualizzazione-dati)
3. [Eseguire un fit e leggere il χ²](#3-eseguire-un-fit-e-leggere-il-χ²)
4. [Tab "Analisi Statistica"](#4-tab-analisi-statistica)
5. [Tab "Propagazione Errori"](#5-tab-propagazione-errori)
6. [Salvare e caricare un progetto](#6-salvare-e-caricare-un-progetto)
7. [Sintassi delle formule](#7-sintassi-delle-formule)
8. [Domande frequenti / risoluzione problemi](#8-domande-frequenti--risoluzione-problemi)

---

## 1. Avvio dell'applicazione

Dalla cartella del progetto, con l'ambiente virtuale attivato:

```
python3 main.py
```

La finestra si apre con tre schede in alto: **Visualizzazione Dati**, **Analisi Statistica**, **Propagazione Errori**.

---

## 2. Tab "Visualizzazione Dati"

Questa è la scheda principale: qui si caricano le serie di dati, si generano grafici da formula e si eseguono i fit.

### 2.1 Aggiungere una serie di dati

Nel pannello a sinistra ci sono quattro pulsanti:

- **Aggiungi Serie di Esempio** — inserisce una serie di prova (seno di 100 punti), utile per fare pratica con l'interfaccia.
- **Inserisci Dati Manualmente** — apre una sequenza di finestre di dialogo che chiedono, in ordine:
  1. Nome della serie
  2. Valori di X, separati da virgola (es. `1, 2, 3, 4`)
  3. Valori di Y, separati da virgola
  4. Errori su X (opzionale — si può lasciare vuoto)
  5. Errori su Y (opzionale — si può lasciare vuoto)

  Il numero di valori X, Y ed errori (se inseriti) deve coincidere, altrimenti compare un messaggio d'errore.

- **Carica da CSV** — apre un file CSV con 2, 3 o 4 colonne, **senza intestazione richiesta** (la prima riga viene comunque saltata come se fosse un'intestazione). Ordine delle colonne:

  | Colonna 1 | Colonna 2 | Colonna 3 (opz.) | Colonna 4 (opz.) |
  |---|---|---|---|
  | X | Y | errore X | errore Y |

  Il nome della serie viene preso automaticamente dal nome del file.

- **Rimuovi Serie Selezionata** — elimina dalla lista la serie attualmente selezionata (clic sul suo nome nella lista sopra i pulsanti).

Ogni serie in elenco ha una casella di spunta: disattivandola, la serie resta caricata ma **non viene disegnata né inclusa nei fit**.

### 2.2 Generare un grafico da formula

Nella sezione **Formula** (sotto la lista delle serie):

- **Formula**: es. `x**2 + 2*x + 1` (vedi [sintassi delle formule](#7-sintassi-delle-formule) per le funzioni disponibili come `np.sin`, `np.sqrt`, ecc. — il campo suggerisce automaticamente i nomi delle funzioni mentre si scrive).
- **X min / X max**: intervallo su cui valutare la formula.
- **Numero di punti**: quanti punti calcolare nell'intervallo.

Premendo **Genera Grafico** la curva viene aggiunta come una nuova serie (senza errori). **Rimuovi ultimo grafico** toglie l'ultima serie generata da formula.

### 2.3 Etichette del grafico

Sotto il grafico si possono impostare **Titolo del grafico**, **Etichetta asse X** ed **Etichetta asse Y**; il pulsante **Aggiorna Etichette** applica i valori inseriti.

### 2.4 Salvare l'immagine del grafico

Il pulsante **Salva Grafico** apre una finestra per esportare il grafico corrente come file PNG.

---

## 3. Eseguire un fit e leggere il χ²

Nella sezione **Tipo di Fit**:

1. Scegli il tipo di fit dal menu a tendina:
   - **Nessun Fit**
   - **Lineare** — `y = a·x + b`
   - **Polinomiale** — grado impostabile nel campo che compare accanto al menu (minimo 1)
   - **Esponenziale** — `y = A · exp(B·x)`
2. Premi **Esegui Fit**.

Il fit viene calcolato **su tutte le serie attualmente visibili** (spuntate nella lista). Per ciascuna serie compare nel riquadro dei risultati:

- l'equazione del fit con i coefficienti,
- ogni coefficiente con il suo errore, nel formato **valore ± errore** arrotondato secondo la convenzione di laboratorio (errore a 1 cifra significativa, 2 se la prima cifra è 1),
- **R²** (coefficiente di determinazione),
- **χ², gradi di libertà (dof) e χ² ridotto** — **solo se la serie ha errori su Y**.

> **Importante**: se la serie non ha errori su Y (inseriti manualmente o da CSV), il fit viene comunque eseguito ma **non compaiono χ² e χ² ridotto**, perché senza un'incertezza sui dati il χ² non ha significato statistico. Per vedere il χ², la serie deve avere la colonna errore Y valorizzata.

Un fit pesato (con errori su Y) dà anche coefficienti ed errori sui coefficienti calcolati correttamente pesando ogni punto con `1/errore²`, secondo il metodo dei minimi quadrati pesati.

Per il fit polinomiale: servono almeno *grado + 2* punti nella serie, altrimenti compare un errore.

Il grafico del fit (curva sovrapposta ai dati) viene aggiunto automaticamente al grafico principale.

---

## 4. Tab "Analisi Statistica"

Sezione indipendente per analizzare un singolo insieme di numeri (non collegata alle serie della prima scheda).

1. Nel campo **Dati** inserisci i numeri separati da virgola (es. `12.3, 11.8, 12.5, 12.1`).
2. **Calcola Statistiche** mostra: media (con errore standard), deviazione standard, minimo, massimo, mediana, skewness, kurtosis e semidispersione massima.
3. **Crea Istogramma** disegna l'istogramma dei dati inseriti, con linee verticali per media e media ± deviazione standard. Il numero di intervalli (bin) si imposta nel campo **Numero di bin**.
4. **Invia media a Propagazione Errori →** apre una finestra per dare un nome alla variabile e trasferisce automaticamente **media ± errore standard** come variabile pronta all'uso nella scheda Propagazione Errori (evita di dover ricopiare i numeri a mano).

---

## 5. Tab "Propagazione Errori"

Calcola il valore e l'errore propagato di un'espressione che combina più variabili, ciascuna con il proprio valore e la propria incertezza (propagazione degli errori con le derivate parziali, formula standard di laboratorio).

1. **Aggiungi Variabile**: inserisci nome, valore ed errore (i campi Valore/Errore accettano anche espressioni come `np.sqrt(2)`), poi premi il pulsante. La variabile compare nell'elenco **Variabili**.
2. **Espressione**: scrivi la formula che combina le variabili aggiunte, es. `a * b + np.sin(c)` (autocompletamento disponibile per le funzioni `np.*`).
3. **Calcola** mostra:
   - il **risultato ± errore assoluto** (formattato secondo la convenzione di laboratorio),
   - l'**errore relativo**,
   - l'**errore percentuale**.
4. **Clear** azzera variabili, espressione e risultato.

Le variabili aggiunte restano disponibili finché non premi Clear o chiudi l'app: puoi riusarle in più calcoli successivi.

---

## 6. Salvare e caricare un progetto

Dal menu **File** in alto:

- **Salva Progetto...** salva in un file `.json` tutte le serie di dati (con relativi errori) e le etichette del grafico (titolo, asse X, asse Y) della scheda Visualizzazione Dati.
- **Carica Progetto...** ricarica un file `.json` salvato in precedenza, ripristinando serie ed etichette.

> Nota: il salvataggio progetto copre solo la scheda **Visualizzazione Dati** (serie ed etichette). Variabili di Propagazione Errori e dati di Analisi Statistica non vengono salvati e vanno reinseriti a ogni sessione.

---

## 7. Sintassi delle formule

Formule (campo "Formula" e campo "Espressione") supportano operatori aritmetici standard (`+ - * / ** %`) e le funzioni, sempre col prefisso `np.`:

`np.sin`, `np.cos`, `np.tan`, `np.arcsin`/`np.asin`, `np.arccos`/`np.acos`, `np.arctan`/`np.atan`, `np.sinh`, `np.cosh`, `np.tanh`, `np.exp`, `np.log`, `np.log10`, `np.log2`, `np.sqrt`, `np.cbrt`, `np.abs`

più le costanti `np.pi` e `np.e`.

Nel campo Formula della scheda Visualizzazione Dati, la variabile è sempre `x` (es. `np.sin(x) + x**2`).

Per motivi di sicurezza le formule **non** vengono valutate con `eval()`: solo le funzioni/costanti elencate sopra sono ammesse. Qualsiasi altra chiamata o nome viene rifiutato con un messaggio d'errore esplicito.

---

## 8. Domande frequenti / risoluzione problemi

**Non vedo il χ² dopo il fit.**
Controlla che la serie abbia gli errori su Y impostati (in fase di inserimento manuale o come 4ª colonna del CSV). Senza errori su Y il χ² non viene calcolato.

**"Il numero di valori X e Y deve essere uguale."**
Nell'inserimento manuale hai scritto un numero diverso di valori X e Y (o di errori). Controlla di aver separato correttamente i numeri con virgole.

**"Punti insufficienti" nel fit polinomiale.**
Il grado scelto richiede almeno *grado + 2* punti nella serie per poter stimare gli errori sui coefficienti. Riduci il grado o aggiungi punti.

**Il fit esponenziale non converge.**
Con dati molto rumorosi o un intervallo di valori poco adatto, l'algoritmo di fit non lineare può non convergere; il risultato in questo caso indica esplicitamente che il fit non è converso.

**Ho chiuso l'app e ho perso le variabili di Propagazione Errori / i dati di Analisi Statistica.**
È normale: solo la scheda Visualizzazione Dati si salva su file (vedi [sezione 6](#6-salvare-e-caricare-un-progetto)). Le altre due schede non hanno salvataggio persistente.
