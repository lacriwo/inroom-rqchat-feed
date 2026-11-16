#!/usr/bin/env python3
import os
import xml.etree.ElementTree as ET

from update_feed import MAX_RETRIES, REQUEST_TIMEOUT, SOURCE_URL, fetch_xml


OUTPUT_FILE = os.environ.get(
    "PERFORMANCE_OUTPUT_FILE", "docs/inroom-performance.xml"
).strip()

PERFORMANCE_SELECTION = {
    "Абстракт": {"180x200", "160x190", "140x190", "140x200", "160x200", "180x190"},
    "Абстракт Элит": {"180x200", "180x190"},
    "Лайн": {"180x200", "160x200", "120x200"},
    "Оптима Лайт": {"160x190", "180x190", "120x190"},
    "Изи": {"160x190", "140x190"},
    "Оптима": {"160x200"},
    "Квадро": {"120x200"},
    "Дельта": {"140x190"},
    "Бокс": {"140x200", "140x190", "160x200", "120x190"},
    "Прайм": {"160x190"},
    "Мидл": {"180x200"},
}


def offer_params(offer: ET.Element) -> dict[str, str]:
    return {
        node.get("name", ""): (node.text or "").strip()
        for node in offer.findall("param")
    }


def filter_performance_offers(tree: ET.ElementTree) -> int:
    root = tree.getroot()
    offers_node = root.find(".//offers")
    if offers_node is None:
        raise RuntimeError("Source feed has no <offers> node")

    categories = {
        node.get("id", ""): (node.text or "").strip()
        for node in root.findall(".//categories/category")
    }

    kept = 0
    for offer in list(offers_node.findall("offer")):
        model = categories.get((offer.findtext("categoryId") or "").strip(), "")
        params = offer_params(offer)
        size = (
            f'{params.get("Ширина спального места, см", "")}'
            f'x{params.get("Длина спального места, см", "")}'
        )
        if model not in PERFORMANCE_SELECTION or size not in PERFORMANCE_SELECTION[model]:
            offers_node.remove(offer)
            continue
        kept += 1

    return kept


def write_atomic(tree: ET.ElementTree, output_file: str) -> None:
    output_dir = os.path.dirname(output_file) or "."
    os.makedirs(output_dir, exist_ok=True)
    temp_file = output_file + ".tmp"
    tree.write(temp_file, encoding="utf-8", xml_declaration=True)
    os.replace(temp_file, output_file)


def main() -> None:
    tree = ET.ElementTree(
        ET.fromstring(fetch_xml(SOURCE_URL, REQUEST_TIMEOUT, MAX_RETRIES))
    )
    performance_count = filter_performance_offers(tree)
    write_atomic(tree, OUTPUT_FILE)
    print(f"Performance offers published: {performance_count}")
    print(f"Models selected: {len(PERFORMANCE_SELECTION)}")
    print(f"Source URL: {SOURCE_URL}")
    print(f"Output file: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
