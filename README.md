# AI News — API

Tarama → doğrulama → sınıflandırma pipeline'ı ile AI/teknoloji gelişmelerini
izleyen sistemin sadece API/backend kısmı. Web arayüzü yoktur; tüm işlevlere
HTTP API üzerinden erişilir.

## Çalıştırma

```bash
cp .env.example .env
# .env içini doldurun: POSTGRES_PASSWORD, ANTHROPIC_API_KEY, API_KEY vb.
docker compose up -d --build
```

Servisler:
- `postgres` — veritabanı
- `api` — FastAPI uygulaması, `http://localhost:8008`
- `scheduler` — otomatik tarama döngüsü

## API

Tüm uç noktalar ve kimlik doğrulama (`X-API-Key` header): [docs/api.md](docs/api.md).
İnteraktif şema: `http://localhost:8008/docs`.

## Yedekleme

```bash
./scripts/backup.sh
```
