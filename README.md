# Rapid Quiz — Backend API

Kayıt gerektirmeyen, soru başına 5 saniyelik hızlı quiz uygulamasının REST API'si.
Django 5 + DRF + PostgreSQL 16. Tek referans kaynak: [docs/rapid-quiz-proje-dokumani.md](docs/rapid-quiz-proje-dokumani.md).

Frontend (Vue 3) ayrı repodadır: `../RapidQuizFrontend`.

## Hızlı başlangıç (önerilen: DB Docker'da, Django venv'de)

```bash
cp .env.example .env              # SECRET_KEY'i değiştir
docker compose up -d db           # PostgreSQL 16
python -m venv .venv
.venv/Scripts/activate            # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py seed_questions   # 5 kategori × 20 soru
python manage.py createsuperuser
python manage.py runserver
```

| Adres | İçerik |
|---|---|
| http://localhost:8000/api/v1/ | API |
| http://localhost:8000/api/docs/ | Swagger UI |
| http://localhost:8000/admin/ | Soru / kategori yönetimi |

> 5432 portu başka bir PostgreSQL tarafından kullanılıyorsa `.env` içinde
> `DB_HOST_PORT=5433` yap ve `DATABASE_URL`'deki portu da 5433 olarak değiştir.

Tamamen Docker ile çalıştırmak için: `docker compose up --build`, ardından
`docker compose exec api python manage.py migrate` ve `seed_questions`.

## Komutlar

| Komut | Açıklama |
|---|---|
| `pytest` | Testler (PostgreSQL gerekir; `--cov` ile kapsam) |
| `ruff check . && ruff format .` | Lint + format |
| `python manage.py seed_questions` | Soru havuzunu `apps/catalog/fixtures/questions/*.json`'dan yükler (idempotent) |
| `python manage.py cleanup_stale_sessions` | Süresi geçmiş oturumları `abandoned` yapar (günde bir kez) |
| `python manage.py spectacular --validate --file openapi.yaml` | OpenAPI şemasını üretir |
| `pip-compile --strip-extras -o requirements.txt pyproject.toml` | Sabitlenmiş bağımlılıkları yeniler (`--extra dev -o requirements-dev.txt` geliştirme için) |

`openapi.yaml` repoda tutulur; API değiştiğinde yeniden üretilip commit edilmelidir
(CI eski kalmışsa başarısız olur). Frontend TypeScript tiplerini bu dosyadan üretir.

## Ortam değişkenleri

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `DJANGO_SETTINGS_MODULE` | `config.settings.local` | `local`, `test`, `production` |
| `SECRET_KEY` | — (zorunlu) | |
| `DATABASE_URL` | — (zorunlu) | `postgres://user:pass@host:port/db` |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173` | Frontend origin'leri |
| `REDIS_URL` | boş | Varsa cache/throttle Redis'te, yoksa LocMem |
| `QUIZ_QUESTIONS_PER_SESSION` | `20` | |
| `QUIZ_TIME_LIMIT_MS` | `5000` | Soru başına süre |
| `QUIZ_GRACE_PERIOD_MS` | `800` | Ağ toleransı |
| `QUIZ_SESSION_TTL_MINUTES` | `30` | |
| `QUIZ_BASE_POINTS` / `QUIZ_MAX_SPEED_BONUS` | `100` / `100` | Puanlama |
| `LEADERBOARD_TOP_N` | `10` | |
| `THROTTLE_SESSION_CREATE` / `_ANSWER` / `_SCORE_SUBMIT` / `_ANON_READ` | `30/hour` / `600/hour` / `20/hour` / `300/hour` | IP bazlı limitler |
| `IPWARE_META_PRECEDENCE_ORDER` | local: `REMOTE_ADDR`; prod: `HTTP_DO_CONNECTING_IP,HTTP_X_FORWARDED_FOR,REMOTE_ADDR` | Gerçek istemci IP'si |
| `DB_SSLMODE`, `SECURE_SSL_REDIRECT` | `require`, `True` | Yalnızca production |

## API özeti

| Metot | Yol | Auth | Amaç |
|---|---|---|---|
| GET | `/api/v1/categories/` | — | Kategori listesi |
| POST | `/api/v1/quiz-sessions/` | — | Oturum başlat + ilk soru |
| GET | `/api/v1/quiz-sessions/{id}/current-question/` | Token | Kaldığı yerden devam |
| POST | `/api/v1/quiz-sessions/{id}/answers/` | Token | Cevapla + sonraki soru |
| GET | `/api/v1/quiz-sessions/{id}/summary/` | Token | Oturum özeti |
| POST | `/api/v1/quiz-sessions/{id}/submit-score/` | Token | Skoru kaydet |
| GET | `/api/v1/leaderboard/` | — | Top N skor |
| GET | `/api/v1/health/` | — | Sağlık kontrolü |

Token, oturum oluşturulurken dönen `session.token` değeridir ve `X-Session-Token`
başlığıyla gönderilir. Tüm hatalar `{"error": {"code", "message", "details"}}` zarfındadır.

## Yapı

```
config/             Django ayarları (base / local / test / production), URL'ler
apps/catalog/       Category, Question, AnswerOption · admin · seed_questions
apps/quiz/          QuizSession, QuizSessionQuestion · services.py (tüm oyun mantığı)
apps/leaderboard/   LeaderboardEntry · sıralama servisi
common/             hata zarfı, throttle, IP çözümleme, takma ad doğrulama
tests/              pytest
```
