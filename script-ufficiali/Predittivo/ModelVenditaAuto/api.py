# api_server.py
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
import pandas as pd
import joblib
import uvicorn
from datetime import datetime
import logging

# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modelli Pydantic per la validazione
class ClienteRequest(BaseModel):
    eta: int
    neo_patentato: str
    nr_figli: int
    reddito_mensile: float
    altre_spese: float
    sesso: str
    zona: str
    tipologia_auto: str
    nuovo_usato: str
    costo_auto: float
    eta_veicolo: int = 0
    anticipo: float = 0
    formula_acquisto: str = "finanziamento classico auto usata"
    nr_rate: int = 36

class PredizioneResponse(BaseModel):
    success: bool
    decisione: str
    probabilita: float
    tutte_probabilita: Dict[str, float]
    id_database: Optional[int] = None
    simulazione: Optional[Dict[str, Any]] = None
    timestamp: str

# Inizializza FastAPI
app = FastAPI(
    title="AI Auto Financing API",
    description="API per predizioni di finanziamento auto con AI",
    version="1.0.0"
)

# Dipendenze (Singleton)
class ModelManager:
    _instance = None
    
    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.feature_importance = None
        self.db_updater = None
        self.retraining_manager = None
        self._carica_modelli()
    
    def _carica_modelli(self):
        """Carica i modelli all'avvio"""
        try:
            self.model = joblib.load("../../model/datamodel.pkl")
            self.label_encoder = joblib.load("../../model/label_encoder.pkl")
            self.feature_importance = joblib.load("../../model/feature_importance.pkl")
            
            # Import qui per evitare circular imports
            from update import DatabaseUpdater
            from retraining_manager import RetrainingManager
            
            self.db_updater = DatabaseUpdater()
            self.retraining_manager = RetrainingManager(soglia_clienti=10)
            
            logger.info("✅ Modelli e dipendenze caricati con successo")
            
        except Exception as e:
            logger.error(f"❌ Errore caricamento modelli: {e}")
            raise e
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ModelManager()
        return cls._instance

# Dependency injection
def get_model_manager() -> ModelManager:
    return ModelManager.get_instance()

# Endpoints
@app.get("/")
async def root():
    """Endpoint di benvenuto"""
    return {
        "message": "🚗 AI Auto Financing API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check dell'API"""
    model_manager = get_model_manager()
    return {
        "status": "healthy",
        "model_loaded": model_manager.model is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/predici", response_model=PredizioneResponse)
async def predici_finanziamento(
    cliente: ClienteRequest,
    model_manager: ModelManager = Depends(get_model_manager)
):
    """
    Endpoint principale per predire il finanziamento auto
    """
    try:
        logger.info(f"📥 Richiesta predizione per cliente: {cliente.dict()}")
        
        # 1. Converti i dati in DataFrame
        data_tester = pd.DataFrame([cliente.dict()])
        
        # 2. Calcola valori finanziari (usa il tuo DatabaseUpdater)
        record, simulazione = model_manager.db_updater.data_predizione_ai(data_tester)
        
        if not record:
            raise HTTPException(status_code=400, detail="Errore nel calcolo valori finanziari")
        
        # 3. Prepara dati per la predizione
        cols_training = [
            'eta', 'neo_patentato', 'nr_figli', 'reddito_mensile', 'altre_spese',
            'sesso', 'zona', 'tipologia_auto', 'nuovo_usato', 'costo_auto',
            'eta_veicolo', 'anticipo', 'formula_acquisto', 'nr_rate',
            'importo_finanziato', 'rata', 'sostenibilita', 'coefficiente_k',
            're', 'rs', 'rd', 'rt', 'is_simulation'
        ]
        
        df_pred = pd.DataFrame(columns=cols_training)
        
        for col in df_pred.columns:
            if col in record:
                df_pred.at[0, col] = record[col]
            else:
                df_pred.at[0, col] = 0  # Valore default
        
        # 4. Fai la predizione
        predizione_numerica = model_manager.model.predict(df_pred)[0]
        probabilità = model_manager.model.predict_proba(df_pred)[0]
        
        # 5. Decodifica la risposta
        decisione = model_manager.label_encoder.inverse_transform([predizione_numerica])[0]
        
        # 6. Prepara le probabilità per tutte le decisioni
        tutte_decisioni = model_manager.label_encoder.classes_
        probabilità_dict = {
            dec: float(prob) 
            for dec, prob in zip(tutte_decisioni, probabilità)
        }
        
        # 7. Salva nel database
        id_database = model_manager.db_updater.create(data_tester)
        
        # 8. Controlla retraining
        if id_database:
            model_manager.retraining_manager.cliente_aggiunto()
        
        # 9. Prepara risposta
        response = PredizioneResponse(
            success=True,
            decisione=decisione,
            probabilita=float(max(probabilità)),
            tutte_probabilita=probabilità_dict,
            id_database=id_database,
            simulazione=simulazione,
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"✅ Predizione completata: {decisione}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Errore durante predizione: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/feature-importance")
async def get_feature_importance(
    model_manager: ModelManager = Depends(get_model_manager)
):
    """Restituisce l'importanza delle features"""
    try:
        if model_manager.feature_importance is None:
            raise HTTPException(status_code=404, detail="Feature importance non disponibile")
        
        features = model_manager.feature_importance.head(10).to_dict('records')
        return {
            "success": True,
            "features": features,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/retraining/forza")
async def forza_retraining(
    model_manager: ModelManager = Depends(get_model_manager)
):
    """Forza il retraining del modello"""
    try:
        success = model_manager.retraining_manager.forza_retraining()
        return {
            "success": success,
            "message": "Retraining forzato eseguito" if success else "Retraining fallito",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",  # Accessibile da qualsiasi IP
        port=8000,       # Porta standard
        reload=True      # Auto-reload durante sviluppo
    )