"""Модуль для вывода аналитических результатов в JSON и XML форматах."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from typing import Any, Sequence
import xml.etree.ElementTree as ET
from xml.dom import minidom


def _to_serializable(obj: Any) -> str | int | float:
    """Преобразует неподдерживаемые JSON типы (например, Decimal) в сериализуемые.

    Args:
        obj: Любой объект, который может прийти из результата запроса.

    Returns:
        str, int или float — безопасное для JSON/XML значение.
    """
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    return str(obj)


class Reporter:
    """Класс для форматированного вывода результатов в консоль или файл (JSON/XML)."""

    @staticmethod
    def to_json(data: Sequence[dict[str, Any]], filepath: str | Path | None = None) -> None:
        """Сохраняет результаты в JSON-формат с красивым отступом.

        Args:
            data: Список словарей с аналитическими результатами (то, что возвращает QueryService).
            filepath: Путь к файлу для сохранения. Если None — вывод в консоль.

        Example:
            >>> Reporter.to_json(results, "output/result.json")
        """
        json_str = json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
            default=_to_serializable
        ) + "\n"

        if filepath:
            Path(filepath).write_text(json_str, encoding="utf-8")
            print(f"JSON saved → {Path(filepath).resolve()}")
        else:
            print(json_str)

    @staticmethod
    def to_xml(data: Sequence[dict[str, Any]], filepath: str | Path | None = None) -> None:
        """Сохраняет результаты в человекочитаемый XML-формат.

        Структура:
            <results>
              <section type="...">
                <item>
                  <room>101</room>
                  <students_count>5</students_count>
                </item>
                ...
              </section>
            </results>

        Args:
            data: Тот же формат данных, что и для to_json.
            filepath: Путь к файлу. Если None — вывод в консоль.
        """
        root = ET.Element("results")

        for section in data:
            section_elem = ET.SubElement(root, "section", type=section["type"])
            for item in section["data"]:
                item_elem = ET.SubElement(section_elem, "item")
                for key, value in item.items():
                    child = ET.SubElement(item_elem, key)
                    child.text = str(_to_serializable(value))

        # Красивое форматирование XML
        rough = ET.tostring(root, encoding="utf-8")
        reparsed = minidom.parseString(rough)
        pretty = reparsed.toprettyxml(indent="  ")
        # Убираем первую пустую строку, которую добавляет toprettyxml
        clean_xml = "\n".join(line for line in pretty.splitlines() if line.strip())

        if filepath:
            Path(filepath).write_text(clean_xml + "\n", encoding="utf-8")
            print(f"XML saved → {Path(filepath).resolve()}")
        else:
            print(clean_xml)