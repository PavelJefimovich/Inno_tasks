# database.py
import MySQLdb
from config import MYSQL_CONFIG
from typing import Any


class Database:
    def __init__(self) -> None:
        """Инициализация объекта подключения к базе данных."""
        self.conn = None
        self.cursor = None

    def connect(self) -> None:
        """Устанавливает соединение с MySQL по настройкам из config.MYSQL_CONFIG."""
        self.conn = MySQLdb.connect(**MYSQL_CONFIG)
        self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

    def execute(self, query: str, params: tuple | None = None) -> None:
        """Выполняет один SQL-запрос с commit."""
        self.cursor.execute(query, params or ())
        self.conn.commit()

    def executemany(self, query: str, data: list[tuple]) -> None:
        """Выполняет один запрос с множеством наборов параметров и делает commit.

        Args:
            query: SQL-запрос с плейсхолдерами %s
            data: Список кортежей с данными (каждый кортеж — одна строка)
        """
        self.cursor.executemany(query, data)
        self.conn.commit()

    def fetchall(self, query: str, params: tuple | None = None) -> list[dict[str, Any]]:
        """Выполняет SELECT-запрос и возвращает все строки в виде списка словарей."""
        self.cursor.execute(query, params or ())
        return self.cursor.fetchall()

    def create_tables(self) -> None:
        """Удаляет старые таблицы (если есть) и создаёт заново rooms и students."""
        self.execute("DROP TABLE IF EXISTS students")
        self.execute("DROP TABLE IF EXISTS rooms")

        self.execute("""
            CREATE TABLE rooms (
                id INT PRIMARY KEY,
                name VARCHAR(255) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        self.execute("""
            CREATE TABLE students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                birthday DATE NOT NULL,
                sex ENUM('M','F') NOT NULL,
                room_id INT NOT NULL,
                FOREIGN KEY (room_id) REFERENCES rooms(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        print("Таблицы rooms и students успешно (пере)созданы!")

    def close(self) -> None:
        """Закрывает курсор и соединение с БД."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()