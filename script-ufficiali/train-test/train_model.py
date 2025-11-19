# train_model.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib
import warnings
import pymysql
from datetime import datetime

warnings.filterwarnings('ignore')

class CarPurchasePredictor:
    """
    Agente AI predittivo - Versione semplificata per training
    """
    
    def __init__(self):
        self.model = None
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_importance = None
        
    class DBConfig:
        def __init__(self):
            self.host = "localhost"
            self.user = "asugamele"
            self.password = "83Asugamele@"
            self.database = "projectAI"
            self.cursorclass = pymysql.cursors.DictCursor

    def load_data_from_db(self):
        """Carica i dati dal database per il training"""
        print("📊 Caricamento dati dal database...")
        
        db_config = self.DBConfig()
        conn = pymysql.connect(**db_config.__dict__)
        
        try:
            query = """
            SELECT 
                m.*,
                np.testo as neo_patentato,
                s.testo as sesso,
                z.testo as zona,
                ta.testo as tipologia_auto,
                nu.testo as nuovo_usato,
                fa.testo as formula_acquisto,
                m.decisione_AI as target_decision
            FROM model m
            LEFT JOIN neo_patentato np ON m.neo_patentato_id = np.id
            LEFT JOIN sesso s ON m.sesso_id = s.id
            LEFT JOIN zona z ON m.zona_id = z.id
            LEFT JOIN tipologia_auto ta ON m.tipologia_auto_id = ta.id
            LEFT JOIN nuovo_usato nu ON m.nuovo_usato_id = nu.id
            LEFT JOIN formula_acquisto fa ON m.formula_acquisto_id = fa.id
            WHERE m.decisione_AI IS NOT NULL
            """
            
            df = pd.read_sql(query, conn)
            print(f"✅ Dati caricati: {len(df)} righe")
            
            # Converti colonne numeriche
            df = self._convert_numeric_columns(df)
            
            return df
            
        except Exception as e:
            print(f"❌ Errore nel caricamento dati: {e}")
            return pd.DataFrame()
        finally:
            conn.close()

    def _convert_numeric_columns(self, df):
        """Converti colonne numeriche"""
        numeric_columns = [
            'eta', 'nr_figli', 'reddito_mensie', 'altre_spese', 'diff_reddito',
            'costo_auto', 'eta_veicolo', 'oneri_accessori', 'anticipo', 'tan',
            'nr_rate', 'importo_finanziato', 'rata', 'sostenibilita', 
            'coefficiente_K', 're', 'rs', 'rd', 'rt'
        ]
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df

    def prepare_features(self, df):
        """Prepara le features per il training"""
        print("🔧 Preparazione features...")
        
        if df.empty:
            raise ValueError("❌ Nessun dato disponibile!")
        
        X = df.copy()
        
        # Features numeriche
        numeric_features = [
            'eta', 'nr_figli', 'reddito_mensie', 'altre_spese', 'diff_reddito',
            'costo_auto', 'oneri_accessori', 'anticipo', 'tan', 'nr_rate',
            'importo_finanziato', 'rata', 'sostenibilita', 'coefficiente_K',
            're', 'rs', 'rd', 'rt'
        ]
        
        # Features categoriche
        categorical_features = [
            'neo_patentato', 'sesso', 'zona', 'tipologia_auto', 
            'nuovo_usato', 'formula_acquisto'
        ]
        
        # Encoding categoriche
        for feature in categorical_features:
            if feature in X.columns and not X[feature].isnull().all():
                self.label_encoders[feature] = LabelEncoder()
                X[feature] = X[feature].fillna('Unknown')
                X[feature] = self.label_encoders[feature].fit_transform(X[feature].astype(str))
        
        # Seleziona colonne disponibili
        all_features = numeric_features + categorical_features
        available_features = [col for col in all_features if col in X.columns and not X[col].isnull().all()]
        
        X_final = X[available_features].dropna()
        
        # Target
        if 'target_decision' in df.columns:
            y = df['target_decision'].loc[X_final.index]
            
            if len(y) == 0:
                raise ValueError("❌ Nessun target valido!")
            
            self.label_encoders['target'] = LabelEncoder()
            y_encoded = self.label_encoders['target'].fit_transform(y)
            
            print(f"🎯 Decisioni target:")
            for decision in self.label_encoders['target'].classes_:
                count = (y == decision).sum()
                print(f"   {decision}: {count} occorrenze")
            
        else:
            raise ValueError("❌ Target non trovato!")
        
        print(f"✅ Features: {len(available_features)}, Righe: {len(X_final)}")
        return X_final, y_encoded, available_features

    def train(self, X, y):
        """Allena il modello"""
        if len(X) < 10:
            raise ValueError(f"❌ Dati insufficienti: {len(X)} righe")
        
        print("🎯 Allenamento modello...")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scaling
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Modello
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True
        
        # Valutazione
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Feature Importance
        self.feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\n📈 RISULTATI TRAINING:")
        print(f"✅ Accuratezza: {accuracy:.1%}")
        print(classification_report(y_test, y_pred, target_names=self.label_encoders['target'].classes_))
        
        return accuracy

    def save_model(self, filename='../../file/model.pkl'):
        """Salva il modello"""
        if not self.is_trained:
            raise ValueError("❌ Nessun modello da salvare!")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_importance': self.feature_importance,
            'training_date': datetime.now()
        }
        
        joblib.dump(model_data, filename)
        print(f"💾 Modello salvato: {filename}")

def main():
    """Main training"""
    print("🚀 TRAINING MODELLO AI")
    print("=" * 50)
    
    predictor = CarPurchasePredictor()
    df = predictor.load_data_from_db()
    
    if df.empty:
        print("❌ Nessun dato per il training")
        return
    
    try:
        X, y, features = predictor.prepare_features(df)
        accuracy = predictor.train(X, y)
        predictor.save_model('../../file/model.pkl')
        
        print("\n🎉 TRAINING COMPLETATO!")
        print("📁 Usa 'test_cliente.py' per testare nuovi clienti")
        
    except Exception as e:
        print(f"❌ Errore training: {e}")

if __name__ == "__main__":
    main()