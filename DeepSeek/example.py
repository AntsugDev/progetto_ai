import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import joblib
import warnings
warnings.filterwarnings('ignore')

class PredictiveSalesAgent:
    """
    Agente AI predittivo per forecast delle vendite
    """
    
    def __init__(self):
        self.model = None
        self.is_trained = False
        self.feature_importance = None
        self.feature_names = None
        self.training_columns = None
        
    def generate_sample_data(self, n_samples=1000):
        """
        Genera dati di esempio per il training
        Teoria: Simula un dataset di vendite con features rilevanti
        """
        np.random.seed(42)
        
        data = {
            'mese': np.random.randint(1, 13, n_samples),
            'giorno_settimana': np.random.randint(1, 8, n_samples),
            'promozione': np.random.randint(0, 2, n_samples),
            'prezzo_scontato': np.random.uniform(0.7, 1.0, n_samples),
            'meteo': np.random.randint(1, 5, n_samples),  # 1=cattivo, 4=ottimo
            'evento_speciale': np.random.randint(0, 2, n_samples),
            'vendite_precedenti': np.random.normal(1000, 200, n_samples)
        }
        
        # Teoria: Creazione target con relazioni non lineari
        base_sales = 500
        mese_effect = data['mese'] * 15
        promozione_effect = data['promozione'] * 200
        meteo_effect = data['meteo'] * 50
        evento_effect = data['evento_speciale'] * 150
        prezzo_effect = (1 - data['prezzo_scontato']) * 300
        storico_effect = data['vendite_precedenti'] * 0.3
        
        # Target: vendite giornaliere
        noise = np.random.normal(0, 50, n_samples)
        data['vendite_giornaliere'] = (base_sales + mese_effect + promozione_effect + 
                                     meteo_effect + evento_effect + prezzo_effect + 
                                     storico_effect + noise)
        
        self.df = pd.DataFrame(data)
        return self.df
    
    def prepare_features(self, df):
        """
        Preparazione features per il modello predittivo
        Teoria: Feature engineering migliora le performance del modello
        """
        X = df.drop('vendite_giornaliere', axis=1)
        y = df['vendite_giornaliere']
        
        # Teoria: Le interazioni tra features catturano relazioni complesse
        X['mese_promozione'] = X['mese'] * X['promozione']
        X['meteo_evento'] = X['meteo'] * X['evento_speciale']
        
        # Salva i nomi delle features per uso futuro
        self.feature_names = X.columns.tolist()
        self.training_columns = X.columns.tolist()
        
        return X, y
    
    def train(self, X, y):
        """
        Addestramento del modello predittivo
        Teoria: Random Forest cattura relazioni non lineari
        """
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Teoria: Ensemble methods combinano multiple decision trees
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Valutazione del modello
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        # Previsioni di test
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        
        # Feature importance
        self.feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"✅ Modello addestrato con successo!")
        print(f"📊 R² Train: {train_score:.3f}")
        print(f"📊 R² Test: {test_score:.3f}")
        print(f"📈 MAE: {mae:.2f}")
        
        return train_score, test_score, mae
    
    def predict(self, X_new):
        """
        Genera previsioni su nuovi dati
        Teoria: Il modello applica pattern appresi a dati non visti
        """
        if not self.is_trained:
            raise ValueError("❌ Modello non addestrato! Chiamare train() prima.")
        
        # Assicurati che X_new abbia le stesse colonne del training
        if isinstance(X_new, pd.DataFrame):
            X_new = X_new[self.training_columns]
        else:
            # Se è un array numpy, converti in DataFrame con i nomi corretti
            X_new = pd.DataFrame(X_new, columns=self.training_columns)
        
        predictions = self.model.predict(X_new)
        return predictions
    
    def explain_prediction(self, X_sample=None):
        """
        Spiega le previsioni mostrando l'importanza delle features
        Teoria: Interpretabilità del modello per decisioni consapevoli
        """
        if self.feature_importance is None:
            print("Nessun dato di feature importance disponibile")
            return
        
        print("\n🔍 ANALISI FEATURE IMPORTANCE:")
        print("=" * 40)
        for _, row in self.feature_importance.head().iterrows():
            print(f"{row['feature']:20} {row['importance']:.3f}")
    
    def create_future_features(self, periods=30):
        """
        Crea features per previsioni future mantenendo la struttura corretta
        """
        future_data = []
        
        for i in range(periods):
            # Simula dati futuri con pattern stagionale
            future_point = {
                'mese': (i % 12) + 1,
                'giorno_settimana': (i % 7) + 1,
                'promozione': 1 if i % 7 == 0 else 0,  # Promozioni la domenica
                'prezzo_scontato': 0.9 if i % 7 == 0 else 1.0,
                'meteo': np.random.randint(2, 5),
                'evento_speciale': 1 if i in [5, 15, 25] else 0,
                'vendite_precedenti': 1000 + (i * 10),  # Trend crescente
            }
            future_data.append(future_point)
        
        future_df = pd.DataFrame(future_data)
        
        # Applica lo stesso feature engineering del training
        future_df['mese_promozione'] = future_df['mese'] * future_df['promozione']
        future_df['meteo_evento'] = future_df['meteo'] * future_df['evento_speciale']
        
        # Assicurati che le colonne siano nello stesso ordine del training
        if self.training_columns:
            future_df = future_df[self.training_columns]
        
        return future_df
    
    def forecast_future(self, periods=30):
        """
        Previsione per periodi futuri
        Teoria: Estrapolazione di trend basata su pattern storici
        """
        if not self.is_trained:
            raise ValueError("❌ Modello non addestrato! Chiamare train() prima.")
        
        # Crea features future con la stessa struttura del training
        future_df = self.create_future_features(periods)
        
        # Genera previsioni
        predictions = self.predict(future_df)
        
        # Visualizza le previsioni
        plt.figure(figsize=(12, 6))
        plt.plot(range(periods), predictions, marker='o', linewidth=2, color='blue', label='Previsioni')
        plt.title('📈 Previsioni Vendite - Prossimi 30 Giorni')
        plt.xlabel('Giorno')
        plt.ylabel('Vendite Previste')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.show()
        
        # Statistiche delle previsioni
        print(f"\n📊 STATISTICHE PREVISIONI:")
        print(f"   Media: {np.mean(predictions):.0f} vendite/giorno")
        print(f"   Massimo: {np.max(predictions):.0f} vendite")
        print(f"   Minimo: {np.min(predictions):.0f} vendite")
        print(f"   Deviazione Standard: {np.std(predictions):.0f}")
        
        return predictions, future_df
    
    def save_model(self, filename='predictive_agent_model.pkl'):
        """Salva il modello addestrato"""
        if self.is_trained:
            model_data = {
                'model': self.model,
                'feature_importance': self.feature_importance,
                'training_columns': self.training_columns,
                'feature_names': self.feature_names
            }
            joblib.dump(model_data, filename)
            print(f"✅ Modello salvato come {filename}")
        else:
            print("❌ Nessun modello da salvare")
    
    def load_model(self, filename='predictive_agent_model.pkl'):
        """Carica un modello addestrato"""
        try:
            model_data = joblib.load(filename)
            self.model = model_data['model']
            self.feature_importance = model_data['feature_importance']
            self.training_columns = model_data['training_columns']
            self.feature_names = model_data['feature_names']
            self.is_trained = True
            print(f"✅ Modello caricato da {filename}")
        except FileNotFoundError:
            print(f"❌ File {filename} non trovato")

# Esempio di utilizzo corretto
if __name__ == "__main__":
    # Inizializza l'agente predittivo
    agent = PredictiveSalesAgent()
    
    # Genera dati di esempio
    print("🔄 Generazione dati di training...")
    df = agent.generate_sample_data(1000)
    
    # Prepara le features
    X, y = agent.prepare_features(df)
    print(f"📋 Features utilizzate: {agent.training_columns}")
    
    # Addestra il modello
    print("🎯 Addestramento modello predittivo...")
    agent.train(X, y)
    
    # Spiega il modello
    agent.explain_prediction()
    
    # Genera previsioni future
    print("\n🔮 Generazione previsioni future...")
    future_predictions, future_features = agent.forecast_future(30)
    
    # Test predizione su singolo punto
    print("\n🧪 Test predizione singolo punto...")
    single_point = future_features.iloc[[0]]  # Prendi il primo punto futuro
    single_prediction = agent.predict(single_point)
    print(f"   Previsione singolo punto: {single_prediction[0]:.0f} vendite")
    
    # Salva il modello
    agent.save_model('my_predictive_agent.pkl')
    
    print("\n" + "="*50)
    print("🎉 AGENTE PREDITTIVO FUNZIONANTE CON SUCCESSO!")
    print("="*50)
