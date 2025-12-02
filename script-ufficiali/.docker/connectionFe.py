import pymysql

class ConnectionFe:

    def __init__(self):
        self.db_config = {
            'host': "localhost",
            'user': "asugamele", 
            'password': "83Asugamele@",
            'database': "finacial_estimated",
            'cursorclass': pymysql.cursors.DictCursor
        }

    def getDbConfig(self):
        return self.db_config   

    def conn(self):
        return pymysql.connect(**self.db_config)
