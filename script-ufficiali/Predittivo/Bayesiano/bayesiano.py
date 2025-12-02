import pandas as pd
import numpy as np
from collections import defaultdict
import math

# ============================================
# 1. DATI DI TRAINING (Email etichettate)
# ============================================

# Creiamo un piccolo dataset di email
emails = [
    # EMAIL SPAM
    ("vinci gratis ora premio soldi", "spam"),
    ("offerta limitata compra subito", "spam"),
    ("guadagna facilmente da casa", "spam"),
    ("prestito immediato senza documenti", "spam"),
    ("pillole miracolose perdita peso", "spam"),
    
    # EMAIL HAM (non-spam)
    ("riunione progetto domani mattina", "ham"),
    ("cena stasera con amici ristorante", "ham"),
    ("rapporto vendite trimestre scorso", "ham"),
    ("riunione famiglia domenica pranzo", "ham"),
    ("presentazione cliente importante venerdì", "ham"),
]

# Convertiamo in DataFrame per comodità
df = pd.DataFrame(emails, columns=['testo', 'classe'])
print("📧 DATASET EMAIL:")
print(df)
print("\n" + "="*60 + "\n")

# ============================================
# 2. CLASSE NAIVE BAYES (Implementazione passo-passo)
# ============================================

class NaiveBayesSpamFilter:
    def __init__(self):
        # Dizionari per memorizzare le probabilità
        self.prior_prob = {}  # P(classe)
        self.word_prob = {}   # P(parola|classe)
        self.vocabulary = set()
        self.total_docs = 0
        
    def train(self, emails):
        """Addestra il modello sulle email etichettate"""
        
        # Conta i documenti per classe
        class_counts = defaultdict(int)
        word_counts = defaultdict(lambda: defaultdict(int))

#-------------------------TODO---------------------------------        
#aggiungi +1 pe vedere quante email sono spam e quante sono ham
#perchè alla fine devi calcolare la probabilità
#P(spam) = (numero email spam) / (totale email)
#P(ham) = (numero email ham) / (totale email)
#-------------------------------------------------------------

        # 1. Conta documenti e parole
        for testo, classe in emails:
            class_counts[classe] += 1
            self.total_docs += 1
            
            # Tokenizzazione semplice (split su spazi)
            parole = testo.lower().split()
            
            # Aggiungi parole al vocabolario
            #per contare quante volte appare una parola in una classe
            for parola in parole:
                self.vocabulary.add(parola)
                word_counts[classe][parola] += 1
        
        # 2. Calcola PROBABILITÀ A PRIORI: P(classe)
        # P(classe) = (documenti in classe) / (documenti totali)
        for classe, count in class_counts.items():
            self.prior_prob[classe] = count / self.total_docs
        
        # 3. Calcola PROBABILITÀ CONDIZIONATE: P(parola|classe)
        # Con smoothing di Laplace (per evitare probabilità = 0)
        # P(parola|classe) = (conteggio(parola,classe) + 1) / (conteggio_totale(classe) + |vocabolario|)
        for classe in class_counts.keys():
            self.word_prob[classe] = {}
            total_words_in_class = sum(word_counts[classe].values())
            
            for parola in self.vocabulary:
                conteggio = word_counts[classe].get(parola, 0)
                # Smoothing di Laplace: aggiungiamo 1 al numeratore e |V| al denominatore
                prob = (conteggio + 1) / (total_words_in_class + len(self.vocabulary))
                self.word_prob[classe][parola] = prob
        
        print("✅ MODELLO ADDESTRATO!")
        print(f"Vocabolario: {len(self.vocabulary)} parole")
        print(f"P(spam) = {self.prior_prob.get('spam', 0):.3f}")
        print(f"P(ham) = {self.prior_prob.get('ham', 0):.3f}")
        
    def predict(self, testo):
        """Predice se un'email è spam o ham"""
        
        parole = testo.lower().split()
        
        # Inizializza i punteggi logaritmici per evitare underflow numerico
        scores = {}
        
        # Per ogni classe (spam, ham), calcola: log(P(classe)) + Σ log(P(parola|classe))
        for classe in self.prior_prob.keys():
            # Inizia con il logaritmo della probabilità a priori
            score = math.log(self.prior_prob[classe])
            
            # Somma i logaritmi delle probabilità delle parole
            for parola in parole:
                if parola in self.vocabulary:
                    prob_parola = self.word_prob[classe][parola]
                    score += math.log(prob_parola)
                else:
                    # Se la parola non è nel vocabolario, usiamo una probabilità piccola
                    score += math.log(1 / (len(self.vocabulary) + 1))
            
            scores[classe] = score
        
        # Trova la classe con il punteggio più alto
        classe_predetta = max(scores, key=scores.get)
        
        # Calcola probabilità normalizzate (opzionale, per interpretazione)
        # Esponenzia i punteggi e normalizza
        exp_scores = {k: math.exp(v) for k, v in scores.items()}
        total = sum(exp_scores.values())
        prob_finali = {k: v/total for k, v in exp_scores.items()}
        
        return classe_predetta, prob_finali
    
    def explain_prediction(self, testo):
        """Spiega la predizione mostrando le parole più influenti"""
        print(f"\n🔍 ANALISI EMAIL: '{testo}'")
        
        parole = testo.lower().split()
        parole_rilevanti = [p for p in parole if p in self.vocabulary]
        
        if not parole_rilevanti:
            print("Nessuna parola conosciuta nel vocabolario!")
            return
        
        print("\nParole rilevanti trovate:")
        for parola in parole_rilevanti:
            prob_spam = self.word_prob['spam'][parola]
            prob_ham = self.word_prob['ham'][parola]
            
            # Calcola il rapporto di probabilità (evidence ratio)
            if prob_ham > 0:
                ratio = prob_spam / prob_ham
                evidenza = "SPAM" if ratio > 1 else "HAM"
                print(f"  '{parola}': P(spam|parola)={prob_spam:.4f}, P(ham|parola)={prob_ham:.4f} → {evidenza} (ratio: {ratio:.2f})")

# ============================================
# 3. ADDESTRAMENTO DEL MODELLO
# ============================================

print("🤖 ADDESTRAMENTO FILTRO BAYESIANO ANTI-SPAM")
print("="*60)

# Creiamo e addestriamo il modello
model = NaiveBayesSpamFilter()
model.train(emails)

# ============================================
# 4. TESTIAMO CON NUOVE EMAIL
# ============================================

print("\n" + "="*60)
print("🧪 TEST CON EMAIL NUOVE")
print("="*60)

test_emails = [
    ("vinci un premio ora subito", "SPAM - parole sospette"),
    ("riunione importante domani ufficio", "HAM - lavoro"),
    ("compra pillole miracolose gratis", "SPAM - combinazione sospetta"),
    ("cena domani sera con colleghi", "HAM - sociale"),
    ("guadagna soldi facilmente da casa tua", "SPAM - classico"),
    ("rapporto mensile progetti in corso", "HAM - lavoro"),
]

for testo, descrizione in test_emails:
    predizione, probabilità = model.predict(testo)
    print(f"\n📩 Email: '{testo}'")
    print(f"   Descrizione: {descrizione}")
    print(f"   🔮 Predizione: {predizione.upper()}")
    print(f"   📊 Probabilità: Spam={probabilità['spam']:.1%}, Ham={probabilità['ham']:.1%}")
    
    # Spiegazione dettagliata per alcune email
    if "miracolose" in testo or "premio" in testo:
        model.explain_prediction(testo)

# ============================================
# 5. ANALISI DELLE PROBABILITÀ APPRESE
# ============================================

print("\n" + "="*60)
print("📊 ANALISI PROBABILITÀ PAROLE CHIAVE")
print("="*60)

# Parole interessanti da analizzare
parole_interessanti = ['gratis', 'vinci', 'riunione', 'cena', 'soldi', 'progetto']

print("\nProbabilità P(parola|classe):")
print("Parola          | P(spam|parola) | P(ham|parola) | Evidenza")
print("-" * 60)

for parola in parole_interessanti:
    if parola in model.vocabulary:
        p_spam = model.word_prob['spam'][parola]
        p_ham = model.word_prob['ham'][parola]
        ratio = p_spam / p_ham if p_ham > 0 else float('inf')
        evidenza = "→ SPAM" if ratio > 1.5 else "→ HAM" if ratio < 0.67 else "→ Neutrale"
        print(f"{parola:15} | {p_spam:13.4f} | {p_ham:12.4f} | {evidenza} (ratio: {ratio:.2f})")

# ============================================
# 6. ESEMPIO VISIVO: COME BAYES "RAGIONA"
# ============================================

print("\n" + "="*60)
print("🧠 SIMULAZIONE RAGIONAMENTO BAYESIANO")
print("="*60)

def simulazione_bayes(testo_email):
    """Mostra il calcolo Bayesiano passo-passo"""
    
    print(f"\n📝 Analizziamo: '{testo_email}'")
    
    # Parole nell'email
    parole = testo_email.lower().split()
    
    # Dati dal nostro modello (approssimati per chiarezza)
    # Probabilità a priori dal nostro dataset
    P_spam = 0.5  # Nel nostro dataset: 5 spam, 5 ham
    P_ham = 0.5
    
    print(f"\n1. PROBABILITÀ A PRIORI (prima di leggere l'email):")
    print(f"   P(spam) = {P_spam:.2f} (50%)")
    print(f"   P(ham) = {P_ham:.2f} (50%)")
    
    print(f"\n2. ANALIZZIAMO OGNI PAROLA:")
    
    # Per semplicità, usiamo stime approssimate
    probabilità_parole = {
        'gratis': {'spam': 0.3, 'ham': 0.01},
        'vinci': {'spam': 0.25, 'ham': 0.01},
        'riunione': {'spam': 0.01, 'ham': 0.2},
        'cena': {'spam': 0.01, 'ham': 0.15},
    }
    
    P_spam_data = P_spam
    P_ham_data = P_ham
    
    for parola in parole:
        if parola in probabilità_parole:
            P_parola_spam = probabilità_parole[parola]['spam']
            P_parola_ham = probabilità_parole[parola]['ham']
            
            print(f"\n   Parola '{parola}':")
            print(f"   - P('{parola}'|spam) = {P_parola_spam:.3f}")
            print(f"   - P('{parola}'|ham) = {P_parola_ham:.3f}")
            
            # Aggiorniamo le probabilità (forma semplificata)
            P_spam_data *= P_parola_spam
            P_ham_data *= P_parola_ham
            
    # Normalizziamo
    totale = P_spam_data + P_ham_data
    if totale > 0:
        P_spam_finale = P_spam_data / totale
        P_ham_finale = P_ham_data / totale
        
        print(f"\n3. PROBABILITÀ FINALI (dopo aver letto l'email):")
        print(f"   P(spam|email) = {P_spam_finale:.1%}")
        print(f"   P(ham|email) = {P_ham_finale:.1%}")
        
        if P_spam_finale > 0.5:
            print(f"\n🎯 CONCLUSIONE: Email classificata come SPAM ({P_spam_finale:.1%} probabilità)")
        else:
            print(f"\n🎯 CONCLUSIONE: Email classificata come HAM ({P_ham_finale:.1%} probabilità)")

# Testiamo con un esempio
simulazione_bayes("vinci gratis ora")

# ============================================
# 7. INTERFACCIA INTERATTIVA SEMPLICE
# ============================================

print("\n" + "="*60)
print("💬 PROVA IL FILTRO CON LE TUE EMAIL")
print("="*60)

while True:
    user_email = input("\nInserisci un'email da testare (o 'exit' per uscire): ")
    
    if user_email.lower() == 'exit':
        print("Arrivederci!")
        break
    
    predizione, probabilità = model.predict(user_email)
    print(f"\n📊 RISULTATO:")
    print(f"   Email: '{user_email}'")
    print(f"   📨 Classificazione: {predizione.upper()}")
    print(f"   📈 Probabilità: Spam={probabilità['spam']:.1%}, Ham={probabilità['ham']:.1%}")
    
    if input("\nVuoi vedere l'analisi dettagliata? (s/n): ").lower() == 's':
        model.explain_prediction(user_email)