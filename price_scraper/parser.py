"""Parser HTML untuk daftar produk, memakai html.parser bawaan Python."""
import re
from html.parser import HTMLParser


def parse_price(text):
    """Ubah teks harga ('Rp 1.250.000', '$1,299.99') menjadi float. None jika gagal."""
    cleaned = re.sub(r"[^\d.,]", "", text or "")
    if not cleaned:
        return None
    last_dot, last_comma = cleaned.rfind("."), cleaned.rfind(",")
    sep = max(last_dot, last_comma)
    # Pemisah desimal hanya jika diikuti 1-2 digit di akhir
    if sep != -1 and len(cleaned) - sep - 1 in (1, 2):
        integer = re.sub(r"[.,]", "", cleaned[:sep])
        value = f"{integer}.{cleaned[sep + 1:]}"
    else:
        value = re.sub(r"[.,]", "", cleaned)
    try:
        return float(value)
    except ValueError:
        return None


class _ProductParser(HTMLParser):
    def __init__(self, item_class, name_class, price_class):
        super().__init__()
        self.item_class, self.name_class, self.price_class = item_class, name_class, price_class
        self.products = []
        self._current = None
        self._item_depth = 0
        self._field = None

    @staticmethod
    def _classes(attrs):
        return (dict(attrs).get("class") or "").split()

    def handle_starttag(self, tag, attrs):
        classes = self._classes(attrs)
        if self._current is None:
            if self.item_class in classes:
                self._current = {"name": "", "price_text": ""}
                self._item_depth = 1
            return
        self._item_depth += 1
        if self.name_class in classes:
            self._field = "name"
        elif self.price_class in classes:
            self._field = "price_text"

    def handle_endtag(self, tag):
        if self._current is None:
            return
        self._field = None
        self._item_depth -= 1
        if self._item_depth == 0:
            name = self._current["name"].strip()
            price = parse_price(self._current["price_text"])
            if name and price is not None:
                self.products.append({"name": name, "price": price})
            self._current = None

    def handle_data(self, data):
        if self._current is not None and self._field:
            self._current[self._field] += data


def parse_products(html, item_class="product", name_class="name", price_class="price"):
    parser = _ProductParser(item_class, name_class, price_class)
    parser.feed(html)
    return parser.products
