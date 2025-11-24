def getColumns(data):
    return ",".join(data)

def getVales(data):
    return ",".join(["%s"] * len(data))    

columns = ["cliente", "eta", "neo_patentato_id", "nr_figli", "reddito_mensile", "altre_spese", "diff_reddito", "sesso_id", "zona_id", "tipologia_auto_id", "nuovo_usato_id", "costo_auto", "eta_veicolo", "oneri_accessori", "anticipo", "tan", "formula_acquisto_id", "nr_rate", "importo_finanziato", "rata", "sostenibilita", "coefficiente_k", "re", "rs", "rd", "rt", "decisione_AI", "is_simulation"]
columnsSimA= ["model_id", "simulation_type_id", "anticipo", "importo_finanziamento", "importo_rata", "sostenibilita", "decisione", "decision_ai"]
columnsSimB= ["model_id", "simulation_type_id", "nr_rata","rata", "sostenibilita", "decisione", "decision_ai"]
INSERT_MODEL = f"""INSERT INTO model ({getColumns(columns)}) VALUES ({getVales(columns)}) """
INSERT_SIMULATION_A = f"""INSERT INTO simulation ({getColumns(columnsSimA)}) VALUES ({getVales(columnsSimA)})"""
INSERT_SIMULATION_B = f"""INSERT INTO simulation ({getColumns(columnsSimB)}) VALUES ({getVales(columnsSimB)})"""
SELECT_ID = """SELECT id FROM :table WHERE upper(TESTO) = upper(':value') """
SELECT_TAN =   """ select distinct cast(tan as DECIMAL(10,2)) as tan from model m left join nuovo_usato nu on (nu.id = m.nuovo_usato_id) WHERE upper(testo) = upper(%s) """ 
SELECT_ALL = """ SELECT
	cliente,
	eta,
	np.testo as neo_patentato,
	nr_figli,
	reddito_mensile,
	altre_spese,
	diff_reddito,
	s.testo as sesso,
	z.testo as zona,
	ta.testo as tipologia_auto,
	nu.testo as nuovo_usato,
	costo_auto,
	eta_veicolo,
	oneri_accessori,
	anticipo,
	tan,
	fa.testo as formula_acquisto,
	nr_rate,
	anticipo,
	m.importo_finanziato ,
	rata,
	m.sostenibilita ,
	m.coefficiente_k,
	re,
	rs,
	rd,
	rt,
	m.decisione_AI ,
	m.is_simulation 
FROM
	model m
left join neo_patentato np on
	(np.id = m.neo_patentato_id)
left join sesso s on
	(s.id = m.sesso_id)
left join zona z on
	(z.id = m.zona_id)
left join tipologia_auto ta on
	(ta.id = m.tipologia_auto_id)
left join nuovo_usato nu on
	(nu.id = m.nuovo_usato_id)
left join formula_acquisto fa on
	(fa.id = m.formula_acquisto_id)
	
	; """