"""Модуль для загрузки данных из JSON-файлов в базу данных."""

import json
from typing import Any
from database import Database


class DataLoader:
    """Класс для загрузки данных о комнатах и студентах из JSON-файлов."""

    @staticmethod
    def load_rooms(db: Database, path: str) -> None:
        """Очищает таблицу rooms (и зависимую students из-за FK) и загружает новые комнаты.

        Args:
            db: Подключённый объект Database для выполнения запросов.
            path: Путь к файлу rooms.json в формате строки.

        Raises:
            json.JSONDecodeError: Если файл не является валидным JSON.
            OSError: Если файл не найден или нет прав на чтение.
        """
        with open(path, encoding="utf-8") as f:
            rooms: list[dict[str, Any]] = json.load(f)

        # Сначала удаляем студентов (из-за внешнего ключа), потом комнаты
        db.execute("DELETE FROM students")
        db.execute("DELETE FROM rooms")

        query = "INSERT INTO rooms (id, name) VALUES (%s, %s)"
        data = [(room["id"], room["name"]) for room in rooms]

        db.executemany(query, data)
        print(f"Number of loaded rooms: {len(rooms)}")

    @staticmethod
    def load_students(db: Database, path: str) -> None:
        """Очищает таблицу students и загружает новых студентов из JSON.

        Поля в JSON:
            - name: str
            - birthday: str в формате YYYY-MM-DD
            - sex: "M" или "F"
            - room: int (id комнаты, он же room_id в БД)

        Args:
            db: Подключённый объект Database.
            path: Путь к файлу students.json.

        Raises:
            json.JSONDecodeError: Если файл невалидный.
            OSError: Если файл недоступен.
            KeyError: Если в JSON отсутствует нужное поле (лучше отловить на этапе валидации).
        """
        with open(path, encoding="utf-8") as f:
            students: list[dict[str, Any]] = json.load(f)

        db.execute("DELETE FROM students")

        query = """
            INSERT INTO students (name, birthday, sex, room_id)
            VALUES (%s, %s, %s, %s)
        """
        data = [
            (student["name"], student["birthday"], student["sex"], student["room"])
            for student in students
        ]

        db.executemany(query, data)
        print(f"Number of loaded students: {len(students)}")