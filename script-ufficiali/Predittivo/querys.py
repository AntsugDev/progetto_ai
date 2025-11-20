def getColumns(data):
    return ",".join(data)

def getVales(data):
    return ",".join(["%s"] * len(data))    

columns = ["cliente", "eta", "neo_patentato_id", "nr_figli", "reddito_mensie", "altre_spese", "diff_reddito", "sesso_id", "zona_id", "tipologia_auto_id", "nuovo_usato_id", "costo_auto", "eta_veicolo", "oneri_accessori", "anticipo", "tan", "formula_acquisto_id", "nr_rate", "importo_finanziato", "rata", "sostenibilita", "coefficiente_k", "re", "rs", "rd", "rt", "decisione_AI", "is_simulation"]
columnsSimA= ["model_id", "simulation_type_id", "anticipo", "importo_finanziato", "importo_rata", "sostenibilita", "decisione", "decision_ai"]
columnsSimB= ["model_id", "simulation_type_id", "nr_rata","rata", "sostenibilita", "decisione", "decision_ai"]
INSERT_MODEL = """INSERT INTO modello ({}) VALUES ({})""".format(getColumns(columns),getVales(columns))
INSERT_SIMULATION_A = """INSERT INTO simulation ({}) VALUES ({})""".format(getColumns(columnsSimA),getVales(columnsSimA))
INSERT_SIMULATION_B = """INSERT INTO simulation ({}) VALUES ({})""".format(getColumns(columnsSimB),getVales(columnsSimB))
SELECT_ID = """ """