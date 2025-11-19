import json
from database import Database

class DataLoader:
    @staticmethod
    def load_rooms(db: Database, path: str):
        with open(path, encoding="utf-8") as f:
            rooms = json.load(f)
        

        db.execute("DELETE FROM students")   # students - зависима таблица, есть foreign key
        db.execute("DELETE FROM rooms")      # 
        query = "INSERT INTO rooms (id, name) VALUES (%s, %s)"
        data = [(r["id"], r["name"]) for r in rooms]
        db.executemany(query, data)
        print(f"Numer of loaded rooms: {len(rooms)}")

    @staticmethod
    def load_students(db: Database, path: str):
        with open(path, encoding="utf-8") as f:
            students = json.load(f)
        
        db.execute("DELETE FROM students")  # всё удаляем
        query = """
            INSERT INTO students (name, birthday, sex, room_id)
            VALUES (%s, %s, %s, %s)
        """
        data = [(s["name"], s["birthday"], s["sex"], s["room"]) for s in students]
        db.executemany(query, data)
        print(f"Number of loaded students: {len(students)}")