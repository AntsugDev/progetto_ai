# Progetto AI

Per maggiori dettagli si rimanda [Progetto AI- WORLD](https://docs.google.com/document/d/1H7IxkOZ4bvjfylxURQkMoo6dv6zCkGSAIYgHQcgnA-w/edit?usp=sharing)

## Descrizione 

Questo progetto ha lo scopo di creare un AI a fini di studio.

Il progetto laravel in essere, ha il solo scopo di confronto dei risultati ottenuti dallo script in python e si trova nella directory [LARAVEL](php-test/control_data_model)

Nella directory **script_ufficiali**, si trovano gli script python



## Logica

- definiamo una soglia di reddito che deve essere uguale a :
		<code>RedditoMedio + (RedditoMedio *(RedditoMin/RedditoMax))</code>, con il risultato che se è minore di 2000, prendo la formula , altrimenti prendo 2000
- calcoliamo 3 score:
	- RE (econominco), dovuto per l'80% dal reddito e dal 20% dell'anticipo(se auto nuova)
	- RS (sostenibilità)
	- RD (altri fattori)
- lo score totale è dato da :
	<code>50%*RE + 30% RS + 20% RD;</code>
- in base al valore finale di RT,l'AI decide:
	- se è inferiore/uguale a 1.5 -> Bonifico
	- se compreso tra 1.6 e 4 -> Finanziamento/ Finanziamento a 3 anni
	- se compreso tra 4.1 e 4.9 -> revisione con simulazione
	- se maggiore o uguale a 5 -> non accettabile
        - se la sostenibilità è maggiore o uguale al 35% -> non accettabile
        - se la sostenibilità è compresa tra il 21% e il 29% -> revisione con simulazione
- La simulazione funziona così:
	- prendo il coefficiente K e vado a creare un indice di intensità, cioè che cresce all'aumentare di K; questa è uguale a Ic = K/1.6; si prende 1.6 come punto massimo, perchè per valori superiori la decisione è di non accettare(troppo rischioso), ho cambiato la formula in quanto per valori di K < 1.3, il risultato verrebbe negativo e di conseguenza anche tutto il resto
	- se auto usata calcolo: 
		- simulazione anticipo = <code>40%* Ic * Costo Auto</code>; quindi dovrà essere ricalcolato il finanziamento, la rata, la sostenibilità
		- simulazione più rate = <code>nrRate +(Ic * 40% * nrRate)</code>; quindi dovrà essere ricalcolata la nuova rata e la sostenibilità
	- se auto nuova calcolo:
	       - simulazione più rate = nrRate +(Ic * 40% * nrRate); quindi dovrà essere ricalcolata la nuova rata e la sostenibilità
	- a questo punto espongo i risultati, vedendo innanzitutto se la sostenibilità è inferiore al 25% e confronto quale tra le due sia la minore; quella che lo è risulta la decisione dell'AI   
	
## Fasi

### Creazione del modello

Attraverso il file [model.py](script-ufficiali/Parte Iniziale -model data/model.py), viene creato il modello base e le condizioni di valutazione ed esito del modello; in questo sono presenti lo studio e la definizione delle condizioni

Il file  [read_data](script-ufficiali/Parte Iniziale -model data/read_data.py), serve per inserire dei dati grezzi base (100 righe) sul database

Da questi due file si passa allo studio dei modelli, iniziando dal **Predittivo**

## Modello Predittivo

Questo è presente nella directory [Predittivo](/home/famigliapassasugamele/web/PYTHON/PROGETTO/script-ufficiali/Predittivo), in cui sono presenti i seguenti file:

- *train_model.py*, dove viene creato il file del modello e dove viene addestrato quet'ultimo
- *calcoli.py*, dove sono riportati i calcoli delle condizioni esposte nel file *model.py*
- *update.py*, dove vengono eseguite le query di inserimento e aggiornamento dei dati
- *test_model.py*, test di prova
