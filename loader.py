import json
from typing import Any
from database import Database


class DataLoader:

    @staticmethod
    def load_rooms(db: Database, path: str) -> None:
        """Clear table rooms and load  """
        with open(path, encoding="utf-8") as f:
            rooms: list[dict[str, Any]] = json.load(f)

        # delete students (because of foreign key) then rooms 
        db.execute("DELETE FROM students")
        db.execute("DELETE FROM rooms")

        query = "INSERT INTO rooms (id, name) VALUES (%s, %s)"
        data = [(room["id"], room["name"]) for room in rooms]

        db.executemany(query, data)
        print(f"Number of loaded rooms: {len(rooms)}")

    @staticmethod
    def load_students(db: Database, path: str) -> None:
        """Clear table students and load .
        
        field:
            - name: str
            - birthday: str  YYYY-MM-DD
            - sex: "M" or "F"
            - room: int (room id , room_id in DB) 
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