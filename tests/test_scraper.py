import tempfile
import unittest
from pathlib import Path

from price_scraper.cli import main
from price_scraper.parser import parse_price, parse_products
from price_scraper.report import changes_to_csv
from price_scraper.storage import PriceDB

FIXTURE = Path(__file__).parent / "fixtures" / "shop.html"


class ParsePriceTest(unittest.TestCase):
    def test_formats(self):
        self.assertEqual(parse_price("Rp 1.250.000"), 1250000)
        self.assertEqual(parse_price("$1,299.99"), 1299.99)
        self.assertEqual(parse_price("Rp 189.000"), 189000)
        self.assertEqual(parse_price("12,5"), 12.5)
        self.assertEqual(parse_price("999"), 999)

    def test_invalid(self):
        self.assertIsNone(parse_price("Hubungi kami"))
        self.assertIsNone(parse_price(""))
        self.assertIsNone(parse_price(None))


class ParseProductsTest(unittest.TestCase):
    def test_fixture(self):
        products = parse_products(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual([p["name"] for p in products], ["Laptop Pro 14", "Mouse Wireless", "Headset Gaming"])
        self.assertEqual(products[0]["price"], 15499000)
        self.assertEqual(products[2]["price"], 1299.99)  # harga di dalam div bersarang

    def test_custom_classes(self):
        html = '<li class="item"><i class="t">A</i><i class="p">10.000</i></li>'
        self.assertEqual(parse_products(html, "item", "t", "p"), [{"name": "A", "price": 10000}])


class StorageTest(unittest.TestCase):
    def test_price_change(self):
        db = PriceDB()
        db.save([{"name": "A", "price": 100}], when="t1")
        db.save([{"name": "A", "price": 110}, {"name": "B", "price": 5}], when="t2")
        changes = {c["name"]: c for c in db.latest_changes()}
        self.assertEqual(changes["A"]["change_pct"], 10.0)
        self.assertIsNone(changes["B"]["change_pct"])

    def test_csv(self):
        csv_text = changes_to_csv([{"name": "A, B", "current": 110, "previous": 100, "change_pct": 10.0}])
        self.assertIn('"A, B",110,100,10.0', csv_text)


class CliTest(unittest.TestCase):
    def test_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            db, out = str(Path(tmp) / "p.db"), str(Path(tmp) / "r.csv")
            self.assertEqual(main([str(FIXTURE), "--db", db, "--csv", out]), 0)
            self.assertEqual(main([str(FIXTURE), "--db", db, "--csv", out]), 0)
            self.assertIn("Laptop Pro 14", Path(out).read_text(encoding="utf-8"))

    def test_missing_source(self):
        self.assertEqual(main(["tidak-ada.html"]), 1)


if __name__ == "__main__":
    unittest.main()
