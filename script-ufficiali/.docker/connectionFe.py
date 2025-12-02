import pymysql

class ConnectionFe:

    def __init__(self):
        self.db_config = {
            'host': "172.18.0.1", #invece di localhost altrimenti il containe non trova il db
            'user': "asugamele", 
            'password': "83Asugamele@",
            'database': "finacial_estimated",
            'cursorclass': pymysql.cursors.DictCursor
        }

    def getDbConfig(self):
        return self.db_config   

    def conn(self):
        return pymysql.connect(**self.db_config)
