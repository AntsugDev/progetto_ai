# script_test_multipli.py
import re
import joblib
import pandas as pd


class ParserIntelligente:
    """Parser più robusto per varie formulazioni"""
    
    @staticmethod
    def estrai_metratura(testo):
        """Estrae metratura da varie formulazioni"""
        testo = testo.lower()
        
        patterns = [
            r'(\d+)\s*m\s*quadri',      # "120m quadri"
            r'(\d+)\s*mq',              # "120mq"
            r'(\d+)\s*m²',              # "120m²"
            r'(\d+)\s*metri quadri',    # "120 metri quadri"
            r'(\d+)\s*metri',           # "120 metri"
            r'di\s*(\d+)\s*m',          # "di 120m"
            r'(\d+)\s*m\s*di',          # "120m di"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, testo)
            if match:
                return int(match.group(1))
        
        return None
    
    @staticmethod
    def estrai_stanze(testo):
        """Estrae numero stanze da varie formulazioni"""
        testo = testo.lower()
        
        patterns = [
            r'(\d+)\s*stanze',          # "5 stanze"
            r'(\d+)\s*camere',          # "5 camere"
            r'(\d+)\s*locali',          # "5 locali"
            r'con\s*(\d+)\s*stanze',    # "con 5 stanze"
            r'di\s*(\d+)\s*stanze',     # "di 5 stanze"
            r'(\d+)\s*stanza',          # "5 stanza"
            r'(\d+)\s*camera',          # "5 camera"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, testo)
            if match:
                return int(match.group(1))
        
        return None
    
    @staticmethod
    def parse(testo):
        """Estrae entrambi i valori"""
        metratura = ParserIntelligente.estrai_metratura(testo)
        stanze = ParserIntelligente.estrai_stanze(testo)
        
        # Se ancora manca qualcosa, cerca numeri generici
        if metratura is None or stanze is None:
            numeri = re.findall(r'\b\d+\b', testo)
            numeri = [int(n) for n in numeri]
            
            if len(numeri) == 2:
                # Distingui per grandezza: il più grande è probabilmente la metratura
                if metratura is None and stanze is None:
                    metratura = max(numeri)
                    stanze = min(numeri)
                elif metratura is None:
                    # Stanze già trovato, cerca metratura tra i numeri
                    for n in numeri:
                        if n != stanze:
                            metratura = n
                            break
                elif stanze is None:
                    # Metratura già trovato, cerca stanze tra i numeri
                    for n in numeri:
                        if n != metratura:
                            stanze = n
                            break
        
        return metratura, stanze

if __name__ == "__main__":

    # Test con varie formulazioni
    test_cases = [
        "per una casa di 120m quadri e con 5 stanze qual è il prezzo finale?",
        "quanto costa una casa di 100 m² con 3 stanze?",
        "prezzo per appartamento 80mq 2 camere",
        "valutazione immobile 150 metri quadri 4 locali",
        "mi serve stima per casa di 90m² con 3 stanze",
        "120m² 5 stanze prezzo?",
        "casa 110 metri 4 camere quanto costa?",
    ]

    print("🧪 TEST VARIE FORMULAZIONI")
    print("="*70)

    parser = ParserIntelligente()
    modello = joblib.load("./pkl/model_ai_chat.pkl")

    for i, domanda in enumerate(test_cases, 1):
        metratura, stanze = parser.parse(domanda)
        df = pd.DataFrame({"metratura": [metratura], "stanze": [stanze]})
        
        result = []
        if metratura and stanze:
            prezzo = modello.predict(df)
            result.append([metratura, stanze, float(prezzo[0])])
        else:
            print(f"✗ Estrazione parziale o fallita:")
        
        df_result = pd.DataFrame(result, columns=["metratura", "stanze", "prezzo"])
        print(df_result)

    print("\n" + "="*70)
    print("✅ Test completati")