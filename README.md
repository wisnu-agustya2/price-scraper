# price-scraper

CLI Python untuk mengambil harga produk dari halaman HTML, menyimpan riwayatnya di SQLite, lalu membuat laporan perubahan harga dalam CSV. Hanya memakai library bawaan Python, tanpa `pip install`.

## Fitur
- Parser HTML dengan nama class CSS yang bisa diatur, termasuk elemen bersarang
- Normalisasi format harga (`Rp 1.250.000`, `$1,299.99`, `12,5`); produk tanpa harga valid dilewati
- Riwayat harga di SQLite, perubahan persen dihitung dari dua pengambilan terakhir
- Laporan CSV
- Sumber bisa URL atau file HTML lokal

## Menjalankan
Butuh Python 3.9 atau lebih baru.
```bash
git clone https://github.com/wisnu-agustya2/price-scraper.git
cd price-scraper
python3 -m price_scraper tests/fixtures/shop.html --db prices.db --csv laporan.csv
```

Contoh output:
```
3 produk disimpan.
- Headset Gaming: 1,300
- Laptop Pro 14: 15,499,000
- Mouse Wireless: 189,000
```
Jalankan lagi setelah harga berubah untuk melihat persentase perubahannya.

Untuk situs lain, sesuaikan nama class:
```bash
python3 -m price_scraper https://contoh.com/produk --item-class card --name-class title --price-class harga
```
Pastikan kamu mengikuti ketentuan layanan dan `robots.txt` situs yang di-scrape.

## Tes
```bash
python3 -m unittest discover -s tests -v
```

## Lisensi
MIT
