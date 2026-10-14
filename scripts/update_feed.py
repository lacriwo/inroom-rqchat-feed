#!/usr/bin/env python3
import os
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET


SOURCE_URL = os.environ.get(
    "SOURCE_FEED_URL", "https://in-room.ru/marketplace/4675585.xml"
).strip()
TARGET_URL = os.environ.get("TARGET_URL", "https://in-room.rqch.ru/").strip()
OUTPUT_FILE = os.environ.get("OUTPUT_FILE", "docs/inroom-rqchat.xml").strip()
REQUEST_TIMEOUT = int(os.environ.get("REQUEST_TIMEOUT", "120"))
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "3"))

PARAM_TO_TAG = {
    "Цвет": "color",
    "Ширина спального места, см": "width",
    "Длина спального места, см": "length",
    "Подъемный механизм": "lift",
}


def fetch_xml(url: str, timeout: int, retries: int) -> bytes:
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "inroom-rqchat-feed/1.0"})
            with urllib.request.urlopen(request, timeout=timeout) as response:
                status = getattr(response, "status", 200)
                if status >= 400:
                    raise RuntimeError(f"HTTP status {status}")
                return response.read()
        except (urllib.error.URLError, TimeoutError, RuntimeError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(attempt * 3)
    raise RuntimeError(f"Unable to fetch source feed after {retries} attempts: {last_error}")


def set_text(parent: ET.Element, tag: str, value: str) -> None:
    node = parent.find(tag)
    if node is None:
        node = ET.SubElement(parent, tag)
    node.text = value or ""


def transform(xml_data: bytes) -> tuple[ET.ElementTree, int]:
    root = ET.fromstring(xml_data)
    categories = {
        node.get("id", ""): (node.text or "").strip()
        for node in root.findall(".//categories/category")
    }
    offers = root.findall(".//offers/offer")

    for offer in offers:
        set_text(offer, "url", TARGET_URL)
        category_id = (offer.findtext("categoryId") or "").strip()
        set_text(offer, "model", categories.get(category_id, ""))

        params = {
            node.get("name", ""): (node.text or "").strip()
            for node in offer.findall("param")
        }
        for param_name, tag in PARAM_TO_TAG.items():
            set_text(offer, tag, params.get(param_name, ""))
        set_text(offer, "available_value", offer.get("available", ""))

    return ET.ElementTree(root), len(offers)


def main() -> None:
    tree, offer_count = transform(fetch_xml(SOURCE_URL, REQUEST_TIMEOUT, MAX_RETRIES))
    output_dir = os.path.dirname(OUTPUT_FILE) or "."
    os.makedirs(output_dir, exist_ok=True)
    temp_file = OUTPUT_FILE + ".tmp"
    tree.write(temp_file, encoding="utf-8", xml_declaration=True)
    os.replace(temp_file, OUTPUT_FILE)
    print(f"Offers processed: {offer_count}")
    print(f"Source URL: {SOURCE_URL}")
    print(f"Target URL: {TARGET_URL}")
    print(f"Output file: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

