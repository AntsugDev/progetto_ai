from connection import ConnectionFe
from querys import *

class PDO:
    def __init__(self):
        c = ConnectionFe()
        self.conn = c.conn()
        self.cursor = self.conn.cursor()

    def insert(self,data):
        with self.cursor as cursor:
            cursor.execute(INSERT_PREVISIONING, data)
            self.conn.commit() 

    def update(self,data): 
        with self.cursor as cursor:
            cursor.execute(UPDATE_PREVISIONING, data) 
            self.conn.commit()        

    def is_accetable(self,data): 
        with self.cursor as cursor:
            cursor.execute(UPDATE_MODEL, data) 
            self.conn.commit()           
        