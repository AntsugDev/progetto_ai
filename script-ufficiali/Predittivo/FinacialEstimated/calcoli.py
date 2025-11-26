IMPORTO_BASE = float(200)
import pandas as pd
class Calcoli:
    def __init__(self):
        pass


    def calcola(self, dataTest):
        diff_reddito = dataTest['reddito'] - dataTest['altre_spese']
        taeg = float((8.33/100)) if dataTest['request'] >= 5000 else float((10.33/100))
        return diff_reddito, taeg

    def decisionAI(self, sostenibilita):
        if sostenibilita <= 0.35:
            return "Accettato"
        else:
            return "Condizioni da rivedere, perchè si è superato la soglia di rischio"  
    def calcola_rata(self,taeg, importo_fin, nr_rate):
        tam = taeg / 12
        importo_rata = (importo_fin*tam)/((1-(1+tam)**(-nr_rate)))
        return importo_rata
    def calcola_sostenibilita(self, rata, reddito):
        sostenibilita = rata / reddito
        return sostenibilita;   
    def rapporto_spese_reddito(self, altre_spese, reddito):
        rapporto = altre_spese / reddito
        return rapporto    
    def rata_for_year(self,nr_rate):
        return nr_rate / 12   
    def sostenibilita_request(self, request,reddito):
        return request / reddito
    def rischio(self,taeg,reddito,request):
        return taeg*self.sostenibilita_request(request,reddito)         
    def rapp_reddito_rata(self, reddito, rata):
        return (reddito / rata)
    def fascia_reddito(self,reddito):
        return pd.cut(reddito, bins=[0, 1000,2000,3000,4000,5000], labels=[1,2,3,4,5])     