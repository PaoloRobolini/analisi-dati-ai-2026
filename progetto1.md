# Progetto "Pokémon Statistics"

**Obiettivo**: Imparare a estrarre informazioni da un dataset reale usando Python puro (senza librerie esterne).

**Ruolo**: Sei un Data Analyst ingaggiato per scoprire quali sono i Pokémon più forti e come sono distribuite le loro statistiche.

## PREPARAZIONE
Prima di iniziare, dobbiamo creare il nostro "Database".

- Apri il tuo editor Python (IDLE, Thonny, VS Code, oppure Colab).

- Crea un nuovo file di testo, chiamalo pokemon.csv.

- Incolla dentro questo testo (è una versione semplificata e pulita del dataset Kaggle):

Name,Type,Attack,Defense,Speed
Bulbasaur,Grass,49,49,45
Charmander,Fire,52,43,65
Squirtle,Water,48,65,43
Pikachu,Electric,55,40,90
Charizard,Fire,84,78,100
Blastoise,Water,83,100,78
Venusaur,Grass,82,83,80
Mewtwo,Psychic,110,90,130
Snorlax,Normal,110,65,30
Gengar,Ghost,65,60,110
Onix,Rock,45,160,70
Machamp,Fighting,130,80,55
Alakazam,Psychic,50,45,120
Arcanine,Fire,110,80,95
Gyarados,Water,125,79,81
Jigglypuff,Normal,45,20,20
Dragonite,Dragon,134,95,80

- Salva il file.

- Crea un nuovo file Python analisi.py nella stessa cartella del CSV.

## Importazione e Casting

Teoria: Un file CSV è solo testo. Python non sa che "80" è un numero. Dobbiamo insegnarglielo noi.

### Task 1: Caricare i dati

Scrivi il codice per aprire e leggere il file pokemon.csv riga per riga, saltando la prima riga (l'intestazione). Conta il numero di righe per verificare che siano state tutte caricate correttamente. 

**Nota**: Puoi scrivere usando python puro, senza librerie, facendo uso di funzioni built-in come `open()` e `readlines()`. In alternativa puoi usare la libreria `csv` se preferisci.

## task 2: Il problema dei Numeri

Ora che hai caricato i dati, prova a stampare il tipo di una statistica, ad esempio l'Attack, per un Pokémon a tua scelta. Vedrai che è una stringa (str) e non un numero (int). 

Scrivi il codice per convertire le statistiche Attack, Defense e Speed da stringhe a interi (int) mentre leggi i dati. Verifica la conversione stampando il tipo di una di queste statistiche dopo la conversione.

## MODULO 2: Analisi Statistica

### Task 3: Calcolare la Media

Scrivi il codice per calcolare la media delle statistiche Attack, Defense e Speed di tutti i Pokémon nel dataset. Stampa i risultati.

### Task 4: Trovare il Pokémon più Forte

Scrivi il codice per trovare il Pokémon con il valore più alto in ciascuna delle tre statistiche (Attack, Defense, Speed). Stampa il nome del Pokémon e il valore della statistica corrispondente.

### Task 5: Distribuzione delle Statistiche

Scrivi il codice per contare quanti Pokémon hanno un valore di Attack superiore a 100. Stampa il risultato.

### Task6: Visualizzazione & Challenge

Per questa parte, puoi scegliere di usare una libreria di visualizzazione come Matplotlib o Seaborn, oppure puoi semplicemente stampare i risultati in modo leggibile.

- Scrivi il codice per creare un semplice grafico a barre che mostra la media delle statistiche Attack, Defense e Speed. Se non vuoi usare librerie esterne, puoi semplicemente stampare i risultati in modo leggibile.

- Scrivi il codice per trovare e stampare i nomi di tutti i Pokémon che hanno una statistica Speed superiore alla media calcolata in precedenza.

- Quali sono i 5 Pokémon con l'attacco più alto? Stampa i loro nomi e valori di attacco.

- I Pokémon sono in media veloci o lenti? Ci sono più Pokémon scarsi o fortissimi? Crea una breve analisi scritta basata sui dati che hai raccolto, supportata da numeri e statistiche, creando anche qualche visualizzazione che ritieni utile.

- Se un Pokémon ha tanta Difesa, ha anche tanta Velocità? O sono lenti?Scrivi il codice per calcolare la correlazione tra le statistiche Defense e Speed. Stampa il risultato e interpreta il significato.

- Qual è la percentuale di Pokémon di Fuoco rispetto all'Acqua?" Scrivi il codice per calcolare la percentuale di Pokémon di tipo Fire rispetto a quelli di tipo Water. Stampa il risultato usando il grafico adatto. Dai una breve interpretazione del dato.

- Scegliete due caratteristiche (es. Attacco e Velocità) e createmi un grafico che dimostri se i Pokémon veloci sono anche forti. Usa scatter plot o un altro tipo di grafico che ritieni adatto. Scrivi una breve analisi del grafico.