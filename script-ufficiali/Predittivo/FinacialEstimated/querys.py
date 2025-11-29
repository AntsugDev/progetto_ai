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


ALL_PREVISIONING = """ SELECT * FROM previsioning """ 

VERSION_MODEL = """ INSERT INTO model_versions
     (version, n_rows, mae_rata, rmse_rata, r2_rata,
      mae_sost, rmse_sost, r2_sost, best_params, model_path)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) """


CALL_LAST_VERSION = """ SELECT model_path FROM model_versions WHERE created_at = (SELECT MAX(created_at) FROM model_versions) """
SELECT_ALL_VERSION = """ SELECT * FROM model_versions """