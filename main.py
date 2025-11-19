import argparse
from pathlib import Path
from database import Database
from loader import DataLoader
from queries import QueryService
from reporter import Reporter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Data processing: loading, query, output in JSON/XML"
    )

    parser.add_argument(
        "rooms",
        nargs="?",
        type=Path,
        default=Path(__file__).parent / "rooms.json",
        help="Path to rooms.json "
    )
    parser.add_argument(
        "students",
        nargs="?",
        type=Path,
        default=Path(__file__).parent / "students.json",
        help="Path to  students.json "
    )


    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-j", "--json",
        action="store_const",
        dest="format",
        const="json",
        help="Output in JSON "
    )
    group.add_argument(
        "-x", "--xml",
        action="store_const",
        dest="format",
        const="xml",
        help="Output in XML"
    )

    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Save resuslt in file "
    )

    parser.set_defaults(format="json")   
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    rooms_path = args.rooms.resolve()
    students_path = args.students.resolve()

     
    for path, name in [(rooms_path, "rooms.json"), (students_path, "students.json")]:
        if not path.is_file():
            print(f"Error: file {name} is not found !")
            print(f"   Path: {path}")
            raise SystemExit(1)

    print("Files are founded:")
    print(f"   rooms.json   → {rooms_path}")
    print(f"   students.json → {students_path}")
    print("-" * 60)

    db = Database()
    db.connect()


    db.execute("DROP TABLE IF EXISTS students")
    db.execute("DROP TABLE IF EXISTS rooms")
    db.execute("CREATE TABLE rooms (id INT PRIMARY KEY, name VARCHAR(255) NOT NULL)")
    db.execute("""
        CREATE TABLE students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            birthday DATE NOT NULL,
            sex ENUM('M','F') NOT NULL,
            room_id INT NOT NULL,
            FOREIGN KEY (room_id) REFERENCES rooms(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    DataLoader.load_rooms(db, str(rooms_path))
    DataLoader.load_students(db, str(students_path))

    QueryService.create_indexes(db)
    results = QueryService.get_results(db)

    print("\n" + "=" * 60)
    print("Result:")
    print("=" * 60)

 
    output_path = args.output
    format_type = args.format

    if output_path:
 
        if output_path.suffix not in {".json", ".xml"}:
            output_path = output_path.with_suffix(f".{format_type}")

        if format_type == "json":
            Reporter.to_json(results, str(output_path))
        else:  
            Reporter.to_xml(results, str(output_path))

        print(f"Result is saved in {output_path}")
    else:

        if format_type == "json":
            Reporter.to_json(results)         
        else:
            Reporter.to_xml(results)          

    db.close()


if __name__ == "__main__":
    main()