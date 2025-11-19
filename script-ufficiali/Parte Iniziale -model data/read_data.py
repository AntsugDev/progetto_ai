import pandas as pd 
import pymysql
import uuid

try:
   
    data = pd.read_csv("../file/datamodel.csv")

    # 🔥 Converti automaticamente tutte le colonne numeriche con virgola
    for col in ["reddito_mensile_netto", "altre_spese", "costo_auto", "anticipo", "tan"]:
        data[col] = data[col].astype(str).str.replace(",", ".").astype(float)

    conn = pymysql.connect(
        host="localhost",
        user="asugamele",
        password="83Asugamele@",
        database="projectAI",
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    cursor.execute("DELETE FROM simulation;")
    cursor.execute("DELETE FROM model;")
    conn.commit()
    for row in data.itertuples(index=False):
        cliente = str(uuid.uuid4())

        reddito = row.reddito_mensile_netto
        altre_spese = row.altre_spese
        diff_reddito = reddito - altre_spese
        oneri_accessori = row.costo_auto * 0.1

        cursor.execute(
            """
            INSERT INTO projectAI.model
            (cliente, eta, neo_patentato_id, nr_figli, reddito_mensie, altre_spese, diff_reddito, sesso_id, zona_id, tipologia_auto_id, nuovo_usato_id, costo_auto, eta_veicolo, oneri_accessori, anticipo, tan, formula_acquisto_id, nr_rate)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                cliente,
                int(row.eta),
                int(row.neo_patentato)+1,
                int(row.nr_figli),
                reddito,
                altre_spese,
                diff_reddito,
                int(row.sesso)+1,
                int(row.zona)+1,
                int(row.tipologia_auto)+1,
                int(row.nuovo_usato)+1,
                row.costo_auto,
                int(row.eta_veicolo),
                oneri_accessori,
                row.anticipo,
                row.tan,
                int(row.formula_acquisto_preferita)+1,
                int(row.nr_rate)
            )
        )

    conn.commit()
    cursor.close()
    conn.close()
    print("Operazione terminata")
except Exception as e:
    print("eccezione", e)

