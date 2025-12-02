import sys
import os

# Aggiungi la directory superiore al path di Python
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from connectionFe import ConnectionFe
from querys import CALL_LAST_VERSION
import joblib
import os

class UploadModel:
    def __init__(self):
        self.conn = ConnectionFe().conn()
        self.cursor = self.conn.cursor()

    def upload(self):
        try:
            with self.cursor as cursor:
                cursor.execute(CALL_LAST_VERSION)
                row = cursor.fetchone()
                if row:
                    return joblib.load(os.path.join("model", row['model_path']))
              
        except Exception as e:
            print(f"Errore durante l'upload: {str(e)}")
            raise e    