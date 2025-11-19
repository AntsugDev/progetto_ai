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
    Agente AI predittivo per consigliare acquisto auto e metodo di pagamento
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
            # Query corretta che rispecchia la tua struttura del database
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
            
            # 🔥 CONVERSIONE COLONNE NUMERICHE - FONDAMENTALE!
            df = self._convert_numeric_columns(df)
            
            return df
            
        except Exception as e:
            print(f"❌ Errore nel caricamento dati: {e}")
            return pd.DataFrame()
        finally:
            conn.close()

    def _convert_numeric_columns(self, df):
        """
        Converti tutte le colonne numeriche da stringhe a float
        """
        print("🔢 Conversione colonne numeriche...")
        
        # Lista di tutte le colonne che dovrebbero essere numeriche
        numeric_columns = [
            'eta', 'nr_figli', 'reddito_mensie', 'altre_spese', 'diff_reddito',
            'costo_auto', 'eta_veicolo', 'oneri_accessori', 'anticipo', 'tan',
            'nr_rate', 'importo_finanziato', 'rata', 'sostenibilita', 
            'coefficiente_K', 're', 'rs', 'rd', 'rt'
        ]
        
        for col in numeric_columns:
            if col in df.columns:
                # Conta quanti valori non nulli abbiamo prima
                non_null_before = df[col].notnull().sum()
                # Prova a convertire in numerico, gli errori diventano NaN
                df[col] = pd.to_numeric(df[col], errors='coerce')
                # Conta dopo la conversione
                non_null_after = df[col].notnull().sum()
        return df

    def prepare_features(self, df):
        """
        Prepara le features per il machine learning
        """
        print("🔧 Preparazione features...")
        
        if df.empty:
            raise ValueError("❌ Nessun dato disponibile per il training!")
        
        # Crea una copia per non modificare l'originale
        X = df.copy()
        
        # 1. FEATURES NUMERICHE DIRETTE 
        numeric_features = [
            'eta', 'nr_figli', 'reddito_mensie', 'altre_spese', 'diff_reddito',
            'costo_auto', 'eta_veicolo', 'oneri_accessori', 'anticipo', 'tan',
            'nr_rate', 'importo_finanziato', 'rata', 'sostenibilita',
            'coefficiente_K', 're', 'rs', 'rd', 'rt'
        ]
        
        # 2. FEATURE ENGINEERING basato sulle tue regole
        print("🎯 Creazione feature derivate...")
        print("Ricreo le condizioni per la sostenibilità")
        
        # Calcola sostenibilità se non presente o non valida
        if 'sostenibilita' not in X.columns or X['sostenibilita'].isnull().all():
            if 'rata' in X.columns and 'diff_reddito' in X.columns:
                # Usiamo .values per evitare problemi con indici
                X['sostenibilita'] = X['rata'].values / np.where(X['diff_reddito'].values > 0, X['diff_reddito'].values, 1)
        
        X['sostenibilita_alta'] = 0
        X['sostenibilita_zona_grigia'] = 0
        X['sostenibilita_bassa'] = 0
        # Indicatori basati sulle tue regole di business - CON CONTROLLO TIPO DATI
        try:
            print("Aggiungo tre campi per la sostenibilità (alta, zona grigia, bassa)")
            X['sostenibilita_alta'] = (X['sostenibilita'] >= 0.35).astype(int)
            X['sostenibilita_zona_grigia'] = ((X['sostenibilita'] >= 0.21) & (X['sostenibilita'] <= 0.34)).astype(int)
            X['sostenibilita_bassa'] = (X['sostenibilita'] <= 0.20).astype(int)
        except Exception as e:
            raise ValueError(f"   ❌ Errore indicatori sostenibilità: {e}")
        
        
        # Altre features derivate con controllo errori
        try:
            if 'anticipo' in X.columns and 'costo_auto' in X.columns:
               X['rapporto_anticipo_costo'] = X['anticipo'] / np.where(X['costo_auto'] > 0, X['costo_auto'], 1)
        except Exception as e:
            raise ValueError(f"   ⚠️  Errore features derivate: {e}")
        
        # 3. FEATURES CATEGORICHE
        categorical_features = [
            'neo_patentato', 'sesso', 'zona', 'tipologia_auto', 
            'nuovo_usato', 'formula_acquisto'
        ]
        
        # Encoding features categoriche
        for feature in categorical_features:
            if feature in X.columns and not X[feature].isnull().all():
                try:
                    self.label_encoders[feature] = LabelEncoder()
                    # Gestisci valori nulli
                    X[feature] = X[feature].fillna('Unknown')
                    X[feature] = self.label_encoders[feature].fit_transform(X[feature].astype(str))
                except Exception as e:
                    raise ValueError(f"   ❌ Errore encoding {feature}: {e}")
        
        # Seleziona tutte le colonne disponibili
        all_possible_features = numeric_features + categorical_features + [
            'sostenibilita_alta', 'sostenibilita_media', 'sostenibilita_bassa',
            'diff_reddito', 'rapporto_anticipo_costo', 'rt'
        ]
        
        # Prendi solo le colonne che esistono e non sono tutte nulle
        available_features = []
        for feature in all_possible_features:
            if feature in X.columns:
                # Controlla se la colonna ha valori non nulli
                if not X[feature].isnull().all():
                    available_features.append(feature)
        print(f"   📊 Features disponibili: {available_features}")
        X_final = X[available_features]
        
        # Rimuovi righe con valori NaN nelle features
        before_clean = len(X_final)
        X_final = X_final.dropna()
        after_clean = len(X_final)
        
        if before_clean > after_clean:
            print(f"   🧹 Rimosse {before_clean - after_clean} righe con valori mancanti")
        
        # Target: la decisione AI che vuoi prevedere
        if 'target_decision' in df.columns:
            y = df['target_decision']
            
            # Allinea y con X_final dopo la pulizia
            y = y.loc[X_final.index]
            
            if len(y) == 0:
                raise ValueError("❌ Nessun target valido (decisione_AI) trovato dopo la pulizia!")
            
            # Encoding del target
            self.label_encoders['target'] = LabelEncoder()
            y_encoded = self.label_encoders['target'].fit_transform(y)
            
            #todo bo???
            print(f"🎯 Decisioni target uniche: {list(self.label_encoders['target'].classes_)}")
            for decision in self.label_encoders['target'].classes_:
                count = (y == decision).sum()
                print(f"   {decision}: {count} occorrenze")
            
        else:
            raise ValueError("❌ Colonna target 'decisione_AI' non trovata!")
        
        return X_final, y_encoded, available_features

    def train(self, X, y):
        """
        Allena il modello Random Forest
        """
        if len(X) < 10:
            raise ValueError(f"❌ Solo {len(X)} righe disponibili dopo la pulizia. Servono almeno 10 righe!")
        
        print(f"🎯 Allenamento modello con {len(X)} righe...")
        
        # Split dei dati (80% training, 20% test)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"   📚 Training set: {len(X_train)} righe")
        print(f"   🧪 Test set: {len(X_test)} righe")
        
        # Scaling delle features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Usiamo Classifier perché prevediamo categorie (decisioni)
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        # Training
        print("⏳ Training in corso...")
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
        
        if len(y_test) > 0:
            print(f"✅ Dettaglio per classe:")
            print(classification_report(y_test, y_pred, 
                                      target_names=self.label_encoders['target'].classes_))
        
        return accuracy

    # ... (il resto dei metodi rimane uguale)
    def predict_decision(self, client_data):
        """
        Prevede la decisione AI per un nuovo cliente
        """
        if not self.is_trained:
            raise ValueError("❌ Modello non addestrato! Chiama train() prima.")
        
        # Converti in DataFrame
        client_df = pd.DataFrame([client_data])
        
        # Applica lo stesso feature engineering del training
        client_processed = self._prepare_single_prediction(client_df)
        
        # Scaling
        client_scaled = self.scaler.transform(client_processed)
        
        # Previsione
        prediction_encoded = self.model.predict(client_scaled)[0]
        prediction_proba = self.model.predict_proba(client_scaled)[0]
        
        # Decodifica
        prediction = self.label_encoders['target'].inverse_transform([prediction_encoded])[0]
        
        return {
            'decisione_prevista': prediction,
            'probabilita': max(prediction_proba),
            'tutte_probabilita': dict(zip(
                self.label_encoders['target'].classes_, 
                prediction_proba
            )),
            'features_utilizzate': list(client_processed.columns)
        }

    def _prepare_single_prediction(self, df):
        """
        Prepara i dati per una singola predizione
        """
        X = df.copy()
        
        # Converti colonne numeriche
        X = self._convert_numeric_columns(X)
        
        # Applica encoding alle features categoriche
        for feature, encoder in self.label_encoders.items():
            if feature != 'target' and feature in X.columns:
                try:
                    if X[feature].iloc[0] not in encoder.classes_:
                        print(f"⚠️  Valore '{X[feature].iloc[0]}' non visto in training per '{feature}'")
                        X[feature] = encoder.classes_[0]
                    else:
                        X[feature] = encoder.transform([X[feature].iloc[0]])[0]
                except Exception as e:
                    print(f"⚠️  Errore encoding {feature}: {e}")
                    X[feature] = 0  # Valore di default
        
        # Feature engineering (come in prepare_features)
        try:
            if 'rata' in X.columns and 'diff_reddito' in X.columns:
                sostenibilita = float(X['rata'].iloc[0]) / float(X['diff_reddito'].iloc[0]) if float(X['diff_reddito'].iloc[0]) > 0 else 1
                X['sostenibilita_alta'] = 1 if sostenibilita >= 0.35 else 0
                X['sostenibilita_media'] = 1 if 0.21 <= sostenibilita <= 0.34 else 0
                X['sostenibilita_bassa'] = 1 if sostenibilita <= 0.20 else 0
            
            if 'reddito_mensie' in X.columns and 'altre_spese' in X.columns:
                X['reddito_dopo_spese'] = float(X['reddito_mensie'].iloc[0]) - float(X['altre_spese'].iloc[0])
            
            if 'anticipo' in X.columns and 'costo_auto' in X.columns and float(X['costo_auto'].iloc[0]) > 0:
                X['rapporto_anticipo_costo'] = float(X['anticipo'].iloc[0]) / float(X['costo_auto'].iloc[0])
                
        except Exception as e:
            print(f"⚠️  Errore feature engineering predizione: {e}")
        
        # Seleziona solo le colonne usate nel training
        if hasattr(self, 'feature_importance') and self.feature_importance is not None:
            training_columns = self.feature_importance['feature'].tolist()
            available_columns = [col for col in training_columns if col in X.columns]
            return X[available_columns]
        else:
            return X

    def explain_prediction(self, client_data):
        """
        Spiega la previsione mostrando le feature più influenti
        """
        if not self.is_trained:
            raise ValueError("❌ Modello non addestrato!")
        
        prediction = self.predict_decision(client_data)
        
        print("\n" + "=" * 50)
        print("🔍 SPIEGAZIONE PREVISIONE")
        print("=" * 50)
        print(f"🎯 Decisione prevista: {prediction['decisione_prevista']}")
        print(f"📊 Probabilità: {prediction['probabilita']:.2%}")
        
        print(f"\n📈 FEATURE PIÙ INFLUENTI NEL MODELLO:")
        if self.feature_importance is not None:
            top_features = self.feature_importance.head(8)
            for _, row in top_features.iterrows():
                stars = "⭐" * int(row['importance'] * 20)
                print(f"   {row['feature']:25} {row['importance']:.3f} {stars}")
        
        print(f"\n🔢 PROBABILITÀ PER OGNI DECISIONE:")
        for decisione, prob in prediction['tutte_probabilita'].items():
            print(f"   {decisione:30} {prob:.2%}")
        
        return prediction

    def save_model(self, filename='../file/model.pkl'):
        """Salva il modello addestrato"""
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

    def load_model(self, filename='../file/model.pkl'):
        """Carica un modello addestrato"""
        model_data = joblib.load(filename)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.label_encoders = model_data['label_encoders']
        self.feature_importance = model_data['feature_importance']
        self.is_trained = True
        
        print(f"✅ Modello caricato: {filename}")

def main():
    """Esempio completo di utilizzo"""
    
    print("🚀 AGENTE AI PREDITTIVIO PER ACQUISTO AUTO")
    print("=" * 60)
    predictor = CarPurchasePredictor()
    print("1. Inizializzazione dell'agente\n" +"=" * 60)
    df = predictor.load_data_from_db()
    print("2. Caricamento e preparazione dei dati\n" +"=" * 60)
    """
    La prima parte prepara i dati per l'usO.
    - traning
    - test
    """
    
    if df.empty:
        raise ValueError("❌ Nessun dato disponibile per il training")
    
    try:
        print("3. Preparazione features e addestramento...\n" + "=" * 60)
        X, y, feature_columns = predictor.prepare_features(df)
        accuracy = predictor.train(X, y)
        print(f"✅ Modello addestrato con accuracy: {accuracy:.2f}" + "\n" + "=" * 60)
        print("4. Salvataggio modello...\n" + "=" * 60)
        predictor.save_model()
        
        print("\n" + "=" * 60)
        print("🎉 AGENTE AI PREDITTIVO PRONTO!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Errore durante il training: {e}")
        print("💡 Verifica i dati nel database")

if __name__ == "__main__":
    main()