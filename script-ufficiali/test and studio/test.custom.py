# test per verificare quanto capito fino ad adesso prendendo il mio modello
from ..Predittivo/querys import SELECT_ALL
from ..Predittivo/connection import Connection
import pandas as pd
class ModelCustom:

    def __init__(self):
        self.conn = Connection()
        self.cursor = None
        self.df = pd.DataFrame
    
#todo costruire il mio modello secondo i test fatti in questa directory usando OneHotEncoder e Pipelines
    def main():


if __name__ == "__main__":
    m = ModelCustom()         