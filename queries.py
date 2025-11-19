from database import Database
from typing import List, Dict, Any

class QueryService:

    @staticmethod
    def create_indexes(db: Database):
        try:
            db.execute("ALTER TABLE students DROP INDEX IF EXISTS idx_opt")
        except:
            pass  
        db.execute("CREATE INDEX idx_opt ON students (room_id, birthday, sex)")
        print("Index created: idx_opt (room_id, birthday, sex)")

    @staticmethod
    def _rows_to_dicts(rows: List[tuple], columns: List[str]) -> List[Dict[str, Any]]:
        return [dict(zip(columns, row)) for row in rows]

    @staticmethod
    def get_results(db: Database):
        # 1
        rooms_rows = db.fetchall("""
            SELECT r.name AS room, COUNT(s.id) AS students_count
            FROM rooms r
            LEFT JOIN students s ON s.room_id = r.id
            GROUP BY r.id, r.name
            ORDER BY r.name
        """)
        rooms = QueryService._rows_to_dicts(rooms_rows, ["room", "students_count"])

        # 2 
        avg_age_rows = db.fetchall("""
            SELECT r.name AS room,
                   ROUND(AVG(
                       TIMESTAMPDIFF(YEAR, s.birthday, '2025-11-17')
                       - (DATE_FORMAT(s.birthday, '%%m-%%d') > '11-17')
                   ), 2) AS avg_age
            FROM rooms r
            JOIN students s ON s.room_id = r.id
            GROUP BY r.id
            ORDER BY avg_age ASC
            LIMIT 5
        """)
        smallest_avg_age = QueryService._rows_to_dicts(avg_age_rows, ["room", "avg_age"])

        # 3 
        diff_rows = db.fetchall("""
            SELECT r.name AS room,
                   MAX(
                       TIMESTAMPDIFF(YEAR, s.birthday, '2025-11-17')
                       - (DATE_FORMAT(s.birthday, '%%m-%%d') > '11-17')
                   ) - MIN(
                       TIMESTAMPDIFF(YEAR, s.birthday, '2025-11-17')
                       - (DATE_FORMAT(s.birthday, '%%m-%%d') > '11-17')
                   ) AS age_diff
            FROM rooms r
            JOIN students s ON s.room_id = r.id
            GROUP BY r.id
            HAVING COUNT(s.id) > 1
            ORDER BY age_diff DESC
            LIMIT 5
        """)
        largest_age_diff = QueryService._rows_to_dicts(diff_rows, ["room", "age_diff"])

        # 4
        mixed_rows = db.fetchall("""
            SELECT r.name AS room
            FROM rooms r
            JOIN students s ON s.room_id = r.id
            GROUP BY r.id
            HAVING COUNT(DISTINCT s.sex) > 1
            ORDER BY r.name
        """)
        mixed_gender_rooms = QueryService._rows_to_dicts(mixed_rows, ["room"])

        return [
            {"type": "rooms_with_students", "data": rooms},
            {"type": "top_5_youngest_rooms", "data": smallest_avg_age},
            {"type": "top_5_largest_age_diff", "data": largest_age_diff},
            {"type": "mixed_gender_rooms", "data": mixed_gender_rooms}
        ]