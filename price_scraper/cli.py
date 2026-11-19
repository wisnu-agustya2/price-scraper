"""CLI: python -m price_scraper <url|file.html> [opsi]"""
import argparse
import sys
import urllib.request
from pathlib import Path

from .parser import parse_products
from .report import changes_to_csv
from .storage import PriceDB


def load_html(source):
    path = Path(source)
    if path.exists():
        return path.read_text(encoding="utf-8")
    if source.startswith(("http://", "https://")):
        req = urllib.request.Request(source, headers={"User-Agent": "price-scraper/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="replace")
    raise FileNotFoundError(f"Sumber tidak ditemukan: {source}")


def build_parser():
    p = argparse.ArgumentParser(prog="price_scraper", description="Scrape harga produk dan lacak perubahannya.")
    p.add_argument("source", help="URL atau path file HTML")
    p.add_argument("--db", default="prices.db", help="path database SQLite (default: prices.db)")
    p.add_argument("--csv", dest="csv_path", help="simpan laporan perubahan ke file CSV")
    p.add_argument("--item-class", default="product")
    p.add_argument("--name-class", default="name")
    p.add_argument("--price-class", default="price")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        html = load_html(args.source)
    except (OSError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    products = parse_products(html, args.item_class, args.name_class, args.price_class)
    if not products:
        print("Tidak ada produk ditemukan. Cek nama class CSS.", file=sys.stderr)
        return 2

    db = PriceDB(args.db)
    db.save(products)
    changes = db.latest_changes()
    db.close()

    print(f"{len(products)} produk disimpan.")
    for c in changes:
        arrow = "" if c["change_pct"] is None else f"  ({c['change_pct']:+.2f}%)"
        print(f"- {c['name']}: {c['current']:,.0f}{arrow}")

    if args.csv_path:
        Path(args.csv_path).write_text(changes_to_csv(changes), encoding="utf-8")
        print(f"Laporan CSV: {args.csv_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
