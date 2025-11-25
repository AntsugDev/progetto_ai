INSERT_PREVISIONING = """
INSERT INTO previsioning (
     reddito, 
     importo_fin, 
     revision_nr_rata, 
     revision_importo_rata, 
     revision_sostenibilita, 
     revision_prevision
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

UPDATE_PREVISIONING = """ UPDATE previsioning SET is_accetable = %s WHERE id = %s """

UPDATE_MODEL = """ UPDATE model_fe SET nr_rate = %s, importo_rata = %s, sostenibilita = %s, updated_at = %s, sync = 'N' WHERE id = %s """


    