# agente_finale.py
"""
AGENTE AI IMMOBILIARE COMPLETO
Gestisce: parsing → modello → risposta
"""

import re
import numpy as np
from typing import Optional, Tuple

# ==================== 1. MODELLO PREDITTIVO ====================
class ModelloPrezziCase:
    """Modello per predire prezzi immobiliari"""
    
    def __init__(self):
        # Parametri del modello (potrebbero venire da un training)
        self.intercetta = 30.0    # prezzo base (migliaia di €)
        self.coeff_metro = 2.8    # coefficiente per m²
        self.coeff_stanza = 18.0  # coefficiente per stanza
        
    def predici(self, metratura: float, stanze: int) -> float:
        """Predice il prezzo in migliaia di €"""
        prezzo = (
            self.intercetta +
            self.coeff_metro * metratura +
            self.coeff_stanza * stanze
        )
        return prezzo
    
    def spiegazione(self, metratura: float, stanze: int) -> str:
        """Restituisce spiegazione del calcolo"""
        return (
            f"{self.intercetta:.1f} (base) + "
            f"{self.coeff_metro:.1f}×{metratura} (metri) + "
            f"{self.coeff_stanza:.1f}×{stanze} (stanze) = "
        )

# ==================== 2. PARSER LINGUAGGIO NATURALE ====================
class ParserDomande:
    """Estrae informazioni da domande in linguaggio naturale"""
    
    @staticmethod
    def normalizza_testo(testo: str) -> str:
        """Normalizza il testo per il parsing"""
        testo = testo.lower()
        # Sostituisce abbreviazioni comuni
        sostituzioni = {
            'mq': 'm²',
            'metri quadri': 'm²',
            'metri quadrati': 'm²',
            'camere': 'stanze',
            'locali': 'stanze',
            'locale': 'stanza'
        }
        for vecchio, nuovo in sostituzioni.items():
            testo = testo.replace(vecchio, nuovo)
        return testo
    
    @staticmethod
    def estrai_coppie_numeriche(testo: str) -> list:
        """Estrae coppie (tipo, valore) dal testo"""
        testo = ParserDomande.normalizza_testo(testo)
        
        coppie = []
        
        # Pattern per metratura
        pattern_metro = r'(\d+)\s*(?:m²|m\s*quadri|metri)'
        matches = re.finditer(pattern_metro, testo)
        for match in matches:
            coppie.append(('metro', int(match.group(1))))
        
        # Pattern per stanze
        pattern_stanze = r'(\d+)\s*stanze?'
        matches = re.finditer(pattern_stanze, testo)
        for match in matches:
            coppie.append(('stanza', int(match.group(1))))
        
        return coppie
    
    @staticmethod
    def parse(domanda: str) -> Tuple[Optional[float], Optional[int]]:
        """Estrae metratura e stanze dalla domanda"""
        coppie = ParserDomande.estrai_coppie_numeriche(domanda)
        
        metratura = None
        stanze = None
        
        for tipo, valore in coppie:
            if tipo == 'metro':
                metratura = float(valore)
            elif tipo == 'stanza':
                stanze = int(valore)
        
        # Fallback: cerca numeri generici
        if metratura is None or stanze is None:
            numeri = re.findall(r'\b\d+\b', domanda)
            numeri = [int(n) for n in numeri]
            
            if len(numeri) >= 2:
                # Ordiniamo e assumiamo: più grande = metratura, più piccolo = stanze
                numeri.sort()
                if metratura is None:
                    metratura = float(numeri[-1])  # il più grande
                if stanze is None:
                    stanze = numeri[0]  # il più piccolo
        
        return metratura, stanze

# ==================== 3. GENERATORE RISPOSTE ====================
class GeneratoreRisposte:
    """Genera risposte in linguaggio naturale"""
    
    @staticmethod
    def genera(metratura: float, stanze: int, prezzo: float) -> str:
        """Genera una risposta personalizzata"""
        
        # Template di base
        template_base = (
            f"🏠 **Stima Immobiliare**\n"
            f"Metratura: {metratura:.0f}m²\n"
            f"Stanze: {stanze}\n"
            f"Prezzo stimato: **€{prezzo:.0f}.000**\n\n"
        )
        
        # Aggiungi contesto basato sul prezzo
        if prezzo < 300:
            contesto = "💰 Questa rientra nella fascia economica del mercato."
        elif prezzo < 500:
            contesto = "💰 Prezzo nella media di mercato."
        else:
            contesto = "💰 Fascia alta del mercato, probabilmente un immobile di pregio."
        
        # Aggiungi consiglio se i parametri sono estremi
        consiglio = ""
        if metratura > 200:
            consiglio += "⚠️ Metratura molto elevata, verifica la zona.\n"
        if stanze > 5:
            consiglio += "⚠️ Numero di stanze insolito per un'abitazione standard.\n"
        
        return template_base + contesto + ("\n" + consiglio if consiglio else "")

# ==================== 4. AGENTE PRINCIPALE ====================
class AgenteImmobiliareAI:
    """Agente AI completo"""
    
    def __init__(self):
        self.modello = ModelloPrezziCase()
        self.parser = ParserDomande()
        self.generatore = GeneratoreRisposte()
        self.storico = []
    
    def processa(self, domanda: str) -> str:
        """Processa una domanda e restituisce risposta"""
        
        # Salva nel storico
        self.storico.append(f"Utente: {domanda}")
        
        # 1. Parsing
        metratura, stanze = self.parser.parse(domanda)
        
        # 2. Validazione
        if metratura is None or stanze is None:
            risposta = (
                "🤔 Non ho trovato tutti i dati necessari.\n"
                "Per favore, specifica sia la metratura che il numero di stanze.\n"
                "Esempio: '120m² 5 stanze' o 'casa di 100 metri con 3 camere'"
            )
        else:
            # 3. Predizione
            prezzo = self.modello.predici(metratura, stanze)
            
            # 4. Generazione risposta
            risposta = self.generatore.genera(metratura, stanze, prezzo)
        
        # Salva risposta nel storico
        self.storico.append(f"AI: {risposta[:50]}...")
        
        return risposta
    
    def mostra_storico(self):
        """Mostra storico conversazione"""
        if not self.storico:
            print("Nessuna conversazione registrata.")
            return
        
        print("\n" + "="*60)
        print("📜 STORICO CONVERSAZIONE")
        print("="*60)
        for messaggio in self.storico[-6:]:  # Ultimi 3 scambi
            print(messaggio)
            print("-"*40)

# ==================== 5. INTERFACCIA UTENTE ====================
def interfaccia_test():
    """Interfaccia di test per l'agente"""
    
    agente = AgenteImmobiliareAI()
    
    print("="*70)
    print("🤖 AGENTE AI IMMOBILIARE - TEST INTERATTIVO")
    print("="*70)
    print("\nComandi:")
    print("  'storico' - Mostra ultime risposte")
    print("  'esci'    - Termina il programma")
    print("\n" + "-"*70)
    
    # Test automatico con la TUA domanda
    tua_domanda = "per una casa di 120m quadri e con 5 stanze qual è il prezzo finale?"
    print(f"\n🧪 Test automatico con la tua domanda:")
    print(f"   '{tua_domanda}'")
    print(f"\n   Risposta:")
    risposta_test = agente.processa(tua_domanda)
    print(f"   {risposta_test}")
    print("-"*70)
    
    # Chat interattiva
    print("\n💬 Ora puoi fare altre domande:")
    
    while True:
        try:
            domanda = input("\nTu: ").strip()
            
            if domanda.lower() in ['esci', 'exit', 'quit']:
                print("Arrivederci! 👋")
                break
            
            if domanda.lower() == 'storico':
                agente.mostra_storico()
                continue
            
            if not domanda:
                continue
            
            risposta = agente.processa(domanda)
            print(f"\n🤖 AI: {risposta}")
            
        except KeyboardInterrupt:
            print("\n\nProgramma interrotto.")
            break
        except Exception as e:
            print(f"\n❌ Errore: {e}")

# ==================== 6. ESECUZIONE ====================
if __name__ == "__main__":
    interfaccia_test()