INSERT_PREVISIONING = """
INSERT INTO previsioning (
     reddito, importo_fin, importo_rata, sostenibilita, decision, revision_id
) VALUES (%s, %s, %s, %s, %s, %s)
"""

INSERT_REVISION = """ INSERT INTO revisions (
     nr_rata, importo_rata, sostenibilita
) VALUES (%s, %s, %s) """

UPDATE_PREVISIONING = """ UPDATE previsioning SET is_accetable = %s WHERE id = %s """

UPDATE_MODEL = """ UPDATE model_fe SET nr_rate = %s, importo_rata = %s, sostenibilita = %s, updated_at = %s, sync = 'N' WHERE id = %s """


    