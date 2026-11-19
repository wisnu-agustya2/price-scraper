"""Pembuat laporan CSV dari perubahan harga."""
import csv
import io


def changes_to_csv(changes):
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(["Produk", "Harga Sekarang", "Harga Sebelumnya", "Perubahan (%)"])
    for c in changes:
        writer.writerow([
            c["name"],
            c["current"],
            "" if c["previous"] is None else c["previous"],
            "" if c["change_pct"] is None else c["change_pct"],
        ])
    return out.getvalue()
