# reporter.py — финальная рабочая версия
import json
from decimal import Decimal
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom


def _to_serializable(obj):
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    return str(obj)


class Reporter:
    @staticmethod
    def to_json(data, filepath=None):
        json_str = json.dumps(data, indent=2, ensure_ascii=False, default=_to_serializable)
        if filepath:
            Path(filepath).write_text(json_str + "\n", encoding="utf-8")
        else:
            print(json_str)

    @staticmethod
    def to_xml(data, filepath=None):
        root = ET.Element("results")

        for section in data:
            section_elem = ET.SubElement(root, "section", type=section["type"])
            data_list = section["data"]
            for item in data_list:
                item_elem = ET.SubElement(section_elem, "item")
                for key, value in item.items():
                    child = ET.SubElement(item_elem, key)
                    child.text = str(_to_serializable(value))

        rough = ET.tostring(root, 'utf-8')
        reparsed = minidom.parseString(rough)
        pretty = reparsed.toprettyxml(indent="  ")
        clean = "\n".join(line for line in pretty.splitlines()[1:] if line.strip())

        if filepath:
            Path(filepath).write_text(clean + "\n", encoding="utf-8")
        else:
            print(clean)