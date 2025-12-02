import sys
import os

# Aggiungi la directory superiore al path di Python
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from fastapi import FastAPI,HTTPException, Depends, APIRouter
from request_validation import RequestValidation,ResponseValidation, Revision, AuthResponse, LoginRequest
from upload_model import UploadModel
from server import Server
from modelRevision import ModelRevision
from calcoli import Calcoli
from datetime import datetime
import pandas as pd
from data_create import DataCreate
from auth import *
from typing import Literal

app = FastAPI(title="API di predizione finanziaria", version="1.0.0")    
upload_model = UploadModel()
model = upload_model.upload()
calcoli = Calcoli()
server = Server(app)


@app.get("/healt-check")
def healt_check():
    return {"status": "ok"} 

@app.post("/login", response_model=AuthResponse)
def login(data: LoginRequest):
    #todo search user in db
    try:
        token = create_token(data.dict())
        if token:
            return AuthResponse(access_token=token)
        else:
            raise HTTPException(status_code=401, detail="Credenziali non valide")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Errore interno del server: {str(e)}")

protected_router = APIRouter(
    prefix="/api",
    dependencies=[Depends(verify_token)]  # JWT richiesto per TUTTO
)


@protected_router.post("/predict", response_model=ResponseValidation)
def predict(request: RequestValidation):
    try:
        X = {
            'reddito':request.reddito,
            'altre_spese':request.altre_spese,
            'request':request.request,
            'nr_rate':request.nr_rate
        }

        data = DataCreate(X)
        df = data.get_data()
        from clearData import ClearData
        clearData = ClearData(df)
        df_clear = clearData.clear()
        y_pred = model.predict(df_clear)
        importo_rata = y_pred[:, 0]
        sostenibilita = y_pred[:, 1]
#
        revision = ModelRevision(sostenibilita[0],X)
        revision, lastId = revision.migliore_scelta()
        
        if revision:
            revision = Revision(
                nr_rate= revision['nr_rate'],
                importo_rata= round(revision['importo_rata'], 2),
                sostenibilita= round(revision['sostenibilita'], 2),
                prevision= revision['prevision']
            )
        response =  ResponseValidation(
            data = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            reddito_netto=request.reddito,
            importo_da_fin=request.request,
            importo_rata=round(importo_rata[0], 2),
            sostenibilita=round(sostenibilita[0], 2),
            decisione_ai=calcoli.decisionAI(sostenibilita[0]),
            revision=revision if revision else None
        )
        return response

       
        
        
    except Exception as e:
        print(f"Errore durante la previsione: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Errore interno del server: {str(e)}")

@protected_router.get("/accept/{is_accept}/{id}")
def accept(is_accept: Literal['S','N'],id: int):
    try:
        from connectionFe import ConnectionFe
        from querys import UPDATE_PREVISIONING, VERIFY_PREVISIONING
        c = ConnectionFe().conn()
        cc = c.cursor()
        with cc as cursor:
            cursor.execute(VERIFY_PREVISIONING, (id))
            row = cursor.fetchone()
            if row['is_count'] == 0:
                raise HTTPException(status_code=404, detail="Previsione non trovata")
            cursor.execute(UPDATE_PREVISIONING, (is_accept, id)) 
        c.commit()
        return {"message": "Previsione aggiornata con accettata" if is_accept == 'S' else "Previsione aggiornata con rifiutata"}
    except Exception as e:
        print(f"Errore durante l'accept: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Errore interno del server: {str(e)}")
   

app.include_router(protected_router)

if __name__ == '__main__':
    server.run()       