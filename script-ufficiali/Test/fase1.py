import pandas as pd
import pymysql
from fase2 import rewrite_df 
from fase3 import train_and_evaluate
"""Connessione al Db ed estrazione dei dati per convertirli in data set"""
DB_CONF = {
    "host": "localhost",
    "user": "asugamele",           # aggiorna se necessario
    "password": "83Asugamele@",    # aggiorna se necessario
    "database": "projectAI",
    "cursorclass": pymysql.cursors.DictCursor
}

conn = pymysql.connect(**DB_CONF)
try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM model")
            rows = cur.fetchall()
            df = pd.DataFrame(rows)
            df_new = rewrite_df(df)
            r1,r2 = train_and_evaluate(df)
            print(r1)
finally:
        conn.close()
    
