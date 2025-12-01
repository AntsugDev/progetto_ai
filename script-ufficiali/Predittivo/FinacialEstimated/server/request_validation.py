from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class RequestValidation(BaseModel):
     reddito: float = Field(...)
     altre_spese: float = Field(...)
     request: float = Field(...)
     nr_rate: int = Field(...)
class Revision(BaseModel):
     nr_rate: int = Field(...)
     importo_rata : float = Field(...)
     sostenibilita : float = Field(...)
     prevision: str = Field(...)


class ResponseValidation(BaseModel):
     data : datetime = Field(...)
     reddito_netto:float = Field(...)
     importo_da_fin: float = Field(...)
     importo_rata : float = Field(...)
     sostenibilita : float = Field(...)
     decisione_ai : str = Field(...)
     revision: Optional[Revision] = None

     