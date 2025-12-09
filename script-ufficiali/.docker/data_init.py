import pandas as pd
from connectionFe import ConnectionFe
from querys import INSERT_MODEL_DATA

class DataInit:
    def __init__(self):
        c = ConnectionFe()
        self.connection = c.conn()
        self.cursor = self.connection.cursor()
        self.file_path = "./data_init/data_init.csv"

    def read_csv(self):
        try:
            reader = pd.read_csv(self.file_path, on_bad_lines='skip')
            print(f"Total rows read: {len(reader)}")
            for index, row in reader.iterrows():
                reddito = float(row['reddito'])
                altre_spese = float(row['altre_spese'])
                request = float(row['importo_finanziamento'])
                taeg = float((row['taeg']/100))
                nr_rate = int(row['nr_rate'])
                diff_reddito = (reddito-altre_spese)
                self.cursor.execute(INSERT_MODEL_DATA  , (
                    reddito,
                    altre_spese,
                    request,
                    taeg,
                    nr_rate,
                    diff_reddito,
                    float(0),
                    float(0)
                ))
            self.connection.commit()
            print("Data inserted successfully")
        except Exception as e:
            print("Exception")
            print(e)
            raise e
    

if __name__ == "__main__":
    d = DataInit()
    d.read_csv()   
    