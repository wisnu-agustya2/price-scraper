"""Penyimpanan riwayat harga di SQLite."""
import sqlite3
from datetime import datetime, timezone


class PriceDB:
    def __init__(self, path=":memory:"):
        self.conn = sqlite3.connect(path)
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                scraped_at TEXT NOT NULL
            )"""
        )
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_prices_name ON prices(name, id)")

    def save(self, products, when=None):
        when = when or datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.conn.executemany(
            "INSERT INTO prices (name, price, scraped_at) VALUES (?, ?, ?)",
            [(p["name"], p["price"], when) for p in products],
        )
        self.conn.commit()

    def latest_changes(self):
        """Bandingkan dua harga terakhir tiap produk. Mengembalikan list dict."""
        rows = self.conn.execute(
            """SELECT name, price, scraped_at FROM prices ORDER BY name, id DESC"""
        ).fetchall()
        grouped = {}
        for name, price, at in rows:
            grouped.setdefault(name, []).append((price, at))
        result = []
        for name, history in sorted(grouped.items()):
            current = history[0][0]
            previous = history[1][0] if len(history) > 1 else None
            change = None
            if previous:
                change = round((current - previous) / previous * 100, 2)
            result.append({"name": name, "current": current, "previous": previous, "change_pct": change})
        return result

    def close(self):
        self.conn.close()
