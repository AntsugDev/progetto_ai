"""
🍪 ESEMPIO BAYESIANO COMPLETO: Le Scatole di Biscotti

SCENARIO:
- Scatola ROSSA: 30 biscotti cioccolato, 10 biscotti vaniglia
- Scatola BLU: 20 biscotti cioccolato, 20 biscotti vaniglia

Problema: Prendi un biscotto a caso, è alla VANIGLIA.
Qual è la probabilità che venga dalla Scatola ROSSA?
"""

# ============================================
# 1. CONFIGURAZIONE INIZIALE
# ============================================

print("=" * 70)
print("🍪 ESEMPIO BAYES: LE SCATOLE DI BISCOTTI")
print("=" * 70)

# Definiamo le scatole
scatola_rossa = {
    'nome': 'Scatola Rossa',
    'cioccolato': 30,
    'vaniglia': 10,
    'totale': 40
}

scatola_blu = {
    'nome': 'Scatola Blu',
    'cioccolato': 20,
    'vaniglia': 20,
    'totale': 40
}

# Visualizziamo le scatole
print("\n📦 CONTENUTO SCATOLE:")
print(f"\n{scatola_rossa['nome']}:")
print(f"  - Cioccolato: {scatola_rossa['cioccolato']} biscotti")
print(f"  - Vaniglia: {scatola_rossa['vaniglia']} biscotti")
print(f"  - TOTALE: {scatola_rossa['totale']} biscotti")

print(f"\n{scatola_blu['nome']}:")
print(f"  - Cioccolato: {scatola_blu['cioccolato']} biscotti")
print(f"  - Vaniglia: {scatola_blu['vaniglia']} biscotti")
print(f"  - TOTALE: {scatola_blu['totale']} biscotti")

# ============================================
# 2. PROBABILITÀ SEMPLICI (FACILI)
# ============================================

print("\n" + "=" * 70)
print("📊 PASSO 1: PROBABILITÀ SEMPLICI")
print("=" * 70)

# Probabilità di scegliere ogni scatola (a priori)
# Supponiamo di scegliere la scatola a caso (50/50)
P_scatola_rossa = 0.5  # 50%
P_scatola_blu = 0.5    # 50%

print(f"\n🎲 Probabilità di scegliere ogni scatola (prima di prendere il biscotto):")
print(f"  P(Scatola Rossa) = {P_scatola_rossa:.1f} ({P_scatola_rossa*100:.0f}%)")
print(f"  P(Scatola Blu)   = {P_scatola_blu:.1f} ({P_scatola_blu*100:.0f}%)")

# Probabilità di prendere un biscotto alla vaniglia DA OGNI SCATOLA
P_vaniglia_dato_rossa = scatola_rossa['vaniglia'] / scatola_rossa['totale']
P_vaniglia_dato_blu = scatola_blu['vaniglia'] / scatola_blu['totale']

print(f"\n🍦 Probabilità di prendere vaniglia DA OGNI SCATOLA:")
print(f"  P(Vaniglia | Scatola Rossa) = {scatola_rossa['vaniglia']}/{scatola_rossa['totale']} = {P_vaniglia_dato_rossa:.3f}")
print(f"  P(Vaniglia | Scatola Blu)   = {scatola_blu['vaniglia']}/{scatola_blu['totale']} = {P_vaniglia_dato_blu:.3f}")

# ============================================
# 3. PROBABILITÀ TOTALE DI VANIGLIA
# ============================================

print("\n" + "=" * 70)
print("🧮 PASSO 2: PROBABILITÀ TOTALE DI VANIGLIA")
print("=" * 70)

"""
La probabilità totale di prendere un biscotto alla vaniglia 
considerando TUTTE le possibilità:

1. Scegli scatola rossa E prendi vaniglia: P(rossa) × P(vaniglia|rossa)
2. Scegli scatola blu E prendi vaniglia:   P(blu) × P(vaniglia|blu)

P(Vaniglia) = P(Vaniglia|Rossa)×P(Rossa) + P(Vaniglia|Blu)×P(Blu)
"""

P_vaniglia_totale = (P_vaniglia_dato_rossa * P_scatola_rossa) + (P_vaniglia_dato_blu * P_scatola_blu)

print(f"\n🌍 Probabilità TOTALE di prendere vaniglia (da qualsiasi scatola):")
print(f"\n  P(Vaniglia) = [P(Vaniglia|Rossa) × P(Rossa)] + [P(Vaniglia|Blu) × P(Blu)]")
print(f"              = [{P_vaniglia_dato_rossa:.3f} × {P_scatola_rossa:.1f}] + [{P_vaniglia_dato_blu:.3f} × {P_scatola_blu:.1f}]")
print(f"              = {P_vaniglia_dato_rossa * P_scatola_rossa:.3f} + {P_vaniglia_dato_blu * P_scatola_blu:.3f}")
print(f"              = {P_vaniglia_totale:.3f}")

# ============================================
# 4. APPLICAZIONE TEOREMA DI BAYES
# ============================================

print("\n" + "=" * 70)
print("🎯 PASSO 3: APPLICAZIONE TEOREMA DI BAYES")
print("=" * 70)

"""
TEOREMA DI BAYES:
                         P(Vaniglia | Scatola Rossa) × P(Scatola Rossa)
P(Scatola Rossa | Vaniglia) = ──────────────────────────────────────────────
                                         P(Vaniglia)
"""

# Calcoliamo la probabilità che il biscotto venga dalla Scatola Rossa
# dato che abbiamo osservato che è alla vaniglia
P_rossa_dato_vaniglia = (P_vaniglia_dato_rossa * P_scatola_rossa) / P_vaniglia_totale

print(f"\n🔍 VOGLIAMO SAPERE: Dato che il biscotto è alla VANIGLIA,")
print(f"   qual è la probabilità che venga dalla SCATOLA ROSSA?\n")

print(f"   TEOREMA DI BAYES:")
print(f"   P(Scatola Rossa | Vaniglia) = ")
print(f"       [P(Vaniglia | Scatola Rossa) × P(Scatola Rossa)]")
print(f"       -----------------------------------------------")
print(f"                    P(Vaniglia)")
print()

print(f"   SOSTITUIAMO I VALORI:")
print(f"   P(Rossa | Vaniglia) = [{P_vaniglia_dato_rossa:.3f} × {P_scatola_rossa:.1f}] / {P_vaniglia_totale:.3f}")
print(f"                       = {P_vaniglia_dato_rossa * P_scatola_rossa:.3f} / {P_vaniglia_totale:.3f}")
print(f"                       = {P_rossa_dato_vaniglia:.3f}")

# Probabilità per la scatola blu (per confronto)
P_blu_dato_vaniglia = (P_vaniglia_dato_blu * P_scatola_blu) / P_vaniglia_totale

print(f"\n   Per completezza, calcoliamo anche per la scatola blu:")
print(f"   P(Blu | Vaniglia) = [{P_vaniglia_dato_blu:.3f} × {P_scatola_blu:.1f}] / {P_vaniglia_totale:.3f}")
print(f"                     = {P_vaniglia_dato_blu * P_scatola_blu:.3f} / {P_vaniglia_totale:.3f}")
print(f"                     = {P_blu_dato_vaniglia:.3f}")

# ============================================
# 5. VISUALIZZAZIONE DEI RISULTATI
# ============================================

print("\n" + "=" * 70)
print("📈 PASSO 4: INTERPRETAZIONE DEI RISULTATI")
print("=" * 70)

print(f"\n🎲 RISULTATI FINALI:")
print(f"\n  PRIMA di vedere il biscotto (probabilità a priori):")
print(f"    • P(Scatola Rossa) = {P_scatola_rossa*100:.1f}%")
print(f"    • P(Scatola Blu)   = {P_scatola_blu*100:.1f}%")

print(f"\n  DOPO aver visto che il biscotto è alla VANIGLIA (probabilità a posteriori):")
print(f"    • P(Scatola Rossa | Vaniglia) = {P_rossa_dato_vaniglia*100:.1f}%")
print(f"    • P(Scatola Blu | Vaniglia)   = {P_blu_dato_vaniglia*100:.1f}%")

print(f"\n🔍 COSA È SUCCESSO?")
print(f"  La probabilità della Scatola Rossa è DIMINUITA dal 50% al {P_rossa_dato_vaniglia*100:.1f}%")
print(f"  perché i biscotti alla vaniglia sono più rari nella Scatola Rossa!")

print(f"\n🤔 RAGIONAMENTO INTUITIVO:")
print(f"  1. Se prendo un biscotto a caso, ho il 50% di probabilità per ogni scatola")
print(f"  2. Ma se scopro che è alla vaniglia...")
print(f"     - Nella Scatola Rossa: solo {scatola_rossa['vaniglia']}/{scatola_rossa['totale']} ({P_vaniglia_dato_rossa*100:.1f}%) sono vaniglia")
print(f"     - Nella Scatola Blu:  {scatola_blu['vaniglia']}/{scatola_blu['totale']} ({P_vaniglia_dato_blu*100:.1f}%) sono vaniglia")
print(f"  3. Quindi è più probabile che un biscotto alla vaniglia venga dalla Scatola Blu!")

# ============================================
# 6. SIMULAZIONE PRATICA
# ============================================

print("\n" + "=" * 70)
print("🎪 PASSO 5: SIMULAZIONE CON 1000 ESTRAZIONI")
print("=" * 70)

import random

def simulazione_estrazioni(num_estrazioni=1000):
    """
    Simula l'estrazione di biscotti per verificare le probabilità
    """
    print(f"\nSimuliamo {num_estrazioni} estrazioni casuali...")
    
    contatori = {
        'rossa_vaniglia': 0,
        'blu_vaniglia': 0,
        'totale_vaniglia': 0
    }
    
    for i in range(num_estrazioni):
        # 1. Scegli scatola a caso (50/50)
        scatola = random.choice(['rossa', 'blu'])
        
        # 2. Scegli biscotto dalla scatola scelta
        if scatola == 'rossa':
            # 30 cioccolato, 10 vaniglia
            biscotto = random.choices(['cioccolato', 'vaniglia'], 
                                     weights=[30, 10])[0]
        else:  # scatola blu
            # 20 cioccolato, 20 vaniglia
            biscotto = random.choices(['cioccolato', 'vaniglia'],
                                     weights=[20, 20])[0]
        
        # 3. Conta solo i biscotti alla vaniglia
        if biscotto == 'vaniglia':
            contatori['totale_vaniglia'] += 1
            if scatola == 'rossa':
                contatori['rossa_vaniglia'] += 1
            else:
                contatori['blu_vaniglia'] += 1
    
    # Calcola probabilità empiriche
    if contatori['totale_vaniglia'] > 0:
        P_rossa_empirica = contatori['rossa_vaniglia'] / contatori['totale_vaniglia']
        P_blu_empirica = contatori['blu_vaniglia'] / contatori['totale_vaniglia']
        
        print(f"\n📊 RISULTATI SIMULAZIONE:")
        print(f"  Biscotti alla vaniglia trovati: {contatori['totale_vaniglia']}")
        print(f"  Di questi:")
        print(f"    • Dalla Scatola Rossa: {contatori['rossa_vaniglia']} ({P_rossa_empirica*100:.1f}%)")
        print(f"    • Dalla Scatola Blu:   {contatori['blu_vaniglia']} ({P_blu_empirica*100:.1f}%)")
        
        print(f"\n🔍 CONFRONTO CON TEORIA:")
        print(f"  Teoria:   P(Rossa|Vaniglia) = {P_rossa_dato_vaniglia*100:.1f}%")
        print(f"  Simulato: P(Rossa|Vaniglia) = {P_rossa_empirica*100:.1f}%")
        print(f"  Differenza: {abs(P_rossa_dato_vaniglia - P_rossa_empirica)*100:.2f}%")

# Esegui la simulazione
simulazione_estrazioni(10000)

# ============================================
# 7. ESPERIMENTO INTERATTIVO
# ============================================

print("\n" + "=" * 70)
print("🎮 PASSO 6: ESPERIMENTO INTERATTIVO")
print("=" * 70)

def esperimento_interattivo():
    """
    Permette all'utente di cambiare i parametri e vedere come cambia Bayes
    """
    print("\n🎛️ MODIFICA I PARAMETTI E VEDI COME CAMBIA BAYES!")
    
    while True:
        print("\n" + "-"*50)
        print("Configura le tue scatole:")
        
        try:
            # Input parametri
            rossa_cioccolato = int(input("Biscotti CIOCCOLATO in Scatola Rossa: ") or "30")
            rossa_vaniglia = int(input("Biscotti VANIGLIA in Scatola Rossa: ") or "10")
            blu_cioccolato = int(input("Biscotti CIOCCOLATO in Scatola Blu: ") or "20")
            blu_vaniglia = int(input("Biscotti VANIGLIA in Scatola Blu: ") or "20")
            
            # Calcoli
            rossa_totale = rossa_cioccolato + rossa_vaniglia
            blu_totale = blu_cioccolato + blu_vaniglia
            
            # Probabilità
            P_vaniglia_rossa = rossa_vaniglia / rossa_totale
            P_vaniglia_blu = blu_vaniglia / blu_totale
            P_rossa = 0.5  # Scelta scatola a caso
            P_blu = 0.5
            
            # Probabilità totale vaniglia
            P_vaniglia_tot = (P_vaniglia_rossa * P_rossa) + (P_vaniglia_blu * P_blu)
            
            # Bayes
            P_rossa_dato_vaniglia = (P_vaniglia_rossa * P_rossa) / P_vaniglia_tot
            
            print(f"\n📊 RISULTATI:")
            print(f"  P(Scatola Rossa | Vaniglia) = {P_rossa_dato_vaniglia*100:.1f}%")
            print(f"  P(Scatola Blu | Vaniglia)   = {(1-P_rossa_dato_vaniglia)*100:.1f}%")
            
            # Interpretazione
            if P_rossa_dato_vaniglia > 0.5:
                print(f"\n🎯 CONCLUSIONE: Se prendi vaniglia, è più probabile che venga dalla Scatola Rossa!")
            elif P_rossa_dato_vaniglia < 0.5:
                print(f"\n🎯 CONCLUSIONE: Se prendi vaniglia, è più probabile che venga dalla Scatola Blu!")
            else:
                print(f"\n🎯 CONCLUSIONE: Non c'è differenza! Vaniglia non ci dà informazioni.")
            
            # Continua?
            continuare = input("\nFare un altro esperimento? (s/n): ").lower()
            if continuare != 's':
                break
                
        except ValueError:
            print("⚠️ Per favore inserisci numeri validi!")
        except ZeroDivisionError:
            print("⚠️ La scatola non può essere vuota!")

# Attiva l'esperimento interattivo
# esperimento_interattivo()  # Decommenta per provare!

# ============================================
# 8. FORMULE IN DIVERSI FORMATI
# ============================================

print("\n" + "=" * 70)
print("📝 PASSO 7: FORMULE IN TUTTI I MODI")
print("=" * 70)

print(f"""
🧮 IL TEOREMA DI BAYES IN DIVERSE NOTAZIONI:

1. NOTAZIONE PROBABILISTICA:
   P(A|B) = [P(B|A) × P(A)] / P(B)

2. CON LE NOSTRE VARIABILI:
   P(ScatolaRossa | Vaniglia) = [P(Vaniglia | ScatolaRossa) × P(ScatolaRossa)] / P(Vaniglia)

3. ESPANDENDO P(Vaniglia):
   P(ScatolaRossa | Vaniglia) = 
        P(Vaniglia | ScatolaRossa) × P(ScatolaRossa)
        ──────────────────────────────────────────────
        P(Vaniglia|Rossa)P(Rossa) + P(Vaniglia|Blu)P(Blu)

4. CON I NUMERI DEL NOSTRO ESEMPIO:
   P(Rossa | Vaniglia) = 
        (10/40) × 0.5
        ──────────────────────
        (10/40)×0.5 + (20/40)×0.5

5. SEMPLIFICATO:
   P(Rossa | Vaniglia) = 
        0.25 × 0.5
        ─────────── = 0.125 / 0.375 = 0.333...
        0.125 + 0.25
""")

# ============================================
# 9. TABELLA RIASSUNTIVA
# ============================================

print("\n" + "=" * 70)
print("📋 PASSO 8: TABELLA RIASSUNTIVA")
print("=" * 70)

# Creiamo una tabella riassuntiva
print(f"""
┌─────────────────────────────────────────────────────┐
│                  📊 RIEPILOGO BAYES                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  SCENARIO INIZIALE:                                 │
│  • Scatola Rossa: {scatola_rossa['cioccolato']} cioccolato, {scatola_rossa['vaniglia']} vaniglia │
│  • Scatola Blu:   {scatola_blu['cioccolato']} cioccolato, {scatola_blu['vaniglia']} vaniglia │
│  • Scegli scatola a caso (50/50)                    │
│                                                     │
│  OSSERVAZIONE: Il biscotto estratto è alla VANIGLIA │
│                                                     │
│  CALCOLI:                                           │
│  P(Vaniglia|Rossa) = {scatola_rossa['vaniglia']}/{scatola_rossa['totale']} = {P_vaniglia_dato_rossa:.3f} │
│  P(Vaniglia|Blu)   = {scatola_blu['vaniglia']}/{scatola_blu['totale']} = {P_vaniglia_dato_blu:.3f} │
│  P(Vaniglia) totale = {P_vaniglia_totale:.3f}                          │
│                                                     │
│  RISULTATO BAYES:                                   │
│  P(Rossa|Vaniglia) = {P_rossa_dato_vaniglia:.3f} = {P_rossa_dato_vaniglia*100:.1f}% │
│  P(Blu|Vaniglia)   = {P_blu_dato_vaniglia:.3f} = {P_blu_dato_vaniglia*100:.1f}% │
│                                                     │
│  CONCLUSIONE:                                       │
│  Dato vaniglia, è {P_blu_dato_vaniglia/P_rossa_dato_vaniglia:.1f}x più │
│  probabile che venga dalla Scatola Blu!             │
└─────────────────────────────────────────────────────┘
""")

print("\n" + "=" * 70)
print("🎉 ESERCIZIO CONCLUSO! HAI CAPITO BAYES! 🎉")
print("=" * 70)