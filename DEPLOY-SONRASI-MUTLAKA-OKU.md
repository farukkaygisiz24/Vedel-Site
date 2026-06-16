# DEPLOY SONRASI MUTLAKA OKU

## Fly.io'ya deploy ettikten sonra bu komutu çalıştır

```bash
fly secrets set PRICE_SHEET_URL="https://docs.google.com/spreadsheets/d/1p13kvy6wSne5sTlsVp_M5G_JU2pp1i7tDvImic11Nlk/export?format=csv"
```

Bu yapılmazsa `/api/prices` endpoint'i hata döner ve sitedeki fiyatlar yüklenmez.

---

## .env.local (local geliştirme için)

Projeyi lokalde çalıştırmak için `.env.local` dosyasına şunu ekle:

```
PRICE_SHEET_URL=https://docs.google.com/spreadsheets/d/1p13kvy6wSne5sTlsVp_M5G_JU2pp1i7tDvImic11Nlk/export?format=csv
```

> `.env.local` dosyası zaten oluşturuldu ve bu değer içinde tanımlı. Yeni bir ortama taşırsan tekrar oluşturman gerekir.
