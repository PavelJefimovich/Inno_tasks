"""Точка входа в приложение: загрузка данных, выполнение запросов и вывод результатов."""

from __future__ import annotations

import argparse
from pathlib import Path
from database import Database
from loader import DataLoader
from queries import QueryService
from reporter import Reporter


def parse_args() -> argparse.Namespace:
    """Настраивает и возвращает парсер командной строки с аргументами.

    Поддерживаемые параметры:
        rooms          — путь к rooms.json (по умолчанию рядом со скриптом)
        students       — путь к students.json
        -j / --json    — вывод в JSON (по умолчанию)
        -x / --xml     — вывод в XML
        -o / --output  — сохранить результат в файл

    Returns:
        Объект argparse.Namespace с распарсенными аргументами.
    """
    parser = argparse.ArgumentParser(
        description="Hostel analytics: load JSON → MySQL → analytical queries → JSON/XML output"
    )

    parser.add_argument(
        "rooms",
        nargs="?",
        type=Path,
        default=Path(__file__).parent / "rooms.json",
        help="Path to rooms.json (default: %(default)s)"
    )
    parser.add_argument(
        "students",
        nargs="?",
        type=Path,
        default=Path(__file__).parent / "students.json",
        help="Path to students.json (default: %(default)s)"
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-j", "--json",
        action="store_const",
        dest="format",
        const="json",
        help="Output result in JSON format (default)"
    )
    group.add_argument(
        "-x", "--xml",
        action="store_const",
        dest="format",
        const="xml",
        help="Output result in XML format"
    )

    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Save result to file. Extension .json or .xml will be added automatically if missing"
    )

    parser.set_defaults(format="json")
    return parser.parse_args()


def main() -> None:
    """Основная логика приложения."""
    args = parse_args()

    # Разрешаем пути и проверяем существование файлов
    rooms_path = args.rooms.resolve()
    students_path = args.students.resolve()

    for path, name in [(rooms_path, "rooms.json"), (students_path, "students.json")]:
        if not path.is_file():
            print(f"Error: file '{name}' not found!")
            print(f"   Expected path: {path}")
            raise SystemExit(1)

    print("Input files found:")
    print(f"   rooms.json   → {rooms_path}")
    print(f"   students.json → {students_path}")
    print("-" * 60)

    # Инициализация БД
    db = Database()
    db.connect()
    db.create_tables()

    # Загрузка данных
    DataLoader.load_rooms(db, str(rooms_path))
    DataLoader.load_students(db, str(students_path))

    # Аналитика
    QueryService.create_indexes(db)
    results = QueryService.get_results(db)

    print("\n" + "=" * 60)
    print("Analytical results:")
    print("=" * 60)

    # Определяем путь и формат вывода
    output_path: Path | None = args.output
    format_type: str = args.format

    if output_path:
        # Автоматически добавляем правильное расширение
        if output_path.suffix not in {".json", ".xml"}:
            output_path = output_path.with_suffix(f".{format_type}")

        if format_type == "json":
            Reporter.to_json(results, output_path)
        else:
            Reporter.to_xml(results, output_path)
    else:
        # Вывод в консоль
        if format_type == "json":
            Reporter.to_json(results)
        else:
            Reporter.to_xml(results)

    db.close()
    print("\nDone! Database connection closed.")


if __name__ == "__main__":
    main()