INTENT_SIMULAZIONE = "simulazione"
INTENT_CONSIGLIO = "consiglio"
INTENT_SOSTENIBILITA = "valutazione_sostenibilita"
INTENT_ALTERNATIVE = "alternative"
INTENT_INFO = "informazione"
INTENT_DATI_MANCANTI = "dati_mancanti"
INTENT_CONVERSAZIONE = "conversazione_generale"

import re

class IntentDetector:
    def __init__(self):
        self.patterns = {
            "simulazione": [
                r"quanto pago",
                r"quanto pagherei",
                r"rata",
                r"mensile",
                r"simula",
                r"calcola"
            ],
            "consiglio": [
                r"cosa consigli",
                r"mi consigli",
                r"meglio",
                r"quale conviene",
                r"consiglio",
                r"è consigliabile",
                r"consigliabile"
            ],
            "valutazione_sostenibilita": [
                r"posso permettermi",
                r"posso fare",
                r"è sostenibile",
                r"è troppo",
                r"ce la faccio",
                r"sostenibile"
            ],
            "alternative": [
                r"alternative",
                r"abbassare la rata",
                r"abbassarla",
                r"ridurre la rata",
                r"soluzione migliore",
                r"altra opzione"
            ],
            "informazione": [
                r"come funziona",
                r"cosa puoi fare",
                r"che dati servono",
                r"aiuto",
                r"help"
            ],
            "conversazione_generale": [
                r"ok",
                r"va bene",
                r"capito",
                r"grazie",
                r"non sono sicuro",
                r"non so"
            ]
        }


    def get_intent(self, msg: str) -> str:
        msg = msg.lower()

        status = {intent: 0 for intent in self.patterns.keys()}

        # Cerca parola chiave per ogni intent
        for intent, pattern_list in self.patterns.items():
            for p in pattern_list:
                if re.search(p, msg):
                    status[intent] += 1

        # Nessun match → verifica numeri
        if all(v == 0 for v in status.values()):
            if not re.search(r"\d+", msg):
                return "dati_mancanti"
            return "simulazione"


        # Intent con punteggio massimo
        max_score = max(status.values())
        candidati = [k for k, v in status.items() if v == max_score]

        # Se c'è un solo intento → ok
        if len(candidati) == 1:
            return candidati[0]
        list_intent = ", ".join(candidati)
        # Parità → richiesta ambigua
        return f"La tua richiesta contiene più aspetti ({list_intent}). Puoi dirmi cosa vuoi sapere per primo?"

if __name__ == "__main__":
    print("-"*80)
    print("Prova di intent dectector ...\n")
    detector = IntentDetector()
    #richiesta = input("Inserisci la tua richiesta: ")
    richiesta = "è consigliabile un prestito di 5000 euro per una rata mensile di 250 euro e con un reddito di 1245 euro?"
    print(detector.get_intent(richiesta))        