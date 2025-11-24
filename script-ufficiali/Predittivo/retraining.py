# retraining_manager.py
import pandas as pd
import joblib
import os
from datetime import datetime, timedelta

class RetrainingManager:
    """
    Gestisce il retraining automatico del modello
    """
    
    def __init__(self, soglia_clienti=50, soglia_giorni=7):
        self.soglia_clienti = soglia_clienti
        self.soglia_giorni = soglia_giorni
        self.contatore_clienti = 0
        self.ultimo_training = self._carica_ultimo_training()
        
    def _carica_ultimo_training(self):
        """Carica la data dell'ultimo training"""
        try:
            metadata = joblib.load('../../model/training_metadata.pkl')
            return metadata.get('ultimo_training')
        except:
            return None
    
    def _salva_metadata_training(self):
        """Salva i metadati del training"""
        metadata = {
            'ultimo_training': pd.Timestamp.now(),
            'clienti_da_ultimo_training': self.contatore_clienti,
            'soglia_clienti': self.soglia_clienti
        }
        joblib.dump(metadata, '../../model/training_metadata.pkl')
    
    def cliente_aggiunto(self):
        """Da chiamare dopo ogni nuovo cliente"""
        self.contatore_clienti += 1
        print(f"📊 Clienti da ultimo training: {self.contatore_clienti}/{self.soglia_clienti}")
        
        # Controlla se è ora di fare retraining
        if self._deve_fare_retraining():
            return self._esegui_retraining()
        return False
    
    def _deve_fare_retraining(self):
        """Decide se è il momento di fare retraining"""
        # Per numero di clienti
        if self.contatore_clienti >= self.soglia_clienti:
            return True
        
        # Per tempo trascorso (almeno una volta a settimana)
        if self.ultimo_training:
            giorni_trascorsi = (pd.Timestamp.now() - self.ultimo_training).days
            if giorni_trascorsi >= self.soglia_giorni:
                return True
        
        return False
    
    def _esegui_retraining(self):
        """Esegue il retraining"""
        try:
            print("🔄 AVVIO RETRAINING AUTOMATICO...")
            
            # Importa e esegue il training
            from train_model import ModelCustom
            trainer = ModelCustom()
            nuovo_modello = trainer.create()
            
            if nuovo_modello:
                print("✅ RETRAINING COMPLETATO!")
                self.contatore_clienti = 0
                self.ultimo_training = pd.Timestamp.now()
                self._salva_metadata_training()
                return True
            else:
                print("❌ RETRAINING FALLITO")
                return False
                
        except Exception as e:
            print(f"❌ Errore durante retraining: {e}")
            return False
    
    def forza_retraining(self):
        """Forza il retraining immediato"""
        return self._esegui_retraining()