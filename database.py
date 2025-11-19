import MySQLdb
from config import MYSQL_CONFIG

class Database:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = MySQLdb.connect(**MYSQL_CONFIG)
        self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)  # ← возвращает словари!

    def execute(self, query: str, params=None):
        self.cursor.execute(query, params or ())  ### Если params — это None, исп-ся пустой кортеж ()
        self.conn.commit()

    def fetchall(self, query: str, params=None):
        self.cursor.execute(query, params or ())  ### Если params — это None, исп-ся пустой кортеж ()
        return self.cursor.fetchall()   ## возврат списка словарей

    def executemany(self, query: str, data):
        self.cursor.executemany(query, data)
        self.conn.commit()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()