#!/usr/bin/env python3
"""Download the official Olist dataset into data/raw/.

Source (official only):
  - Brazilian E-Commerce Public Dataset by Olist, from the official Olist
    GitHub hiring repo (same files as the Kaggle publication).
    https://github.com/olist/work-at-olist-data
    Canonical licence on the Kaggle publication by Olist: CC BY-NC-SA 4.0.
    https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce/

UCI Online Retail II is no longer downloaded. It was considered as a 1P
cost basis and dropped: its wholesale gift-retailer prices are not a
credible stocking-side basis.

This script never scrapes a marketplace catalogue.
"""
from __future__ import annotations

import hashlib
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
UA = "own-vs-list-open-data/1.0 (portfolio; non-commercial; Ami Sata)"

UCI_URL = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
UCI_ZIP_SHA256 = "572e36277c2390fbfde10664750731e0a86f55e33470d91919085f0408e67bfb"

OLIST_BASE = "https://raw.githubusercontent.com/olist/work-at-olist-data/master/datasets"
OLIST_FILES = {
    "olist_orders_dataset.csv": "8df58ef3d2d7e9944010f7beecd9b75367f5588ec6e3c91cec19ae3345ef9ecf",
    "olist_order_items_dataset.csv": "4f6abdbbc94036d0df4a76fa0520c072e31a40119d70f7f370fba1e2285d2bcb",
    "olist_products_dataset.csv": "3e6569628a17fbc75fd206ee357b59e20364b9afa90f5b6cd5b4d624c58aa9cc",
    "olist_order_reviews_dataset.csv": "012b61c7593e34f51fa614efdf802b9c7056ce6aae5307ddb93236e7cfc797d7",
    "olist_sellers_dataset.csv": "31eb9bd50d684526a78f2389413ce61841e97692de7b828fe7d956b534586312",
    "product_category_name_translation.csv": "a81f0d1f27b27e7293f761bc79e3ce8f348ee39c4b3ed3e49bde38f478586278",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(url: str, dest: Path, expected: str | None = None) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and expected and sha256(dest) == expected:
        print(f"ok (cached) {dest.name}")
        return dest
    print(f"downloading {url}")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r, dest.open("wb") as f:
        while True:
            chunk = r.read(1 << 16)
            if not chunk:
                break
            f.write(chunk)
    digest = sha256(dest)
    if expected and digest != expected:
        raise SystemExit(f"SHA-256 mismatch for {dest.name}: got {digest}")
    print(f"ok {dest.name} {digest}")
    return dest


def main() -> int:
    olist_dir = RAW / "olist"
    for name, digest in OLIST_FILES.items():
        fetch(f"{OLIST_BASE}/{name}", olist_dir / name, digest)
    print("done. raw files are gitignored; run scripts/build_products.py next.")
    print("UCI Online Retail II is not downloaded; it is not used as a 1P cost basis.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
