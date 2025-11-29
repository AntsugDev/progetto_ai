import sys
import os

# Aggiungi la directory superiore al path di Python
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from fastapi import FastAPI
from request_validation import RequestValidation,ResponseValidation, Revision
from upload_model import UploadModel
from server import Server
from modelRevision import ModelRevision
from calcoli import Calcoli
from datetime import datetime
import pandas as pd

app = FastAPI(title="API di predizione finanziaria", version="1.0.0")    
upload_model = UploadModel()
model = upload_model.upload()
calcoli = Calcoli()
server = Server(app)


@app.get("/healt-check")
def healt_check():
    return {"status": "ok"}   

@app.post("/predict", response_model=ResponseValidation)
def predict(request: RequestValidation):
    try:
        X = {
            'reddito':request.reddito,
            'altre_spese':request.altre_spese,
            'request':request.request,
            'nr_rate':request.nr_rate
        }
        df = pd.DataFrame(X,columns=['reddito', 'altre_spese', 'request', 'nr_rate'])
        y_pred = model.predict(df)
        importo_rata = y_pred[:, 0]
        sostenibilita = y_pred[:, 1]

        revision = ModelRevision(sostenibilita[0],request)
        revision, lastId = revision.migliore_scelta()

        response =  ResponseValidation(
            data = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            reddito_netto=request.reddito,
            importo_da_fin=request.request,
            importo_rata=float(round(importo_rata[0], 2)),
            sostenibilita=float(round(sostenibilita[0]*100, 2)),
            decisione_ai=calcoli.decisionAI(sostenibilita[0])
        )

        if revision:
            revision = Revision({
                'nr_rate': revision['nr_rate'],
                'importo_rata': float(round(revision['importo_rata'], 2)),
                'sostenibilita': float(round(revision['sostenibilita']*100, 2))
            })
        
        return response
        
    except Exception as e:
        print(f"Errore durante la previsione: {str(e)}")
        raise e

server.run()       