"""
🎯 AGENTE AI PREDITTIVO COMPLETO
Teoria e Implementazione Pratica del Random Forest

AUTORE: Assistente AI
DATA: 2024
DESCRIZIONE: Script completo che unisce teoria e pratica
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import matplotlib.pyplot as plt
import warnings
import os
from datetime import datetime

warnings.filterwarnings('ignore')

# =============================================================================
# 🧠 PARTE 1: TEORIA E SPIEGAZIONI
# =============================================================================

class TeoriaRandomForest:
    """
    Classe contenente le spiegazioni teoriche del Random Forest
    """
    
    @staticmethod
    def spiegazione_concetti_base():
        """
        Spiegazione dei concetti fondamentali
        """
        print("=" * 70)
        print("🎯 CONCETTI FONDAMENTALI - AGENTE AI PREDITTIVO")
        print("=" * 70)
        
        concetti = {
            "AGENTE AI PREDITTIVO": [
                "Sistema che analizza dati storici",
                "Identifica pattern e correlazioni", 
                "Costruisce modelli matematici",
                "Genera previsioni su eventi futuri",
                "Si adatta automaticamente ai nuovi dati"
            ],
            
            "RANDOM FOREST": [
                "🌳 Algoritmo di MACHINE LEARNING ENSEMBLE",
                "🤝 Combina MULTIPLI ALBERI DECISIONALI", 
                "🎯 Crea modello più ROBUSTO e ACCURATO",
                "📊 Prevenzione naturale dell'OVERFITTING",
                "🔍 FEATURE IMPORTANCE automatica"
            ],
            
            "ANALOGIA PRATICA": [
                "Singolo albero = UN ESPERTO (può sbagliare)",
                "Random Forest = COMITATO DI ESPERTI",
                "Ogni esperto ha una specializzazione diversa",
                "Decisione finale = VOTO DEMOCRATICO",
                "Risultato più STABILE e AFFIDABILE"
            ]
        }
        
        for titolo, punti in concetti.items():
            print(f"\n📖 {titulo}:")
            for punto in punti:
                print(f"   ✅ {punto}")
    
    @staticmethod
    def spiegazione_features_vs_target():
        """
        Spiegazione della differenza fondamentale tra Features e Target
        """
        print("\n" + "=" * 70)
        print("🎯 FEATURES vs TARGET - LA DIFFERENZA FONDAMENTALE")
        print("=" * 70)
        
        print("""
📝 DEFINIZIONE CHIAVE:
> "Le FEATURES sono i dati che servono per fare una previsione 
> di un risultato TARGET"

🎯 DOMANDA SEMPLICE PER IDENTIFICARE:
> "Questo dato lo conosco PRIMA di dover fare la previsione?"
>   - SÌ → È una FEATURE  
>   - NO → È il TARGET

📊 ESEMPI PRATICI:
""")
        
        esempi = [
            {
                "Scenario": "Previsione Vendite",
                "Features": "Mese, Promozione, Meteo, Evento, Vendite Ieri",
                "Target": "Vendite Oggi"
            },
            {
                "Scenario": "Previsione Meteo", 
                "Features": "Temperatura, Umidità, Pressione, Vento",
                "Target": "Pioverà? (Sì/No)"
            },
            {
                "Scenario": "Prezzo Casa",
                "Features": "Metratura, Quartiere, Anno, Numero Bagni",
                "Target": "Prezzo di Vendita"
            }
        ]
        
        for esempio in esempi:
            print(f"🏷️  {esempio['Scenario']}:")
            print(f"   📥 FEATURES: {esempio['Features']}")
            print(f"   📤 TARGET: {esempio['Target']}")
            print()
    
    @staticmethod
    def spiegazione_file_pkl():
        """
        Spiegazione del file .pkl e sua importanza
        """
        print("\n" + "=" * 70)
        print("💾 FILE .pkl - IL CUORE DEL SISTEMA")
        print("=" * 70)
        
        print("""
COS'È IL FILE .pkl?
> È il MODELLO ADDESTRATO salvato su disco!
> Contiene tutta la CONOSCENZA appresa dai dati

ANALOGIA:
- 📝 Script Python = RICETTA della torta
- 💾 File .pkl = TORTA già cotta e pronta
- 🔧 .fit() = CUCINARE la torta (lento)
- 🎯 .predict() = SERVIRE la torta (veloce)

PERCHÈ SALVARE IL MODELLO?
""")
        
        confronto = {
            "SENZA .pkl (INEFFICIENTE)": [
                "Carica tutti i dati storici",
                "Riprepara le features", 
                "Riallenza il modello (30+ minuti)",
                "Fa la previsione",
                "⏰ TEMPO: 30+ minuti a previsione!"
            ],
            
            "CON .pkl (EFFICIENTE)": [
                "Carica modello già addestrato (1 secondo)",
                "Fa la previsione (0.1 secondi)", 
                "⏰ TEMPO: 1.1 secondi a previsione!"
            ]
        }
        
        for scenario, punti in confronto.items():
            print(f"\n{scenario}:")
            for punto in punti:
                print(f"   ✅ {punto}")

# =============================================================================
# 🏗️ PARTE 2: IMPLEMENTAZIONE PRATICA
# =============================================================================

class PredictiveSalesAgent:
    """
    Agente AI predittivo completo per previsioni vendite
    """
    
    def __init__(self):
        self.model = None
        self.is_trained = False
        self.feature_importance = None
        self.training_columns = None
        self.training_date = None
        
    def spiegazione_metodo(self, nome_metodo):
        """
        Mostra spiegazioni teoriche durante l'esecuzione
        """
        spiegazioni = {
            'generate_sample_data': """
📊 GENERAZIONE DATI DI TRAINING:
- Creazione dati sintetici realistici
- Features: Mese, Promozione, Meteo, Evento, Vendite Precedenti  
- Target: Vendite Giornaliere
- Relazioni non lineari simulate
            """,
            
            'prepare_features': """
🔧 PREPARAZIONE FEATURES (Feature Engineering):
- Separazione chiara Features vs Target
- Creazione interazioni intelligenti:
  * mese_promozione = Mese × Promozione
  * meteo_evento = Meteo × Evento
- Per catturare relazioni complesse
            """,
            
            'train': """
🎯 ALLENAMENTO RANDOM FOREST:
- Split 80/20 (Training/Test)
- Creazione di 100 alberi decisionali
- Ogni albero vede dati leggermente diversi
- Prevenzione naturale overfitting
            """,
            
            'forecast_future': """
🔮 PREVISIONI FUTURE:
- Creazione dati futuri con stessa struttura
- Applicazione pattern appresi
- Restituzione solo risultati numerici
- Nella realtà: interfaccia pulita senza grafici
            """
        }
        
        if nome_metodo in spiegazioni:
            print(spiegazioni[nome_metodo])
    
    def generate_sample_data(self, n_samples=1000):
        """
        Genera dati di esempio realistici per il training
        """
        self.spiegazione_metodo('generate_sample_data')
        
        np.random.seed(42)
        print(f"🔄 Generazione {n_samples} righe di dati...")
        
        # Features (ciò che conosciamo prima)
        data = {
            'mese': np.random.randint(1, 13, n_samples),
            'giorno_settimana': np.random.randint(1, 8, n_samples),
            'promozione': np.random.randint(0, 2, n_samples),
            'prezzo_scontato': np.random.uniform(0.7, 1.0, n_samples),
            'meteo': np.random.randint(1, 5, n_samples),
            'evento_speciale': np.random.randint(0, 2, n_samples),
            'vendite_precedenti': np.random.normal(1000, 200, n_samples)
        }
        
        # Target (ciò che vogliamo prevedere) - con relazioni realistiche
        base_sales = 500
        mese_effect = data['mese'] * 15           # Stagionalità
        promozione_effect = data['promozione'] * 200
        meteo_effect = data['meteo'] * 50
        evento_effect = data['evento_speciale'] * 150
        prezzo_effect = (1 - data['prezzo_scontato']) * 300
        storico_effect = data['vendite_precedenti'] * 0.3
        noise = np.random.normal(0, 50, n_samples)
        
        data['vendite_giornaliere'] = (base_sales + mese_effect + promozione_effect + 
                                     meteo_effect + evento_effect + prezzo_effect + 
                                     storico_effect + noise)
        
        self.df = pd.DataFrame(data)
        print(f"✅ Dati generati: {len(self.df)} righe, {len(self.df.columns)} colonne")
        return self.df
    
    def prepare_features(self, df):
        """
        Prepara le features per il machine learning
        """
        self.spiegazione_metodo('prepare_features')
        
        print("🎯 Separazione Features vs Target...")
        # Features: tutto tranne il target
        X = df.drop('vendite_giornaliere', axis=1)
        # Target: solo ciò che vogliamo prevedere
        y = df['vendite_giornaliere']
        
        print("🔧 Feature Engineering...")
        # Creazione interazioni intelligenti
        X['mese_promozione'] = X['mese'] * X['promozione']
        X['meteo_evento'] = X['meteo'] * X['evento_speciale']
        
        # Salva struttura per consistency
        self.training_columns = X.columns.tolist()
        
        print(f"✅ Features preparate: {len(self.training_columns)} variabili")
        return X, y
    
    def train(self, X, y):
        """
        Addestra il modello Random Forest
        """
        self.spiegazione_metodo('train')
        
        print("📊 Split dati (80% training, 20% test)...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        print("🌳 Creazione Random Forest (100 alberi)...")
        self.model = RandomForestRegressor(
            n_estimators=100,      # Numero di "esperti" nel comitato
            max_depth=10,          # Limite complessità singolo esperto
            random_state=42,       # Riproducibilità
            n_jobs=-1              # Usa tutti i core CPU
        )
        
        print("🎯 Allenamento modello...")
        self.model.fit(X_train, y_train)
        self.is_trained = True
        self.training_date = datetime.now()
        
        # Valutazione performance
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        
        # Feature Importance
        self.feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\n" + "=" * 50)
        print("📈 RISULTATI ALLENAMENTO:")
        print("=" * 50)
        print(f"✅ R² Training: {train_score:.3f}")
        print(f"✅ R² Test:     {test_score:.3f}")
        print(f"✅ MAE:         {mae:.2f} vendite")
        
        return train_score, test_score, mae
    
    def explain_model(self):
        """
        Spiega il modello mostrando feature importance
        """
        if self.feature_importance is None:
            print("❌ Modello non ancora addestrato!")
            return
        
        print("\n" + "=" * 50)
        print("🔍 FEATURE IMPORTANCE - COSA GUIDA LE PREVISIONI")
        print("=" * 50)
        
        for _, row in self.feature_importance.iterrows():
            stars = "⭐" * int(row['importance'] * 20)
            print(f"{row['feature']:20} {row['importance']:.3f} {stars}")
        
        print("\n💡 INTERPRETAZIONE:")
        print("   Le feature più importanti guidano maggiormente le previsioni")
        print("   Es: vendite_precedenti = 51% → il passato è il miglior predittore!")
    
    def predict_single(self, mese, promozione, meteo, evento_speciale, vendite_precedenti):
        """
        Prevede le vendite per un singolo set di input
        (Versione production-like)
        """
        if not self.is_trained:
            raise ValueError("❌ Modello non addestrato!")
        
        # Prepara input nello stesso formato del training
        input_data = {
            'mese': [mese],
            'giorno_settimana': [1],  # Default
            'promozione': [promozione],
            'prezzo_scontato': [1.0],  # Default
            'meteo': [meteo],
            'evento_speciale': [evento_speciale],
            'vendite_precedenti': [vendite_precedenti]
        }
        
        input_df = pd.DataFrame(input_data)
        
        # Applica stesso feature engineering
        input_df['mese_promozione'] = input_df['mese'] * input_df['promozione']
        input_df['meteo_evento'] = input_df['meteo'] * input_df['evento_speciale']
        
        # Ordine colonne consistente
        input_df = input_df[self.training_columns]
        
        # Previsione
        prediction = self.model.predict(input_df)[0]
        
        return round(prediction)
    
    def forecast_future(self, periods=30, show_plot=True):
        """
        Genera previsioni future (con grafico solo per dimostrazione)
        """
        self.spiegazione_metodo('forecast_future')
        
        if not self.is_trained:
            raise ValueError("❌ Modello non addestrato!")
        
        print(f"🔮 Generazione previsioni per {periods} giorni...")
        
        future_data = []
        for i in range(periods):
            future_point = {
                'mese': (i % 12) + 1,
                'giorno_settimana': (i % 7) + 1,
                'promozione': 1 if i % 7 == 0 else 0,
                'prezzo_scontato': 0.9 if i % 7 == 0 else 1.0,
                'meteo': np.random.randint(2, 5),
                'evento_speciale': 1 if i in [5, 15, 25] else 0,
                'vendite_precedenti': 1000 + (i * 10),
            }
            future_data.append(future_point)
        
        future_df = pd.DataFrame(future_data)
        
        # Stesso feature engineering del training
        future_df['mese_promozione'] = future_df['mese'] * future_df['promozione']
        future_df['meteo_evento'] = future_df['meteo'] * future_df['evento_speciale']
        future_df = future_df[self.training_columns]
        
        predictions = self.model.predict(future_df)
        
        # 📊 GRAFICO (SOLO PER DIMOSTRAZIONE - nella realtà non si fa!)
        if show_plot:
            plt.figure(figsize=(12, 6))
            plt.plot(range(periods), predictions, marker='o', linewidth=2, color='blue')
            plt.title('📈 PREVISIONI VENDITE - PROSSIMI 30 GIORNI\n(Dimostrazione - In produzione solo numeri)')
            plt.xlabel('Giorno')
            plt.ylabel('Vendite Previste')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()
        
        print(f"✅ Previsioni generate: media {np.mean(predictions):.0f} vendite/giorno")
        return predictions
    
    def save_model(self, filename='sales_model.pkl'):
        """
        Salva il modello addestrato su disco
        """
        if not self.is_trained:
            raise ValueError("❌ Nessun modello da salvare!")
        
        model_data = {
            'model': self.model,
            'training_columns': self.training_columns,
            'feature_importance': self.feature_importance,
            'training_date': self.training_date,
            'model_type': 'RandomForestRegressor',
            'version': '1.0'
        }
        
        # Crea directory se non esiste
        os.makedirs('models', exist_ok=True)
        model_path = f'models/{filename}'
        
        joblib.dump(model_data, model_path)
        print(f"💾 Modello salvato: {model_path}")
        print(f"📏 Dimensioni: {os.path.getsize(model_path) / 1024 / 1024:.2f} MB")
        
        return model_path
    
    def load_model(self, filename='sales_model.pkl'):
        """
        Carica un modello addestrato da disco
        """
        model_path = f'models/{filename}'
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"❌ File {model_path} non trovato!")
        
        print(f"📂 Caricamento modello da: {model_path}")
        model_data = joblib.load(model_path)
        
        self.model = model_data['model']
        self.training_columns = model_data['training_columns']
        self.feature_importance = model_data['feature_importance']
        self.training_date = model_data['training_date']
        self.is_trained = True
        
        print("✅ Modello caricato con successo!")
        return self

# =============================================================================
# 🏭 PARTE 3: SISTEMA PRODUCTION-READY
# =============================================================================

class ProductionSalesPredictor:
    """
    Versione semplificata per uso in produzione
    (Senza grafici, senza spiegazioni - solo numeri!)
    """
    
    def __init__(self, model_path='models/sales_model.pkl'):
        self.model_path = model_path
        self.model = None
        self.training_columns = None
        self.load_model()
    
    def load_model(self):
        """Carica il modello per le previsioni"""
        try:
            model_data = joblib.load(self.model_path)
            self.model = model_data['model']
            self.training_columns = model_data['training_columns']
            print(f"✅ Modello production caricato: {self.model_path}")
        except Exception as e:
            print(f"❌ Errore caricamento modello: {e}")
            raise
    
    def predict(self, mese, promozione, meteo, evento_speciale, vendite_precedenti):
        """
        Fai una previsione - VERSIONE PRODUCTION!
        Input → Output, senza grafici o spiegazioni
        """
        # Prepara input
        input_data = {
            'mese': [mese],
            'giorno_settimana': [1],
            'promozione': [promozione],
            'prezzo_scontato': [1.0],
            'meteo': [meteo],
            'evento_speciale': [evento_speciale],
            'vendite_precedenti': [vendite_precedenti]
        }
        
        input_df = pd.DataFrame(input_data)
        input_df['mese_promozione'] = input_df['mese'] * input_df['promozione']
        input_df['meteo_evento'] = input_df['meteo'] * input_df['evento_speciale']
        input_df = input_df[self.training_columns]
        
        # Previsione
        prediction = self.model.predict(input_df)[0]
        
        return {
            'success': True,
            'prediction': round(prediction),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

# =============================================================================
# 🚀 PARTE 4: ESEMPIO COMPLETO DI UTILIZZO
# =============================================================================

def esempio_completo():
    """
    Esempio completo che mostra tutto il flusso
    """
    print("=" * 70)
    print("🚀 ESEMPIO COMPLETO - AGENTE AI PREDITTIVO")
    print("=" * 70)
    
    # 1. TEORIA
    teoria = TeoriaRandomForest()
    teoria.spiegazione_concetti_base()
    teoria.spiegazione_features_vs_target()
    
    input("\n📚 Premi INVIO per continuare con la parte pratica...")
    
    # 2. IMPLEMENTAZIONE
    print("\n" + "=" * 70)
    print("🏗️  IMPLEMENTAZIONE PRATICA")
    print("=" * 70)
    
    agent = PredictiveSalesAgent()
    
    # 2.1 Genera dati
    df = agent.generate_sample_data(1000)
    
    # 2.2 Prepara features
    X, y = agent.prepare_features(df)
    
    # 2.3 Allena modello
    agent.train(X, y)
    
    # 2.4 Spiega modello
    agent.explain_model()
    
    input("\n🎯 Premi INVIO per vedere le previsioni...")
    
    # 2.5 Previsioni singole (production-like)
    print("\n" + "=" * 70)
    print("🎯 PREVISIONI SINGOLE - VERSIONE PRODUCTION")
    print("=" * 70)
    
    test_cases = [
        (12, 1, 4, 0, 1200),  # Dicembre, promo, bel tempo
        (6, 1, 3, 1, 1100),   # Giugno, promo, meteo buono, evento
        (1, 0, 2, 0, 900),    # Gennaio, no promo, meteo mediocre
    ]
    
    for i, (mese, promo, meteo, evento, vend_ieri) in enumerate(test_cases, 1):
        pred = agent.predict_single(mese, promo, meteo, evento, vend_ieri)
        print(f"Caso {i}: Mese={mese}, Promo={promo}, Meteo={meteo} → {pred} vendite")
    
    # 2.6 Previsioni future (con grafico dimostrativo)
    print("\n" + "=" * 70)
    print("🔮 PREVISIONI FUTURE - CON GRAFICO DIMOSTRATIVO")
    print("=" * 70)
    print("⚠️  NOTA: In produzione NON si mostrano grafici!")
    print("   Si restituiscono solo i numeri via API/interfaccia")
    
    agent.forecast_future(30, show_plot=True)
    
    # 2.7 Salva modello
    print("\n" + "=" * 70)
    print("💾 SALVATAGGIO MODELLO PER PRODUZIONE")
    print("=" * 70)
    
    model_path = agent.save_model('modello_completo.pkl')
    
    # 3. DEMO PRODUCTION
    input("\n🏭 Premi INVIO per vedere la versione Production...")
    
    print("\n" + "=" * 70)
    print("🏭 VERSIONE PRODUCTION - SOLO INPUT/OUTPUT")
    print("=" * 70)
    
    # Carica modello salvato
    production_predictor = ProductionSalesPredictor('modello_completo.pkl')
    
    # Simula interfaccia utente
    print("\n🖥️  INTERFACCIA PRODUCTION:")
    print("   Inserisci i valori → Ottieni la previsione")
    print()
    
    # Esempio di utilizzo reale
    risultato = production_predictor.predict(
        mese=12,
        promozione=1, 
        meteo=4,
        evento_speciale=0,
        vendite_precedenti=1200
    )
    
    if risultato['success']:
        print(f"📊 INPUT UTENTE:")
        print(f"   - Mese: Dicembre (12)")
        print(f"   - Promozione: Sì (1)") 
        print(f"   - Meteo: Ottimo (4)")
        print(f"   - Evento: No (0)")
        print(f"   - Vendite Ieri: 1200")
        print()
        print(f"🎯 RISULTATO:")
        print(f"   ⚡ PREVISIONE VENDITE OGGI: {risultato['prediction']} €")
        print(f"   🕒 Timestamp: {risultato['timestamp']}")
    else:
        print(f"❌ Errore: {risultato.get('error', 'Unknown')}")
    
    print("\n" + "=" * 70)
    print("🎉 ESEMPIO COMPLETATO CON SUCCESSO!")
    print("=" * 70)
    print("\n💡 HAI VISTO TUTTO IL FLUSSO:")
    print("   📚 Teoria → 🏗️ Implementazione → 🏭 Production")
    print("   👨‍🏫 Script Didattico → 🖥️ Interfaccia Pulita")

# =============================================================================
# 🎯 MAIN E ESECUZIONE
# =============================================================================

if __name__ == "__main__":
    """
    Script principale - Esegui tutto l'esempio
    """
    print("🎯 AGENTE AI PREDITTIVO COMPLETO")
    print("   Teoria + Implementazione + Production")
    print("   " + "=" * 50)
    
    try:
        # Esegui l'esempio completo
        esempio_completo()
        
        print("\n" + "🎯 PROSSIMI PASSI:")
        print("1. Modifica i parametri per il tuo caso specifico")
        print("2. Sostituisci i dati sintetici con dati reali") 
        print("3. Integra in un'API web o dashboard")
        print("4. Metti in produzione!")
        
    except Exception as e:
        print(f"\n❌ Errore durante l'esecuzione: {e}")
        print("💡 Controlla di avere tutte le dipendenze installate:")
        print("   pip install numpy pandas scikit-learn matplotlib joblib")
    
    finally:
        print("\n" + "=" * 70)
        print("📚 RISORSE PER APPROFONDIRE:")
        print("   - Documentazione scikit-learn: https://scikit-learn.org")
        print("   - Random Forest: https://scikit-learn.org/stable/modules/ensemble.html#forest")
        print("   - Machine Learning: https://scikit-learn.org/stable/user_guide.html")
        print("=" * 70)
