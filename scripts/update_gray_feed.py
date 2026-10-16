#!/usr/bin/env python3
import os
import xml.etree.ElementTree as ET

from update_feed import (
    MAX_RETRIES,
    REQUEST_TIMEOUT,
    SOURCE_URL,
    fetch_xml,
    transform,
)


OUTPUT_FILE = os.environ.get("GRAY_OUTPUT_FILE", "docs/inroom-gray.xml").strip()
GRAY_GROUP = "grey"
PREFERRED_COLOR = "темно-серый"
PREFERRED_WIDTH = "120"
PREFERRED_LENGTH = "200"


def filter_gray_offers(tree: ET.ElementTree) -> int:
    offers_node = tree.getroot().find(".//offers")
    if offers_node is None:
        raise RuntimeError("Source feed has no <offers> node")

    gray_by_model: dict[str, list[ET.Element]] = {}
    for offer in offers_node.findall("offer"):
        if (offer.findtext("color_group") or "").strip() != GRAY_GROUP:
            continue
        model = (offer.findtext("model") or "").strip()
        if not model:
            raise RuntimeError("Gray offer has no model")
        gray_by_model.setdefault(model, []).append(offer)

    def preference(offer: ET.Element) -> tuple[int, int, int, str, str, str]:
        color = (offer.findtext("color") or "").strip().lower().replace("ё", "е")
        width = (offer.findtext("width") or "").strip()
        length = (offer.findtext("length") or "").strip()
        offer_id = (offer.findtext("offer_id") or "").strip()
        return (
            color != PREFERRED_COLOR,
            width != PREFERRED_WIDTH,
            length != PREFERRED_LENGTH,
            color,
            width,
            offer_id,
        )

    selected = {min(offers, key=preference) for offers in gray_by_model.values()}
    seen_ids: set[str] = set()
    for offer in list(offers_node.findall("offer")):
        if offer not in selected:
            offers_node.remove(offer)
            continue
        offer_id = (offer.findtext("offer_id") or "").strip()
        if not offer_id:
            raise RuntimeError("Selected gray offer has no offer_id")
        if offer_id in seen_ids:
            raise RuntimeError(f"Duplicate gray offer_id: {offer_id}")
        seen_ids.add(offer_id)

    return len(selected)


def write_atomic(tree: ET.ElementTree, output_file: str) -> None:
    output_dir = os.path.dirname(output_file) or "."
    os.makedirs(output_dir, exist_ok=True)
    temp_file = output_file + ".tmp"
    tree.write(temp_file, encoding="utf-8", xml_declaration=True)
    with open(temp_file, "rb") as generated:
        cleaned = b"\n".join(line.rstrip(b" \t") for line in generated.read().splitlines())
    with open(temp_file, "wb") as generated:
        generated.write(cleaned + b"\n")
    os.replace(temp_file, output_file)


def main() -> None:
    tree, source_count = transform(
        fetch_xml(SOURCE_URL, REQUEST_TIMEOUT, MAX_RETRIES)
    )
    gray_count = filter_gray_offers(tree)
    write_atomic(tree, OUTPUT_FILE)
    print(f"Source offers processed: {source_count}")
    print(f"Gray offers published: {gray_count}")
    print(f"Gray color group: {GRAY_GROUP}")
    print(f"Source URL: {SOURCE_URL}")
    print(f"Output file: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
