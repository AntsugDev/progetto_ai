# agent/slot_extractor.py

import re

class SlotExtractor:

    def extract(self, message: str) -> dict:
        """
        Estrae reddito, importo, rate, spese e percentuali dal messaggio.
        Restituisce solo gli slot trovati.
        """
        msg = message.lower()
        slots = {}

        # Estrae tutti i numeri
        numeri = [int(n) for n in re.findall(r"\d+", msg)]

        # --- Mappa per assegnare numeri ---
        # REDDITO
        if re.search(r"reddito|stipendio|prendo|guadagno|entrate", msg):
            match = re.search(r"(reddito|stipendio|prendo|guadagno).*?(\d+)", msg)
            if match:
                slots["reddito"] = int(match.group(2))

        # SPESE
        if re.search(r"spese|uscite|costi", msg):
            match = re.search(r"(spese|uscite|costi).*?(\d+)", msg)
            if match:
                slots["altre_spese"] = int(match.group(2))

        # NUMERO RATE
        if re.search(r"rate|mesi|rate mensili", msg):
            match = re.search(r"(rate|mesi|mensili).*?(\d+)", msg)
            if match:
                slots["nr_rate"] = int(match.group(2))
            else:
                # fallback se non trovato direttamente
                for n in numeri:
                    if 6 <= n <= 120:  # range classico dei finanziamenti
                        slots["nr_rate"] = n

        # IMPORTO RICHIESTO
        if re.search(r"prestito|finanziamento|richiedo|voglio|serve|importo", msg):
            match = re.search(r"(prestito|finanziamento|richiedo|voglio|serve|importo).*?(\d+)", msg)
            if match:
                slots["request"] = int(match.group(2))
            else:
                # fallback: numero più alto tra quelli trovati
                if numeri:
                    slots["request"] = max(numeri)

        # PERCENTUALI
        match_percent = re.search(r"(\d+)%", msg)
        if match_percent:
            slots["percentuale"] = int(match_percent.group(1))

        return slots
