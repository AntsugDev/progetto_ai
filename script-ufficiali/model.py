import csv
import pymysql
import math

def getSoglia(connection):
    try:
        with connection.cursor() as cursor:
            # Recupera min, max e media in una sola query
            sql = """
                SELECT 
                    ROUND(AVG(md.diff_reddito), 2) AS media,
                    MIN(md.diff_reddito) AS minimo,
                    MAX(md.diff_reddito) AS massimo
                FROM model_data md
            """
            cursor.execute(sql)
            
            result = cursor.fetchone()
            
            if not result or result['media'] is None:
                raise ValueError("Nessun risultato trovato o result è NULL")
            
            media = result['media']
            minimo = result['minimo']
            massimo = result['massimo']
            
            # Esempio di calcolo personalizzato
            soglia = round(media + (media * (media / massimo)), 2)
            
            return soglia
                
    except (pymysql.Error, ValueError) as e:
        print(f"Errore getSoglia: {e}")
        return None
        
def get_importo_finanziato(formula, costo_auto):
        if(formula):
            return costo_auto*0.1
        else:
            return costo_auto

def get_rata(nr_rate, tan, importo):
     try:
        if nr_rate <= 0:
            return 0
        tam = tan / 12
        numeratore = importo * tam
        denominatore = 1 - ((1 + tam) ** -nr_rate)
        if denominatore == 0:
            return 0
        return numeratore / denominatore
     except:
        return 0

def sostenibilita(reddito, rata):
    return round(rata/reddito,2)
        
        

def main():
    conn = None
    try:
        conn = pymysql.connect(
            host="localhost",
            user="asugamele",
            password="83Asugamele@",
            database="projectAI",
            cursorclass=pymysql.cursors.DictCursor
        )
        
        sogliaReddito = getSoglia(conn)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM model_data")
        rows = cursor.fetchall()
        for idx, row in enumerate(rows, start=1):
            costo = float(row["costo_auto"])
            formula_nuova = not bool(row["nuovo_usato"])
            nr_rate=int(row['nr_rate'])
            tan    =float(row['tan'])
            importo_fin   = get_importo_finanziato(formula_nuova, costo)
            rata          = get_rata(nr_rate, tan,importo_fin)
            
            
    except Exception as e:
        print(f"Errore main: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
