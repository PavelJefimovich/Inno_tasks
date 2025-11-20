"""Модуль с бизнес-логикой: создание индексов и выполнение аналитических запросов."""

from typing import List, Dict, Any, Sequence
from database import Database
from config import CURRENT_DATE


class QueryService:
    """Сервис для создания индексов и получения аналитических результатов."""

    @staticmethod
    def create_indexes(db: Database) -> None:
        """Создаёт составной индекс для ускорения всех аналитических запросов."""
        try:
            db.execute("ALTER TABLE students DROP INDEX IF EXISTS idx_opt")
        except Exception:
            pass

        db.execute("CREATE INDEX idx_opt ON students (room_id, birthday, sex)")
        print("Index created: idx_opt (room_id, birthday, sex)")

    @staticmethod
    def _rows_to_dicts(rows: Sequence[tuple], columns: List[str]) -> List[Dict[str, Any]]:
        """Преобразует список кортежей из БД в список словарей."""
        return [dict(zip(columns, row)) for row in rows]

    # ──────────────────────────────────────────────────────────────
    # Отдельные методы для каждого запроса — чисто и красиво!
    # ──────────────────────────────────────────────────────────────

    @staticmethod
    def get_rooms_with_students_count(db: Database) -> List[Dict[str, Any]]:
        """1. Количество студентов в каждой комнате."""
        rows = db.fetchall("""
            SELECT 
                r.name AS room, 
                COUNT(s.id) AS students_count
            FROM rooms r
            LEFT JOIN students s ON s.room_id = r.id
            GROUP BY r.id, r.name
            ORDER BY r.name
        """)
        return QueryService._rows_to_dicts(rows, ["room", "students_count"])

    @staticmethod
    def get_top_5_youngest_rooms(db: Database) -> List[Dict[str, Any]]:
        """2. Топ-5 комнат с самым молодым средним возрастом."""
        rows = db.fetchall(f"""
            SELECT 
                r.name AS room,
                ROUND(AVG(DATEDIFF('{CURRENT_DATE}', s.birthday) / 365.25), 2) AS avg_age
            FROM rooms r
            JOIN students s ON s.room_id = r.id
            GROUP BY r.id, r.name
            ORDER BY avg_age ASC
            LIMIT 5
        """)
        return QueryService._rows_to_dicts(rows, ["room", "avg_age"])

    @staticmethod
    def get_top_5_largest_age_diff(db: Database) -> List[Dict[str, Any]]:
        """3. Топ-5 комнат с наибольшей разницей в возрасте."""
        rows = db.fetchall(f"""
            SELECT 
                r.name AS room,
                ROUND(
                    (MAX(DATEDIFF('{CURRENT_DATE}', s.birthday)) 
                     - MIN(DATEDIFF('{CURRENT_DATE}', s.birthday))) / 365.25
                ) AS age_diff
            FROM rooms r
            JOIN students s ON s.room_id = r.id
            GROUP BY r.id, r.name
            HAVING COUNT(s.id) > 1
            ORDER BY age_diff DESC
            LIMIT 5
        """)
        return QueryService._rows_to_dicts(rows, ["room", "age_diff"])

    @staticmethod
    def get_mixed_gender_rooms(db: Database) -> List[Dict[str, Any]]:
        """4. Комнаты, где живут и мальчики, и девочки."""
        rows = db.fetchall("""
            SELECT r.name AS room
            FROM rooms r
            JOIN students s ON s.room_id = r.id
            GROUP BY r.id, r.name
            HAVING COUNT(DISTINCT s.sex) > 1
            ORDER BY r.name
        """)
        return QueryService._rows_to_dicts(rows, ["room"])

    # ──────────────────────────────────────────────────────────────
    # Главная функция — просто собирает всё вместе
    # ──────────────────────────────────────────────────────────────

    @staticmethod
    def get_results(db: Database) -> List[Dict[str, Any]]:
        """Собирает результаты всех аналитических запросов в один список."""
        return [
            {"type": "rooms_with_students", "data": QueryService.get_rooms_with_students_count(db)},
            {"type": "top_5_youngest_rooms", "data": QueryService.get_top_5_youngest_rooms(db)},
            {"type": "top_5_largest_age_diff", "data": QueryService.get_top_5_largest_age_diff(db)},
            {"type": "mixed_gender_rooms", "data": QueryService.get_mixed_gender_rooms(db)},
        ]