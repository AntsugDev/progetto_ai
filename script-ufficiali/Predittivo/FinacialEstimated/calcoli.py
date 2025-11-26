IMPORTO_BASE = float(200)
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

         