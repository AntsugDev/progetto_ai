# Progetto AI

## Descrizione 

Questo progetto ha lo scopo di creare un AI a fini di studio.

Il progetto laravel in essere, ha il solo scopo di confronto dei risultati ottenuti dallo script in python.


## Logica

- definiamo una soglia di reddito che deve essere uguale a :
		<code>RedditoMedio + (RedditoMedio *(RedditoMin/RedditoMax))</code>
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
