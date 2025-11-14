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

def get_sostenibilita(reddito, rata):
    return round(rata/reddito,3)

def get_K(sostenibilita):
  if(sostenibilita >= 0.20):
    K = round(sostenibilita/0.20,3)
    return K;
  return 0;

def Rincome(reddito, soglia):
    if(reddito >= soglia): return 1
    elif(reddito >= (soglia *0.8)):
       return 2;
    elif(reddito >= (soglia *0.6)):
       return 3;
    elif(reddito >= (soglia *0.4)):
       return 4;
    else: return 5;
    
def Ranticipo(formula,anticipo):
    if(!formula): return 1;
    else:
        if(anticipo >= 25): return 1
        elif(anticipo >= 15 && anticipo <= 24): return 2
        elif(anticipo >= 5 && anticipo <= 14): return 3
        else: return 4;
    
anticipo >= 15 && anticipo <= 24
def get_RE(reddito, anticipo,formula, soglia):
    Ri = Rincome(reddito,soglia)
    Ra = Ranticipo(formula,anticipo)

def get_RS(sostenibilita):
    if(sostenibilita <= 0.15): return 1;
    elif(sostenibilita >= 0.16 &&  sostenibilita <= 0.20): return  2
    elif(sostenibilita >= 0.21 &&  sostenibilita <= 0.29): return  3
    elif(sostenibilita >= 0.30 &&  sostenibilita <= 0.34): return  4
    else: return 5;
    

def get_RT():
    RE = 0;
    RS = 0;
    RD = 0;
    RT = round((0.5*RE) +(0.3*RS) +(0.2*RD), 2);
  

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
            costo         = float(row["costo_auto"])
            formula_nuova = not bool(row["nuovo_usato"])
            nr_rate       = int(row['nr_rate'])
            tan           = float(row['tan'])
            reddito       = float(row['diff_reddito'])
            importo_fin   = get_importo_finanziato(formula_nuova, costo)
            rata          = get_rata(nr_rate, tan,importo_fin)
            sostenibilita = get_sostenibilita(reddito, rata)
            coefficiente_K= get_K(sostenibilita)
            
            print(f"{idx}\ncosto={costo}\nnuova_usata={formula_nuova}\nnrrate={nr_rate}\n reddito={reddito}\nimport_fin={importo_fin}\nrata={rata}\nsostenibilita={sostenibilita}\nK={coefficiente_K}\n------------------------------\n")
            
            
    except Exception as e:
        print(f"Errore main: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
