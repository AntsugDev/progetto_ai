# Progetto AI

Per maggiori dettagli si rimanda [Progetto AI- WORLD](https://docs.google.com/document/d/1H7IxkOZ4bvjfylxURQkMoo6dv6zCkGSAIYgHQcgnA-w/edit?usp=sharing)

## Descrizione 

Questo progetto ha lo scopo di creare un AI a fini di studio.

Nella directory **script_ufficiali**, si trovano gli script python

Questa directory è così divisa:
- *Predittivo*: contiene i file per creare e addestrare il modello predittivo
- *Chat Agente*: contiene i file per creare e addestrare il modello di chat
- *Parte Iniziale*: contiene i file per creare e addestrare il modello di chat (test)
- *.docker*: in questa directory si trova il progetto e il docker file con per avviare un server, con le api necessaria al funzionamento del modello

All'interno della directory **Predittivo** si trovano:

- *FinacialEstimated* : modello di creazione di un agente predittivo per definire l'importo della rata del finanziamento e la sostenibilità
- *ModelVenditaAuto*: model creatto secondo le regole del file docx definito sopra
- *Bayesiano*: modello di test usato per studaiare gli algoritmi di Bayes


## Logica

### Modello predittivo vendita auto

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

***
### Modello predittivo finanziamento

In questo modello si un agente ai per definiree l'importo  della rata e la sostenibilità, relativa al reddito.
Le regole per il calcolo dell'importo della rata sono date dall'analisi finanziara, fatto salvo di conoscere:

- il reddito
- le spese totali che influiscono sul reddito
- il nr. delle rate
- l'importo del finanziamento da richiedere

In questo modello, sis richiede a quest'ultimo di calcolare e definire queste tre variabili:

- importo della rata
- la sostenibilità (rata/ reddito)
- in base la sostenibilità, se il finanziamento è accettabile o meno; se non lo è prevedere una simulazione di possibile soluzione accettabile

***

## Linguaggi usati e installazioni

- python (versione usata in questa progetto la 3.13.3)
- le librerie installabile con il file [libraries.txt](script-ufficiali/.docker/libraries.txt), installabile attraverso questo commando:
	<pre>pip install -r libraries.txt</pre>
- il file docker è presente all'interno della directory [Dockerfile](script-ufficiali/.docker/Dockerfile), eseguibile attraverso il commando:
    - build: <pre>docker build -t ai .</pre>
    - run: <pre>docker run -p 8000:8000 ai</pre>	

