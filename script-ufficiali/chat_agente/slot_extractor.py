import re

class SlotExtractor:
    def normalize_number(self, testo: str):
        pattern = r"([\d.,]+)\s*(mila|k|mil(?:e|ioni?)?|mil(?:iard(?:e|i)?)?)"
    
    # Cerca tutte le occorrenze
        matches = list(re.finditer(pattern, testo, re.IGNORECASE))
    
    # Per ogni match, calcola il valore e prepara la sostituzione
        sostituzioni = []
    
        for match in matches:
            numero_str = match.group(1)
            unita = match.group(2).lower()
            parola_completa = match.group(0)
            
            # Converti il numero stringa in float
            numero = float(numero_str.replace(',', '.'))
            
            # Converti in base all'unità
            if unita in ['k', 'mila']:
                valore = numero * 1000
            elif 'milion' in unita:
                valore = numero * 1000000
            elif 'miliard' in unita:
                valore = numero * 1000000000
            else:
                valore = numero
            
            sostituzioni.append((parola_completa, str(int(valore))))
    
    # Applica le sostituzioni (dalla più lunga alla più corta per evitare problemi)
        testo_modificato = testo
        for parola_vecchia, parola_nuova in sorted(sostituzioni, key=lambda x: len(x[0]), reverse=True):
            testo_modificato = testo_modificato.replace(parola_vecchia, parola_nuova)
    
        return testo_modificato

        # ---- TODO 5) numeri scritti in lettere (base)
       #text_map = {
       #    "mille": 1000,
       #    "duemila": 2000,
       #    "tremila": 3000,
       #    "quattromila": 4000,
       #    "cinquemila": 5000,
       #    "seimila": 6000,
       #    "settemila": 7000,
       #    "ottomila": 8000,
       #    "novemila": 9000,
       #    "diecimila": 10000
       #}

       #if text in text_map:
       #    return text_map[text]

       ## ---- 6) numero normale
        try:
            return text
        except:
            print(f"[WARN] impossibile convertire la stringa iniziale")
            return None

    def extract(self, msg: str) -> dict:
        msg = self.normalize_number(msg)
    
        slots = {
            "reddito": None,
            "altre_spese": None,
            "request": None,
            "nr_rate": None,
            "importo_rata": None
        }
    
        # 1. Prima cerchiamo tutti i numeri con contesto
        patterns = {
            "reddito": r"(?:reddito|stipendio|guadagno|prendo).*?(?:di\s*)?([\d.,]+)(?:\s*euro|mila|milioni|k)?",
            "altre_spese": r"(?:spese|uscite|costo\s+fisso|spese\s+mensile|spese\s+fisse|spesa).*?([\d.,]+)(?:\s*euro|mila|milioni|k)?",
            "request": r"(?:prestito|finanziamento|importo|richiest[ao]).*?(?:di\s*)?([\d.,]+)(?:\s*euro|mila|milioni|k)?",
            "nr_rate": r"(?:rate|mesi|mensilit[àa]).*?(\d+)",
            "importo_rata": r"(?:importo\s+rata|importo|rata\s*(?:mensile|di)?).*?([\d.,]+)(?:\s*euro|mila|milioni|k)?"
        }
        new_slots = {
            'reddito':[],
            'altre_spese':[],
            'request':[],
            'nr_rate':[],
            'importo_rata':[]
        }
        for key, pattern in patterns.items():
            matches = re.findall(pattern, msg)
            for val in matches:
                val = val.replace(",", ".")
                new_slots[key].append(float(val) if key != "nr_rate" else int(val))
            
            # m = re.search(pattern, msg)
            #if m:
            #    valore = m.group(1)
            #    slots[key].append(float(val) if key != "nr_rate" else int(val))
            
        ambiguous = any(len(v) > 1 for v in new_slots.values() if v)
        all_numbers = re.findall(r"\d+", msg)
        recognized = [str(int(v[0])) if isinstance(v, list) else str(int(v))
                      for v in new_slots.values() if v]

        unrecognized = [n for n in all_numbers if n not in recognized]

        
        return {
            "slots": {k: v[0] if v and len(v) == 1 else  v for k, v in new_slots.items()},
            "ambiguous": ambiguous or len(unrecognized) > 0,
            "unrecognized_numbers": unrecognized
        }


if __name__ == "__main__":
    print("-"*80)
    print("Prova di slot extractor ...\n")
    extractor = SlotExtractor()
    richiesta = "è consigliabile un prestito di 5.2 mila euro per una rata mensile di 250 euro e con un reddito di 1245 euro?"
    #richiesta = "voglio pagare 200 per 24"
    slots = extractor.extract(richiesta)
    print(slots)        
