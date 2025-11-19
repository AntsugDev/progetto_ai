# training_script.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os
from datetime import datetime

class ModelTrainer:
    """
    Classe per addestrare e salvare il modello
    """
    
    def __init__(self):
        self.model = None
        self.training_columns = None
        
    def generate_training_data(self, n_samples=5000):
        """Genera dati di training realistici"""
        np.random.seed(42)
        
        print("📊 Generazione dati di training...")
        data = {
            'mese': np.random.randint(1, 13, n_samples),
            'giorno_settimana': np.random.randint(1, 8, n_samples),
            'promozione': np.random.randint(0, 2, n_samples),
            'prezzo_scontato': np.random.uniform(0.7, 1.0, n_samples),
            'meteo': np.random.randint(1, 5, n_samples),
            'evento_speciale': np.random.randint(0, 2, n_samples),
            'vendite_precedenti': np.random.normal(1000, 200, n_samples)
        }
        
        # Creazione target con relazioni realistiche
        base_sales = 500
        mese_effect = data['mese'] * 15
        promozione_effect = data['promozione'] * 200
        meteo_effect = data['meteo'] * 50
        evento_effect = data['evento_speciale'] * 150
        prezzo_effect = (1 - data['prezzo_scontato']) * 300
        storico_effect = data['vendite_precedenti'] * 0.3
        noise = np.random.normal(0, 50, n_samples)
        
        data['vendite_giornaliere'] = (base_sales + mese_effect + promozione_effect + 
                                     meteo_effect + evento_effect + prezzo_effect + 
                                     storico_effect + noise)
        
        return pd.DataFrame(data)
    
    def prepare_features(self, df):
        """Prepara le features per il training"""
        X = df.drop('vendite_giornaliere', axis=1)
        y = df['vendite_giornaliere']
        
        # Feature engineering
        X['mese_promozione'] = X['mese'] * X['promozione']
        X['meteo_evento'] = X['meteo'] * X['evento_speciale']
        
        # Salva l'ordine delle colonne per consistency
        self.training_columns = X.columns.tolist()
        
        return X, y
    
    def train_model(self, X, y):
        """Addestra il modello Random Forest"""
        print("🎯 Addestramento modello in corso...")
        
        # Split dei dati
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Creazione e training del modello
        self.model = RandomForestRegressor(
            n_estimators=150,
            max_depth=12,
            random_state=42,
            n_jobs=-1  # Usa tutti i core della CPU
        )
        
        self.model.fit(X_train, y_train)
        
        # Valutazione
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        
        print(f"✅ Modello addestrato con successo!")
        print(f"📊 R² Training: {train_score:.3f}")
        print(f"📊 R² Test: {test_score:.3f}")
        print(f"📈 MAE: {mae:.2f} vendite")
        
        return test_score, mae
    
    def save_model(self, filename='sales_model.pkl'):
        """Salva il modello addestrato su disco"""
        if self.model is None:
            raise ValueError("❌ Nessun modello da salvare!")
        
        # Prepara i dati da salvare
        model_data = {
            'model': self.model,
            'training_columns': self.training_columns,
            'feature_names': self.training_columns,
            'training_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'model_type': 'RandomForestRegressor',
            'version': '1.0'
        }
        
        # Crea la directory se non esiste
        os.makedirs('models', exist_ok=True)
        
        # Salva il file
        model_path = f'models/{filename}'
        joblib.dump(model_data, model_path)
        
        print(f"💾 Modello salvato in: {model_path}")
        print(f"📏 Dimensioni file: {os.path.getsize(model_path) / 1024 / 1024:.2f} MB")
        
        return model_path

def main():
    """Script principale di training"""
    print("🚀 AVVIO TRAINING MODELLO")
    print("=" * 50)
    
    # Inizializza il trainer
    trainer = ModelTrainer()
    
    try:
        # 1. Genera dati
        df = trainer.generate_training_data(5000)
        print(f"📁 Dati generati: {len(df)} righe")
        
        # 2. Prepara features
        X, y = trainer.prepare_features(df)
        print(f"🎯 Features utilizzate: {len(X.columns)}")
        
        # 3. Allena modello
        test_score, mae = trainer.train_model(X, y)
        
        # 4. Salva modello
        model_path = trainer.save_model('sales_model_v1.pkl')
        
        print("=" * 50)
        print("🎉 TRAINING COMPLETATO CON SUCCESSO!")
        print(f"📁 Modello salvato: {model_path}")
        print(f"📊 Performance: R²={test_score:.3f}, MAE={mae:.1f}")
        
    except Exception as e:
        print(f"❌ Errore durante il training: {e}")

if __name__ == "__main__":
    main()
