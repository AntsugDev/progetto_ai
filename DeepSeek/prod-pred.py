# production_predictor.py
import joblib
import pandas as pd
import os
from datetime import datetime

class SalesPredictor:
    """
    Classe per caricare e usare il modello addestrato in produzione
    """
    
    def __init__(self, model_path='models/sales_model_v1.pkl'):
        self.model_path = model_path
        self.model = None
        self.training_columns = None
        self.load_model()
    
    def load_model(self):
        """Carica il modello addestrato dal file .pkl"""
        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Modello non trovato: {self.model_path}")
            
            print(f"📂 Caricamento modello da: {self.model_path}")
            model_data = joblib.load(self.model_path)
            
            self.model = model_data['model']
            self.training_columns = model_data['training_columns']
            self.training_date = model_data.get('training_date', 'Sconosciuta')
            self.version = model_data.get('version', '1.0')
            
            print(f"✅ Modello caricato con successo!")
            print(f"📅 Data training: {self.training_date}")
            print(f"🔄 Versione: {self.version}")
            print(f"📊 Features: {len(self.training_columns)}")
            
        except Exception as e:
            print(f"❌ Errore nel caricamento modello: {e}")
            raise
    
    def validate_input(self, mese, promozione, meteo, evento_speciale, vendite_precedenti):
        """Valida gli input dell'utente"""
        errors = []
        
        if not (1 <= mese <= 12):
            errors.append("Mese deve essere tra 1 e 12")
        if promozione not in [0, 1]:
            errors.append("Promozione deve essere 0 o 1")
        if not (1 <= meteo <= 4):
            errors.append("Meteo deve essere tra 1 e 4")
        if evento_speciale not in [0, 1]:
            errors.append("Evento speciale deve essere 0 o 1")
        if vendite_precedenti < 0:
            errors.append("Vendite precedenti non possono essere negative")
        
        return errors
    
    def prepare_input_features(self, mese, promozione, meteo, evento_speciale, vendite_precedenti):
        """Prepara le features per la prediction nello stesso formato del training"""
        # Crea il DataFrame di input
        input_data = {
            'mese': [mese],
            'giorno_settimana': [1],  # Default, potrebbe essere migliorato
            'promozione': [promozione],
            'prezzo_scontato': [1.0],  # Default
            'meteo': [meteo],
            'evento_speciale': [evento_speciale],
            'vendite_precedenti': [vendite_precedenti]
        }
        
        df = pd.DataFrame(input_data)
        
        # Applica lo stesso feature engineering del training
        df['mese_promozione'] = df['mese'] * df['promozione']
        df['meteo_evento'] = df['meteo'] * df['evento_speciale']
        
        # Assicurati che le colonne siano nello stesso ordine
        df = df[self.training_columns]
        
        return df
    
    def predict_sales(self, mese, promozione, meteo, evento_speciale, vendite_precedenti):
        """
        Prevede le vendite basandosi sugli input
        
        Args:
            mese (int): 1-12
            promozione (int): 0=No, 1=Sì
            meteo (int): 1=Cattivo, 4=Ottimo
            evento_speciale (int): 0=No, 1=Sì
            vendite_precedenti (float): Vendite del giorno precedente
        
        Returns:
            dict: Risultato della previsione
        """
        try:
            # Validazione input
            errors = self.validate_input(mese, promozione, meteo, evento_speciale, vendite_precedenti)
            if errors:
                return {
                    'success': False,
                    'error': "; ".join(errors),
                    'prediction': None
                }
            
            # Prepara features
            features_df = self.prepare_input_features(mese, promozione, meteo, evento_speciale, vendite_precedenti)
            
            # Fai la previsione
            prediction = self.model.predict(features_df)[0]
            
            return {
                'success': True,
                'prediction': round(prediction),
                'confidence': self._get_confidence_level(prediction),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'input_used': {
                    'mese': mese,
                    'promozione': promozione,
                    'meteo': meteo,
                    'evento_speciale': evento_speciale,
                    'vendite_precedenti': vendite_precedenti
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Errore nella previsione: {e}",
                'prediction': None
            }
    
    def _get_confidence_level(self, prediction):
        """Determina il livello di confidenza basato sulla prediction"""
        if prediction > 2000:
            return "high"
        elif prediction > 1000:
            return "medium"
        else:
            return "low"
    
    def get_model_info(self):
        """Restituisce informazioni sul modello"""
        return {
            'version': self.version,
            'training_date': self.training_date,
            'features_count': len(self.training_columns),
            'features': self.training_columns,
            'model_type': type(self.model).__name__
        }

# ESEMPIO DI UTILIZZO IN PRODUZIONE
def main():
    """Esempio di utilizzo del predictor in produzione"""
    print("🚀 AVVIO PREDICTOR DI PRODUZIONE")
    print("=" * 50)
    
    # Inizializza il predictor (carica automaticamente il modello)
    predictor = SalesPredictor('models/sales_model_v1.pkl')
    
    # Esempio 1: Previsione normale
    print("\n📈 ESEMPIO 1: Previsione normale")
    result1 = predictor.predict_sales(
        mese=12,           # Dicembre
        promozione=1,      # Con promozione
        meteo=4,           # Ottimo meteo
        evento_speciale=0, # Nessun evento
        vendite_precedenti=1200
    )
    
    if result1['success']:
        print(f"✅ Previsione: {result1['prediction']} vendite")
        print(f"🎯 Confidenza: {result1['confidence']}")
    else:
        print(f"❌ Errore: {result1['error']}")
    
    # Esempio 2: Previsione con input invalido
    print("\n⚠️ ESEMPIO 2: Input invalido")
    result2 = predictor.predict_sales(
        mese=15,  # Mese invalido
        promozione=1,
        meteo=4,
        evento_speciale=0,
        vendite_precedenti=1200
    )
    
    if not result2['success']:
        print(f"❌ Errore: {result2['error']}")
    
    # Informazioni modello
    print("\n🔍 INFORMAZIONI MODELLO:")
    info = predictor.get_model_info()
    for key, value in info.items():
        print(f"   {key}: {value}")

if __name__ == "__main__":
    main()
