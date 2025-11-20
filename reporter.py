from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from typing import Any, Sequence
import xml.etree.ElementTree as ET
from xml.dom import minidom


def _to_serializable(obj: Any) -> str | int | float:
    """Reorg unsupported json types .    """
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    return str(obj)


class Reporter:

    @staticmethod
    def to_json(data: Sequence[dict[str, Any]], filepath: str | Path | None = None) -> None:
        """save res in json        """
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
        """save as XML        """
        root = ET.Element("results")

        for section in data:
            section_elem = ET.SubElement(root, "section", type=section["type"])
            for item in section["data"]:
                item_elem = ET.SubElement(section_elem, "item")
                for key, value in item.items():
                    child = ET.SubElement(item_elem, key)
                    child.text = str(_to_serializable(value))

        # formatting in xml
        rough = ET.tostring(root, encoding="utf-8")
        reparsed = minidom.parseString(rough)
        pretty = reparsed.toprettyxml(indent="  ")
        # delete first empty row, added by toprettyxml
        clean_xml = "\n".join(line for line in pretty.splitlines() if line.strip())

        if filepath:
            Path(filepath).write_text(clean_xml + "\n", encoding="utf-8")
            print(f"XML saved → {Path(filepath).resolve()}")
        else:
            print(clean_xml)