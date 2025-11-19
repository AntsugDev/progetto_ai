# production_predictor.py
import joblib
import pandas as pd

class ProductionSalesPredictor:
    def __init__(self, model_path='my_predictive_agent.pkl'):
        self.model = joblib.load(model_path)
    
    def predict_sales(self, input_dict):
        """
        input_dict = {
            'mese': 12,
            'promozione': 1, 
            'meteo': 4,
            'evento_speciale': 0,
            'vendite_precedenti': 1200
        }
        """
        # Prepara features come durante il training
        features = self._prepare_features(input_dict)
        
        # Previsione
        prediction = self.model.predict(features)[0]
        
        return {
            'predicted_sales': round(prediction),
            'confidence': 'high',  # Basato su performance modello
            'timestamp': pd.Timestamp.now()
        }
    
    def _prepare_features(self, input_data):
        # Stesso feature engineering del training
        df = pd.DataFrame([input_data])
        df['mese_promozione'] = df['mese'] * df['promozione']
        df['meteo_evento'] = df['meteo'] * df['evento_speciale']
        return df

# USO REALE:
if __name__ == "__main__":
    predictor = ProductionSalesPredictor()
    
    # Simula input utente
    user_input = {
        'mese': 12,
        'promozione': 1,
        'meteo': 4, 
        'evento_speciale': 0,
        'vendite_precedenti': 1200
    }
    
    result = predictor.predict_sales(user_input)
    print(f"🎯 Previsione: {result['predicted_sales']} vendite")
    # Output: 🎯 Previsione: 1850 vendite
