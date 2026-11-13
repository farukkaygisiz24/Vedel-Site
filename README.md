# Vedel Servis

Vedel Klima operasyon portalı ve genel tanıtım sitesi.

| Yüzey | Teknoloji | Adres |
|---|---|---|
| Portal (satış, servis, stok, saha) | Django + Postgres | [servis.vedel.com.tr](https://servis.vedel.com.tr) |
| Tanıtım sitesi | Next.js | vedel.com.tr |

AI asistanları için: [AGENTS.md](AGENTS.md) → [CLAUDE.md](CLAUDE.md).

## Lokal portal

Docker gerekir.

```bash
docker compose up -d
# http://127.0.0.1:8000
```

Migrate / test:

```bash
docker compose exec backend python manage.py migrate --noinput
docker compose exec backend python manage.py test
```

Ortam değişkenleri: `backend/env.example`. Prod benzeri: `docker-compose.prod.yml` + kökte `.env`.

Prod iş verisini lokale çek (kullanıcılar dokunulmaz):

```bash
./scripts/pull-prod-biz.sh --load
```

## Lokal tanıtım sitesi

```bash
npm install
npm run dev
# http://localhost:3000
```

Fiyatlar için `.env.local` içinde `PRICE_SHEET_URL` (bkz. `DEPLOY-SONRASI-MUTLAKA-OKU.md`).

## Yapı

```
backend/          Django portal (accounts, sales, service, stock, crew)
src/              Next.js tanıtım sitesi
docker-compose.yml
.cursor/rules/    Cursor kuralları (ör. İngilizce URL path)
```

## Kurallar (kısa)

- Sayfa path’leri İngilizce kebab-case; arayüz metni Türkçe.
- Yeni / değişen URL: 3 seçenek öner, seçim bekle.
- Gizli dosyaları (`.env`, anahtarlar) commit etme.
- Commit / deploy yalnızca istendiğinde.
- İş bitmeden test: `manage.py test` + ilgili manuel smoke ([CLAUDE.md](CLAUDE.md) → Test phase).

## Lisans

Özel proje — Vedel Klima.
