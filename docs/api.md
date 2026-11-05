# API Kullanım Kılavuzu

Taban adres: `https://{API_DOMAIN}` (reverse proxy kurulumu: [self-hosting.md](self-hosting.md)).
Yerelde test için: `http://localhost:8008`.

İnteraktif şema: `GET /docs` (Swagger UI) ve `GET /openapi.json` — bu ikisi kimlik
doğrulama gerektirmez, sadece şemayı gösterir; "Try it out" ile gerçek çağrı
yapmak için yine `X-API-Key` gerekir.

## Kimlik doğrulama

`.env`'de `API_KEY` ayarlıysa her `/api/*` isteği şu başlığı taşımalıdır:

```
X-API-Key: <anahtar>
```

Eksik veya hatalı anahtar `401 {"detail": "Geçersiz veya eksik API anahtarı"}`
döner. `API_KEY` boşsa (yalnızca yerel geliştirme) doğrulama yapılmaz.

Anahtar üretimi:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Uç noktalar

### `GET /health`

Auth gerektirmez. Healthcheck/monitoring içindir. `{"status": "ok"}` döner.

### `GET /api/developments`

Gelişme listesini filtreli döner. Query parametreleri (hepsi opsiyonel):

| Parametre | Tip | Açıklama |
|---|---|---|
| `q` | string | Metin arama (başlık/özet, TR+EN) |
| `sector` | string | Sektör etiketine göre filtre |
| `source_type` | string | `academic`, `company`, `media`, `defense`, `social` |
| `min_priority` | int | Minimum öncelik skoru (0-100) |
| `show_unverified` | bool | Doğrulanmamışları da göster |
| `sort` | string | `priority` (varsayılan), `recent`, `relevance` |
| `period` | string | `today`, `week`, `all` (varsayılan) |

Yanıt: `weekly_digest`, `scan_status`, `developments[]`, `search`, `all_sectors`,
`source_type_counts`, `total_count`, `verified_count`, `pending_count`,
`last_fetched_at` alanlarını içeren bir obje. Her `developments[]` öğesi: skorlar
(`technical_impact_score`, `hype_score`, `applicability_score`, `priority_score`),
`sector_tags`, Türkçe başlık/özet (`title_tr`, `summary_tr`) ve kaynak bilgisini
taşıyan `raw_item` alt objesi.

### `GET /api/developments/{id}/preview`

Bağlantı önizlemesi (görsel, başlık, özet). 404 döner: `id` yoksa.

### `POST /api/developments/{id}/chat`

Body: `{"question": "...", "history": [{"role": "user"|"assistant", "content": "..."}], "llm_provider": "anthropic"|"gemini", "llm_api_key": "...", "llm_model": "..."}`.
Üçü de opsiyoneldir; verilmezse sunucudaki varsayılan (`.env`'deki `LLM_PROVIDER` ve ona ait anahtar/model) kullanılır. Verilirse bu istek için geçersiz kılar — örn. `llm_provider: "gemini"` ile farklı bir sağlayıcı/anahtar/model ile çağrı yapılabilir.
Yanıt: `{"answer": "..."}`.

### `POST /api/refresh`

Manuel tarama tetikler. `202` (`{"started": true, "scan": {...}}`), tarama zaten
sürüyorsa `409`, tarama altyapısı başlatılamazsa `503`.

### `GET /api/scan-status`

Otomatik tarama durumu: `enabled`, `hours`, `timezone`, `interval_minutes`,
`scheduler_online`, `next_run_at`, `last_scan`, `last_successful_at`.

### Ayarlar

- `GET /api/settings` — tarama ayarları + kaynak listesi.
- `PUT /api/settings/scan` — body: `interval_minutes`, `auto_scan_enabled`, `program` (hepsi opsiyonel). Geçersiz aralık: `400`.
- `PUT /api/settings/sources/{source_name}` — body: `{"enabled": true|false}`. Bilinmeyen kaynak: `404`.
- `POST /api/settings/sources/custom` (`201`) — body: `name`, `feed_url`, `source_type`. Geçersiz URL/tür: `400`; isim çakışması: `409`.
- `DELETE /api/settings/sources/custom/{id}` — bulunamazsa `404`.

## Hata biçimi

Tüm hatalar `{"detail": "..."}` gövdesiyle standart HTTP durum koduyla döner
(`400`, `401`, `404`, `409`, `503`).

## Sınırlamalar

- Rate limiting yok; istemci taraflı makul bir çağrı sıklığı önerilir.
- Sürümleme yok; kırıcı değişiklikler önceden haber verilir.
- Tek kiracılı mimari: bir API anahtarı tüm veriye erişir, kullanıcı/müşteri bazlı ayrım yoktur.
