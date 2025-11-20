# config.py
from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем .env из корня проекта
load_dotenv(Path(__file__).parent / ".env")

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "university"),
    "charset": os.getenv("MYSQL_CHARSET", "utf8mb4"),
    "autocommit": True,
}

# Дата для расчёта возраста
CURRENT_DATE: str = os.getenv("CURRENT_DATE", "2025-11-17")