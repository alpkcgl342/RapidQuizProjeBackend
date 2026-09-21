# Rapid Quiz — Proje Dokümanı

> **Sürüm:** 1.0
> **Tarih:** 21 Eylül 2026
> **Durum:** Geliştirmeye hazır (implementation-ready)
> **Amaç:** Bu doküman, Claude Code ile geliştirilecek olan Rapid Quiz uygulamasının tek referans kaynağıdır. Ürün gereksinimleri, mimari kararlar, veri modeli, API sözleşmesi, UI tasarım sistemi ve görev listesi burada toplanmıştır.

---

## İçindekiler

1. [Proje Özeti](#1-proje-özeti)
2. [Kapsam](#2-kapsam)
3. [Kullanıcı Akışı ve Ekranlar](#3-kullanıcı-akışı-ve-ekranlar)
4. [Oyun Mekaniği ve Puanlama](#4-oyun-mekaniği-ve-puanlama)
5. [Sistem Mimarisi](#5-sistem-mimarisi)
6. [Veri Modeli](#6-veri-modeli)
7. [API Sözleşmesi](#7-api-sözleşmesi)
8. [Backend Detayları](#8-backend-detayları)
9. [Frontend Detayları](#9-frontend-detayları)
10. [UI Tasarım Sistemi](#10-ui-tasarım-sistemi)
11. [Mobil Uygulama Hazırlığı](#11-mobil-uygulama-hazırlığı)
12. [Örnek Seed Verisi](#12-örnek-seed-verisi)
13. [Test Stratejisi](#13-test-stratejisi)
14. [Ortamlar ve Deployment](#14-ortamlar-ve-deployment)
15. [Yol Haritası ve Görev Listesi](#15-yol-haritası-ve-görev-listesi)
16. [Kararlar ve Açık Konular](#16-kararlar-ve-açık-konular)

---

## 1. Proje Özeti

**Rapid Quiz**, kullanıcıların kayıt olmadan, seçtikleri kategoride hızlı bir bilgi yarışmasına katıldığı bir web (ve sonrasında mobil) uygulamasıdır.

Uygulamanın temel karakteri **hız**tır: her soru için kullanıcıya yalnızca **5 saniye** verilir. Süre dolduğunda soru otomatik olarak kaçırılmış sayılır ve bir sonraki soruya geçilir. Bu, uygulamayı klasik quiz uygulamalarından ayıran ve adını veren özelliktir.

### Tek cümlelik tanım

> Kayıt gerektirmeyen, 5 kategoride 20'şer soruluk, her soruya 5 saniye süre tanıyan, bitişte takma ad ile Top 10 skor tablosuna girilebilen hızlı quiz uygulaması.

### Temel prensipler

| Prensip | Açıklama |
|---|---|
| **Sürtünmesiz giriş** | Kayıt, giriş, e-posta doğrulama yok. Kullanıcı açar açmaz oynar. |
| **Sunucu otoritesi** | Süre, puan ve doğru cevap kontrolü sunucuda yapılır. İstemciye güvenilmez. |
| **Tek soru, tek ekran** | Kullanıcı bir soruyu cevaplamadan (veya süresi dolmadan) sonraki soruyu göremez ve yükleyemez. |
| **Mobil-hazır backend** | API baştan itibaren platformdan bağımsız JSON REST olarak tasarlanır; web ve mobil aynı sözleşmeyi kullanır. |
| **Canlı ve genç arayüz** | Koyu/ağır tema yerine aydınlık zemin üstünde yüksek doygunluklu renkler, yumuşak köşeler, hareketli geri bildirimler. |

### Kategoriler

| Slug | Görünen ad | Tema rengi | Soru sayısı |
|---|---|---|---|
| `yazilim` | Yazılım | `#6C4DFF` | 20 / oturum |
| `yapay-zeka` | Yapay Zekâ | `#00C2A8` | 20 / oturum |
| `bilgisayar-muhendisligi` | Bilgisayar Mühendisliği | `#2B8CFF` | 20 / oturum |
| `ulkeler` | Ülkeler | `#FF8A3D` | 20 / oturum |
| `fizik` | Fizik | `#FF5C8A` | 20 / oturum |

> **Not:** Her kategorinin havuzunda en az 20 soru olmak zorundadır. Havuz 20'den büyükse (önerilen: 60+) her oturumda rastgele 20 soru seçilir, böylece tekrar oynanabilirlik artar. Faz 1 için kategori başına **minimum 20, hedef 40** soru girilir.

---

## 2. Kapsam

### 2.1 Kapsam içi (v1.0)

- Kategori seçim ekranı (5 kategori)
- Kategori başına 20 soruluk oturum, her soru ayrı ekranda
- Soru başına 5 saniyelik geri sayım (sunucu doğrulamalı)
- Çoktan seçmeli sorular (4 şık, tek doğru)
- Anlık cevap geri bildirimi (doğru/yanlış + doğru şıkkın gösterilmesi)
- Oturum sonu skor ekranı (doğru/yanlış/kaçırılan dağılımı, toplam puan)
- Takma ad (nickname) girişi ve skor tablosuna kaydetme
- Kategori bazlı ve genel **Top 10** skor tablosu
- Responsive web arayüzü (mobil tarayıcı öncelikli)
- OpenAPI şeması ile belgelenmiş, mobil istemcinin de kullanabileceği REST API
- Django admin üzerinden soru/kategori yönetimi

### 2.2 Kapsam dışı (v1.0)

- Kullanıcı kaydı, giriş, profil, şifre yönetimi
- Sosyal giriş (Google, Apple vb.)
- Çok oyunculu / gerçek zamanlı düello modu
- Arkadaş listesi, bildirim, mesajlaşma
- Ödeme, reklam, premium içerik
- Kullanıcı tarafından soru ekleme / moderasyon akışı
- Çoklu dil (altyapı hazırlanır, v1.0'da yalnızca Türkçe yayınlanır)

### 2.3 Sonraki fazlar (planlanan)

| Faz | İçerik |
|---|---|
| v1.1 | Mobil uygulama (React Native veya Flutter — karar bekliyor), aynı API |
| v1.2 | Zorluk seviyeleri, günlük seri (streak), rozet sistemi |
| v1.3 | Skor paylaşımı (görsel kart üretimi), haftalık sıralama |

---

## 3. Kullanıcı Akışı ve Ekranlar

### 3.1 Akış şeması

```
[1] Ana Ekran (Kategori Seçimi)
        │  kategori seçildi
        ▼
[2] Geri Sayım / Hazırlık Ekranı  (3-2-1-Başla, ~2.5 sn)
        │
        ▼
[3] Soru Ekranı  ──(cevap verildi veya 5 sn doldu)──┐
        ▲                                            │
        │                                            ▼
        │                                   [4] Cevap Geri Bildirimi
        │                                       (~1.2 sn, otomatik)
        └──────── soru < 20 ise sonraki soru ────────┘
                                                     │ 20. soru bitti
                                                     ▼
                                            [5] Sonuç Ekranı
                                                     │ "Skoru kaydet"
                                                     ▼
                                            [6] Takma Ad Girişi
                                                     │
                                                     ▼
                                            [7] Skor Tablosu (Top 10)
                                                     │
                                       ┌─────────────┴─────────────┐
                                       ▼                           ▼
                              "Tekrar oyna" → [1]        "Ana sayfa" → [1]
```

### 3.2 Ekran detayları

#### [1] Ana Ekran — Kategori Seçimi

- Uygulama logosu ve "5 saniyede bir soru" alt başlığı
- 5 kategori kartı (grid; mobilde 2 sütun, masaüstünde 3 sütun)
- Her kartta: kategori ikonu, adı, kendi tema rengiyle gradyan arka plan, soru sayısı rozeti (`20 soru`)
- Alt kısımda "Skor Tablosu" butonu (oynamadan da skorlara bakılabilir)
- Kart tıklanınca hafif ölçek animasyonu, ardından [2]'ye geçiş

#### [2] Geri Sayım / Hazırlık Ekranı

- Seçilen kategorinin rengiyle dolu tam ekran
- Büyük "3 → 2 → 1 → BAŞLA!" animasyonu (toplam ~2.5 sn)
- Bu sırada arka planda `POST /quiz-sessions/` çağrısı yapılır ve ilk soru önden yüklenir
- Amaç: ağ gecikmesini kullanıcıya hissettirmeden ilk sorunun 0. milisaniyesinde hazır olmasını sağlamak

#### [3] Soru Ekranı

Bileşenler:

- **Üst bar:** `Soru 7 / 20` göstergesi, anlık puan, çıkış (X) butonu
- **Geri sayım halkası:** 5 saniyeden 0'a inen dairesel progress. Renk geçişi: yeşil (`5.0–3.0s`) → amber (`3.0–1.5s`) → kırmızı (`1.5–0s`). Son 2 saniyede hafif nabız (pulse) animasyonu
- **Soru metni:** büyük, en fazla 2-3 satır
- **4 şık:** dikey liste, büyük dokunma alanı (min. 56px yükseklik), A/B/C/D harf rozeti
- **Davranış:**
  - Şıkka tıklanınca tüm şıklar anında kilitlenir (çift tıklama engellenir), geri sayım durur
  - Süre dolarsa istemci otomatik olarak "cevapsız" (timeout) gönderir
  - Tarayıcı geri tuşu engellenir; sekme değiştirme sayaç durdurmaz (sunucu zamanı esastır)

#### [4] Cevap Geri Bildirimi

- Seçilen şık doğruysa yeşile döner + onay ikonu + konfeti mikro-animasyonu
- Yanlışsa seçilen şık kırmızıya, doğru şık yeşile döner
- Süre dolduysa "Süre doldu!" uyarısı + doğru şık yeşile döner
- Kazanılan puan `+135` şeklinde yukarı doğru kayan rozet olarak gösterilir
- ~1.2 saniye sonra otomatik olarak sonraki soruya geçilir (kullanıcı aksiyonu gerekmez)

#### [5] Sonuç Ekranı

- Büyük toplam puan (sayaç animasyonuyla 0'dan yukarı sayar)
- Dağılım: `Doğru: 14` / `Yanlış: 4` / `Kaçırılan: 2`
- Doğruluk yüzdesi ve ortalama cevap süresi (`1.8 sn`)
- Performansa göre motive edici başlık ("Fena değil!", "Şimşek gibisin!" vb.)
- Birincil buton: **Skoru Kaydet** → [6]
- İkincil butonlar: **Tekrar Oyna**, **Skor Tablosu**

#### [6] Takma Ad Girişi

- Tek input: "Takma adın ne?" (2–20 karakter)
- Doğrulama: boş olamaz, uzunluk/karakter kuralları (§7.8), aynı isim birden çok kez kullanılabilir (benzersizlik aranmaz). Küfür filtresi v1.0'da **yoktur**; uygunsuz kayıtlar admin'den silinir
- Kaydettikten sonra [7]'ye geçilir ve kullanıcının kendi satırı vurgulanır
- "Kaydetmeden geç" bağlantısı: skor kaydedilmez, doğrudan [7]'ye gider

#### [7] Skor Tablosu

- Sekmeler: `Genel` + 5 kategori
- Her sekmede Top 10 liste: sıra, takma ad, puan, kategori rozeti, tarih
- İlk 3 sıra altın/gümüş/bronz vurgulu
- Kullanıcı az önce skor kaydettiyse kendi satırı parlar; ilk 10'a giremediyse listenin altında ayrı bir satırda `Sen — 47. sıra — 1.840 puan` şeklinde gösterilir
- Butonlar: **Tekrar Oyna**, **Ana Sayfa**

---

## 4. Oyun Mekaniği ve Puanlama

### 4.1 5 saniye kuralı

Süre yönetimi **sunucu otoriteli**dir. İstemcideki geri sayım yalnızca görseldir.

1. Sunucu bir soruyu istemciye gönderdiğinde `served_at` zaman damgasını veritabanına yazar ve cevabın kabul edileceği son anı (`deadline = served_at + 5s + grace`) belirler.
2. İstemci cevabı gönderdiğinde sunucu `answered_at - served_at` farkını hesaplar.
3. Fark `5800 ms`'yi (5000 ms limit + 800 ms tolerans) aşıyorsa cevap içeriğine bakılmaksızın **`timeout`** sayılır ve 0 puan verilir.
4. **Ağ toleransı (grace period): 800 ms.** Yani sunucuya 5800 ms'ye kadar ulaşan cevaplar değerlendirilir, ancak puan hesabında süre `clamped_elapsed_ms = min(elapsed_ms, 5000)` olarak kırpılır. Bu, yavaş bağlantıdaki kullanıcının haksız yere ceza almasını önler ama avantaj da sağlamaz: 5000 ms'yi geçen bir doğru cevap hız bonusu alamaz, yalnızca 100 taban puanı alır.
5. İstemci, kendi sayacı 5 saniyeyi geçtiğinde otomatik olarak `selected_option_id: null` ile istek atar (kullanıcı ekranı kapatmadıysa).
6. Kullanıcı sekmeyi kapatır/uygulamadan çıkarsa cevap hiç gelmez. Bu durumda oturum "abandoned" kalır; bir sonraki soru talebinde veya `finish` çağrısında cevaplanmamış sorular otomatik `timeout` olarak işaretlenir.

### 4.2 Puanlama formülü

```
Doğru cevap için:
  base_points  = 100
  speed_bonus  = round(100 * (5000 - clamped_elapsed_ms) / 5000)
  points       = base_points + speed_bonus        →  100 ile 200 arasında

Yanlış cevap için:
  points = 0

Süre dolduysa (timeout):
  points = 0

Oturum toplamı:
  total_score = Σ points                          →  0 ile 4000 arasında
```

**Örnekler:**

| Senaryo | Geçen süre | Puan |
|---|---|---|
| Doğru, anında (0.4 sn) | 400 ms | 100 + 92 = **192** |
| Doğru, orta (2.5 sn) | 2500 ms | 100 + 50 = **150** |
| Doğru, son anda (4.9 sn) | 4900 ms | 100 + 2 = **102** |
| Yanlış | 1200 ms | **0** |
| Cevapsız | 5000+ ms | **0** |

> **Tasarım gerekçesi:** Hız bonusunun doğrusal olması hem açıklanabilir hem de "hızlı ol" mesajını net verir. Doğru cevabın tabanı (100) her zaman hız bonusundan büyük veya eşit tutulur ki doğruluk hızdan daha değerli kalsın.

### 4.3 Soru seçimi

- Oturum başlarken ilgili kategorinin `is_active=true` soruları arasından **rastgele 20 tane** seçilir.
- Seçim oturum başlangıcında **tek seferde** yapılır ve `QuizSessionQuestion` tablosuna sıralı olarak yazılır. Böylece kullanıcı yenilerse/geri gelirse aynı soru setiyle devam eder.
- Bir oturum içinde aynı soru tekrar etmez.
- Havuzda 20'den az aktif soru varsa API `422 INSUFFICIENT_QUESTIONS` döner (bu bir geliştirme/veri hatasıdır, kullanıcıya "Bu kategori şu an hazırlanıyor" mesajı gösterilir).

### 4.4 Kopya ve suistimal önlemleri

| Risk | Önlem |
|---|---|
| Doğru cevabın istemcide görünmesi | `is_correct` alanı soru gönderilirken **asla** serialize edilmez. Doğru şık yalnızca cevap verildikten sonra dönen yanıtta yer alır. |
| Soruları toplu çekip önceden çalışma | Oturum API'si her seferinde yalnızca **sıradaki tek soruyu** döner. Toplu soru listesi endpoint'i yoktur. |
| İstemci saatiyle oynama | Süre farkı yalnızca sunucu saatiyle hesaplanır; istemciden gelen süre bilgisi kabul edilmez. |
| Aynı soruya birden çok cevap | `QuizSessionQuestion.answered_at` doluysa ikinci cevap `409 ALREADY_ANSWERED` ile reddedilir. |
| Oturum token'ını tahmin etme | Oturum token'ı 32 byte'lık kriptografik rastgele değerdir (`secrets.token_urlsafe(32)`). |
| Skor tablosunu doğrudan besleme | Skor tablosuna yazma yalnızca `finish` edilmiş bir oturumun token'ıyla ve **bir kez** yapılabilir. Puan istemciden alınmaz, sunucudaki oturum kaydından okunur. |
| Bot ile toplu oturum açma | IP bazlı throttling: oturum oluşturma 30/saat, cevap gönderme 600/saat, skor kaydetme 20/saat. |
| Uygunsuz takma ad | Sunucu tarafında kelime listesi filtresi + uzunluk/karakter doğrulaması. |

---

## 5. Sistem Mimarisi

### 5.1 Genel görünüm

```
┌──────────────────┐        ┌──────────────────┐
│   Web Frontend   │        │  Mobil Uygulama  │
│   (Vue 3 + Vite) │        │   (v1.1, TBD)    │
└─────────┬────────┘        └─────────┬────────┘
          │                            │
          │      HTTPS / JSON REST     │
          │      X-Session-Token       │
          └────────────┬───────────────┘
                       ▼
          ┌────────────────────────────┐
          │   Backend API              │
          │   Django 5 + DRF           │
          │   ├── api/v1/              │
          │   ├── OpenAPI (spectacular)│
          │   └── Django Admin         │
          └────────────┬───────────────┘
                       ▼
          ┌────────────────────────────┐
          │   PostgreSQL 16            │
          └────────────────────────────┘
          ┌────────────────────────────┐
          │   Redis (opsiyonel)        │
          │   cache + throttle sayaçları│
          └────────────────────────────┘
```

### 5.2 Repo yapısı

İki ayrı repo kullanılacaktır (mobil için ileride üçüncüsü eklenecek):

| Repo | İsim önerisi | İçerik |
|---|---|---|
| Backend | `rapid-quiz-api` | Django projesi, DRF, migration'lar, seed komutları, OpenAPI şeması |
| Frontend | `rapid-quiz-web` | Vue 3 SPA, Vite, Pinia, tasarım sistemi |
| Mobil (v1.1) | `rapid-quiz-mobile` | Aynı API'yi tüketen mobil istemci |

**API sözleşmesinin paylaşımı:** Backend repo'su `openapi.yaml` dosyasını CI'da üretip repo köküne commit eder. Frontend repo'su bu dosyadan TypeScript tiplerini üretir (`openapi-typescript`). Böylece sözleşme değişiklikleri derleme zamanında yakalanır.

### 5.3 Teknoloji yığını

**Backend**

| Katman | Seçim | Not |
|---|---|---|
| Dil | Python 3.12+ | |
| Framework | Django 5.x | |
| API | Django REST Framework 3.15+ | |
| Veritabanı | PostgreSQL 16 | |
| ORM | Django ORM | |
| API dokümantasyonu | drf-spectacular | OpenAPI 3.1 şeması + Swagger UI |
| Ayarlar | django-environ | `.env` tabanlı yapılandırma |
| CORS | django-cors-headers | |
| Cache / throttle | Redis (prod), LocMem (dev) | |
| Test | pytest + pytest-django + factory_boy | |
| Kod kalitesi | ruff (lint + format), mypy (opsiyonel) | |
| Sunucu | gunicorn + whitenoise | |

**Frontend**

| Katman | Seçim | Not |
|---|---|---|
| Framework | Vue 3 (Composition API, `<script setup>`) | |
| Dil | TypeScript | |
| Build | Vite 5+ | |
| Router | Vue Router 4 | |
| State | Pinia | |
| HTTP | Axios (interceptor ile token ve hata yönetimi) | |
| Stil | CSS değişkenleri + scoped CSS (veya Tailwind — bkz. §16) | |
| Animasyon | CSS transitions + `@vueuse/motion` (opsiyonel) | |
| Test | Vitest + Vue Test Utils, Playwright (E2E) | |
| Kod kalitesi | ESLint + Prettier | |

### 5.4 Klasör yapıları

**`rapid-quiz-api`**

```
rapid-quiz-api/
├── config/                      # Django proje ayarları
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py / asgi.py
├── apps/
│   ├── catalog/                 # Kategori ve sorular
│   │   ├── models.py            # Category, Question, AnswerOption
│   │   ├── admin.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── management/commands/seed_questions.py
│   │   └── fixtures/questions/*.json
│   ├── quiz/                    # Oturum ve cevap akışı
│   │   ├── models.py            # QuizSession, QuizSessionQuestion
│   │   ├── services.py          # İş mantığı (puanlama, süre kontrolü)
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── authentication.py    # SessionTokenAuthentication
│   │   └── management/commands/cleanup_stale_sessions.py
│   └── leaderboard/
│       ├── models.py            # LeaderboardEntry
│       ├── services.py          # Sıralama, skor kaydı
│       ├── serializers.py
│       └── views.py
├── common/
│   ├── exceptions.py            # Standart hata zarfı
│   ├── throttles.py             # IP bazlı throttle sınıfları
│   ├── ip.py                    # django-ipware ile istemci IP'si
│   └── nickname.py              # Takma ad doğrulama (uzunluk/karakter)
├── tests/
├── .do/
│   └── app.yaml                 # DigitalOcean App Platform spec (versiyonlanır)
├── .github/workflows/ci.yml
├── openapi.yaml                 # CI tarafından üretilir
├── pyproject.toml
├── requirements.txt             # Dockerfile bunu kullanır (pip-compile ile üretilir)
├── Dockerfile                   # DO App Platform bunu derler
├── .dockerignore
├── docker-compose.yml           # yalnızca yerel geliştirme
├── .env.example
└── README.md
```

**`rapid-quiz-web`**

```
rapid-quiz-web/
├── src/
│   ├── api/
│   │   ├── client.ts            # Axios instance + interceptor
│   │   ├── quiz.ts              # Oturum endpoint'leri
│   │   ├── catalog.ts
│   │   ├── leaderboard.ts
│   │   └── types.gen.ts         # openapi.yaml'dan üretilen tipler
│   ├── assets/
│   │   └── styles/
│   │       ├── tokens.css       # Tasarım tokenları (renk, spacing, radius)
│   │       ├── base.css
│   │       └── animations.css
│   ├── components/
│   │   ├── base/                # BaseButton, BaseCard, BaseModal...
│   │   ├── quiz/                # CountdownRing, QuestionCard, OptionButton,
│   │   │                        # ProgressBar, ScorePopup, FeedbackOverlay
│   │   └── leaderboard/         # LeaderboardTable, LeaderboardRow, TabBar
│   ├── composables/
│   │   ├── useCountdown.ts      # requestAnimationFrame tabanlı sayaç
│   │   └── useQuizSession.ts
│   ├── stores/
│   │   ├── quiz.ts              # Pinia: oturum durum makinesi
│   │   └── leaderboard.ts
│   ├── views/
│   │   ├── HomeView.vue
│   │   ├── CountdownView.vue
│   │   ├── QuizView.vue
│   │   ├── ResultView.vue
│   │   ├── NicknameView.vue
│   │   └── LeaderboardView.vue
│   ├── router/index.ts
│   ├── App.vue
│   └── main.ts
├── public/
├── tests/
│   ├── unit/
│   └── e2e/
├── .do/
│   └── app.yaml                 # DigitalOcean Static Site spec
├── .github/workflows/ci.yml
├── .env.example
├── vite.config.ts
├── tsconfig.json
└── README.md
```

---

## 6. Veri Modeli

### 6.1 ER diyagramı

```
Category 1 ────< Question 1 ────< AnswerOption
    │                  │
    │                  │
    │ 1                │ 1
    │                  │
    ▼                  ▼
QuizSession 1 ────< QuizSessionQuestion
    │
    │ 1
    ▼
LeaderboardEntry (0..1)
```

### 6.2 Tablolar

#### `catalog_category`

| Alan | Tip | Kısıt | Açıklama |
|---|---|---|---|
| `id` | BigAutoField | PK | |
| `slug` | SlugField(50) | unique, index | `yazilim`, `fizik` … |
| `name` | CharField(80) | | Görünen ad (TR) |
| `description` | CharField(200) | blank | Kart altında kısa açıklama |
| `color_hex` | CharField(7) | | `#6C4DFF` |
| `icon` | CharField(40) | | İkon anahtarı (`code`, `brain`, `chip`, `globe`, `atom`) |
| `display_order` | PositiveSmallIntegerField | default 0 | Sıralama |
| `is_active` | BooleanField | default True | |
| `created_at` / `updated_at` | DateTimeField | auto | |

#### `catalog_question`

| Alan | Tip | Kısıt | Açıklama |
|---|---|---|---|
| `id` | BigAutoField | PK | |
| `category_id` | FK → Category | on_delete=PROTECT, index | |
| `external_ref` | CharField(40) | unique, null | Seed fixture kimliği (`yazilim-001`). API'de **dönülmez**, yalnızca idempotent seed için |
| `text` | TextField | max 300 karakter (validator) | Soru metni |
| `explanation` | TextField | blank | Cevap sonrası gösterilebilecek kısa açıklama (v1.2) |
| `difficulty` | SmallIntegerField | choices 1..3, default 2 | 1=kolay, 2=orta, 3=zor (v1.2'de kullanılacak) |
| `is_active` | BooleanField | default True, index | |
| `times_served` | PositiveIntegerField | default 0 | İstatistik |
| `times_correct` | PositiveIntegerField | default 0 | İstatistik |
| `created_at` / `updated_at` | DateTimeField | auto | |

**Kısıtlar:** Bir sorunun tam olarak 4 şıkkı ve tam olarak 1 doğru şıkkı olmalıdır. Bu kural `Question.clean()` içinde ve `seed_questions` komutunda doğrulanır; ayrıca admin'de inline formset validasyonu ile zorlanır.

**İndeks:** `(category_id, is_active)` bileşik indeks — rastgele soru seçimi bu sorguyu kullanır.

#### `catalog_answeroption`

| Alan | Tip | Kısıt | Açıklama |
|---|---|---|---|
| `id` | BigAutoField | PK | |
| `question_id` | FK → Question | on_delete=CASCADE, index | |
| `text` | CharField(200) | | Şık metni |
| `is_correct` | BooleanField | default False | **API'de soru gönderilirken asla serialize edilmez** |
| `display_order` | PositiveSmallIntegerField | | 0..3 |

**Kısıt:** `UniqueConstraint(question, display_order)`. Doğru şık sayısı = 1 kuralı uygulama katmanında doğrulanır.

#### `quiz_quizsession`

| Alan | Tip | Kısıt | Açıklama |
|---|---|---|---|
| `id` | UUIDField | PK, default uuid4 | Dışarıya açılan kimlik |
| `token` | CharField(64) | unique, index | `secrets.token_urlsafe(32)`; `X-Session-Token` başlığında taşınır |
| `category_id` | FK → Category | PROTECT | |
| `status` | CharField(16) | choices, index | `in_progress`, `completed`, `abandoned` |
| `total_questions` | PositiveSmallIntegerField | default 20 | |
| `current_index` | PositiveSmallIntegerField | default 0 | Sıradaki sorunun 0-tabanlı indeksi |
| `score` | PositiveIntegerField | default 0 | Sunucu tarafından hesaplanır |
| `correct_count` | PositiveSmallIntegerField | default 0 | |
| `wrong_count` | PositiveSmallIntegerField | default 0 | |
| `timeout_count` | PositiveSmallIntegerField | default 0 | |
| `client_platform` | CharField(16) | `web`, `ios`, `android` | Analitik için |
| `client_version` | CharField(20) | blank | |
| `started_at` | DateTimeField | auto_now_add | |
| `finished_at` | DateTimeField | null | |
| `expires_at` | DateTimeField | index | `started_at + 30 dk`; sonrasında oturum `abandoned` |

#### `quiz_quizsessionquestion`

| Alan | Tip | Kısıt | Açıklama |
|---|---|---|---|
| `id` | BigAutoField | PK | |
| `session_id` | FK → QuizSession | CASCADE, index | |
| `question_id` | FK → Question | PROTECT | |
| `order` | PositiveSmallIntegerField | 0..19 | |
| `served_at` | DateTimeField | null | Soru istemciye ilk gönderildiği an |
| `answered_at` | DateTimeField | null | Cevabın sunucuya ulaştığı an |
| `selected_option_id` | FK → AnswerOption | null, SET_NULL | Null = cevapsız |
| `is_correct` | BooleanField | null | Null = henüz cevaplanmadı |
| `elapsed_ms` | PositiveIntegerField | null | `answered_at - served_at` |
| `points` | PositiveSmallIntegerField | default 0 | |
| `outcome` | CharField(10) | `pending`, `correct`, `wrong`, `timeout` | |

**Kısıtlar:** `UniqueConstraint(session, order)`, `UniqueConstraint(session, question)`.

#### `leaderboard_leaderboardentry`

| Alan | Tip | Kısıt | Açıklama |
|---|---|---|---|
| `id` | BigAutoField | PK | |
| `session_id` | OneToOne → QuizSession | CASCADE, unique | Bir oturum yalnızca bir kez skor tablosuna girebilir |
| `category_id` | FK → Category | PROTECT, index | Denormalize (sorgu hızı için) |
| `nickname` | CharField(20) | index | |
| `score` | PositiveIntegerField | index | Denormalize |
| `correct_count` | PositiveSmallIntegerField | | |
| `total_elapsed_ms` | PositiveIntegerField | | Beraberlik bozucu. Tüm soruların kırpılmış süreleri toplamı; `timeout` olan sorular `QUIZ_TIME_LIMIT_MS` (5000 ms) sayılır |
| `created_at` | DateTimeField | auto_now_add, index | |

**İndeksler:** `(category_id, -score, total_elapsed_ms)` — kategori Top 10 sorgusu; `(-score, total_elapsed_ms)` — genel (tüm kategoriler) Top 10 sorgusu.

**Sıralama kuralı:** Önce `score` azalan, eşitlik halinde `total_elapsed_ms` artan (daha hızlı bitiren üstte), o da eşitse `created_at` artan (önce kaydeden üstte).

---

## 7. API Sözleşmesi

### 7.1 Genel kurallar

| Konu | Karar |
|---|---|
| Base URL | `https://api.rapidquiz.app/api/v1/` |
| Format | JSON (UTF-8). İstek ve yanıt gövdeleri `application/json` |
| Sürümleme | URL yolunda (`/api/v1/`). Kırıcı değişiklikte `/api/v2/` açılır, v1 en az 6 ay yaşatılır |
| Kimlik doğrulama | Kullanıcı hesabı yok. Aktif oturum işlemleri `X-Session-Token: <token>` başlığıyla yetkilendirilir |
| Çerez / CSRF | API çerez kullanmaz, CSRF gerekmez (mobil uyumluluk için kritik) |
| Alan adlandırma | `snake_case` |
| Tarih formatı | ISO 8601, UTC, `Z` sonekli (`2026-09-21T14:30:05.123Z`) |
| Süre birimi | Milisaniye (`_ms` soneki) |
| Dil | `Accept-Language: tr` (v1.0'da yalnızca `tr`) |
| İstemci tanıtımı | `X-Client-Platform: web|ios|android`, `X-Client-Version: 1.0.0` |
| Sayfalama | Limit/offset. `?limit=10&offset=0`, varsayılan limit 10, maksimum 50 |

### 7.2 Standart hata zarfı

Tüm 4xx/5xx yanıtları aynı yapıdadır:

```json
{
  "error": {
    "code": "ALREADY_ANSWERED",
    "message": "Bu soru zaten cevaplandı.",
    "details": {
      "question_id": 1183,
      "expected_question_id": 1190
    }
  }
}
```

**Hata kodları:**

| HTTP | `code` | Ne zaman |
|---|---|---|
| 400 | `VALIDATION_ERROR` | Gövde doğrulaması başarısız (`details` alan bazlı hataları içerir) |
| 401 | `INVALID_SESSION_TOKEN` | Token yok, geçersiz veya süresi dolmuş |
| 403 | `SESSION_NOT_OWNED` | Token başka bir oturuma ait |
| 404 | `NOT_FOUND` | Kategori/oturum/soru bulunamadı |
| 409 | `ALREADY_ANSWERED` | Bu soru zaten cevaplandı |
| 409 | `SESSION_ALREADY_FINISHED` | Bitmiş oturuma cevap gönderildi |
| 409 | `SESSION_NOT_FINISHED` | Bitmemiş oturumun skoru kaydedilmeye / özeti alınmaya çalışıldı |
| 409 | `SCORE_ALREADY_SUBMITTED` | Bu oturumun skoru zaten kaydedildi |
| 410 | `SESSION_EXPIRED` | Oturum 30 dakikayı aştı |
| 422 | `INSUFFICIENT_QUESTIONS` | Kategoride 20 aktif soru yok |
| 429 | `RATE_LIMITED` | Throttle limiti aşıldı (`Retry-After` başlığı döner) |
| 500 | `INTERNAL_ERROR` | Beklenmeyen hata |

> **Not:** Süre dolması bir **hata değil, normal bir oyun sonucudur.** Grace period'u aşan cevaplar da dahil olmak üzere tüm zaman aşımları `200 OK` ile ve `outcome: "timeout"` alanıyla döner; hata zarfı kullanılmaz. Bkz. §7.6.

---

### 7.3 `GET /api/v1/categories/`

Kategori listesini döner. Kimlik doğrulama gerekmez.

**Yanıt `200`**

```json
{
  "results": [
    {
      "slug": "yazilim",
      "name": "Yazılım",
      "description": "Diller, algoritmalar, araçlar",
      "color_hex": "#6C4DFF",
      "icon": "code",
      "questions_per_session": 20,
      "available_question_count": 42,
      "is_playable": true
    },
    {
      "slug": "yapay-zeka",
      "name": "Yapay Zekâ",
      "description": "Makine öğrenmesi, modeller, kavramlar",
      "color_hex": "#00C2A8",
      "icon": "brain",
      "questions_per_session": 20,
      "available_question_count": 38,
      "is_playable": true
    }
  ]
}
```

`is_playable`, `available_question_count >= 20` olduğunda `true` döner. Frontend oynanamayan kategoriyi soluk gösterir ve tıklamayı engeller.

---

### 7.4 `POST /api/v1/quiz-sessions/`

Yeni bir quiz oturumu başlatır ve **ilk soruyu** döner.

**İstek**

```http
POST /api/v1/quiz-sessions/
Content-Type: application/json
X-Client-Platform: web
X-Client-Version: 1.0.0
```

```json
{
  "category": "yazilim"
}
```

**Yanıt `201`**

```json
{
  "session": {
    "id": "0b8b5a5e-31d1-4c2e-9a5d-8b4c7f2a1d90",
    "token": "8Kd3nQ7xR2vT5yU8iO1pA4sD6fG9hJ0kL3zX6cV9bN2m",
    "category": {
      "slug": "yazilim",
      "name": "Yazılım",
      "color_hex": "#6C4DFF"
    },
    "total_questions": 20,
    "current_index": 0,
    "score": 0,
    "status": "in_progress",
    "expires_at": "2026-09-21T15:00:05.000Z"
  },
  "question": {
    "id": 1183,
    "index": 0,
    "text": "Python'da bir listenin elemanlarını yerinde ters çeviren metot hangisidir?",
    "options": [
      { "id": 4721, "label": "A", "text": "reverse()" },
      { "id": 4722, "label": "B", "text": "reversed()" },
      { "id": 4723, "label": "C", "text": "sort(reverse=True)" },
      { "id": 4724, "label": "D", "text": "flip()" }
    ],
    "time_limit_ms": 5000,
    "served_at": "2026-09-21T14:30:05.000Z",
    "deadline_at": "2026-09-21T14:30:10.000Z"
  }
}
```

> **Önemli:** `options` dizisinde `is_correct` alanı **yoktur**. Şıkların sırası sunucuda her oturum için karıştırılır (shuffle), böylece "doğru cevap hep B" gibi örüntüler oluşmaz.

**Olası hatalar:** `404 NOT_FOUND` (kategori yok), `422 INSUFFICIENT_QUESTIONS`, `429 RATE_LIMITED`

---

### 7.5 `GET /api/v1/quiz-sessions/{id}/current-question/`

Sıradaki cevaplanmamış soruyu döner. Sayfa yenilenmesi / bağlantı koptuğunda kaldığı yerden devam için kullanılır.

**İstek**

```http
GET /api/v1/quiz-sessions/0b8b5a5e-.../current-question/
X-Session-Token: 8Kd3nQ7xR2vT5yU8iO1pA4sD6fG9hJ0kL3zX6cV9bN2m
```

**Yanıt `200`** — `POST /quiz-sessions/` yanıtındaki `question` nesnesiyle aynı şema.

**Davranış:** Soru daha önce servis edilmişse `served_at` **güncellenmez** — yani yenileyerek süre sıfırlanamaz. Eğer `now > deadline_at` ise sunucu bu soruyu otomatik `timeout` olarak kapatır, `current_index`'i ilerletir ve bir sonraki soruyu döner.

**Yanıt `200`** (oturum bittiyse):

```json
{
  "question": null,
  "session": { "status": "completed", "current_index": 20, "score": 2840 }
}
```

---

### 7.6 `POST /api/v1/quiz-sessions/{id}/answers/`

Sıradaki soruya cevap gönderir. **Bu uygulamanın en kritik endpoint'idir.**

**İstek**

```http
POST /api/v1/quiz-sessions/0b8b5a5e-.../answers/
Content-Type: application/json
X-Session-Token: 8Kd3nQ7xR2vT5yU8iO1pA4sD6fG9hJ0kL3zX6cV9bN2m
```

```json
{
  "question_id": 1183,
  "selected_option_id": 4721
}
```

`selected_option_id` **`null`** gönderilirse cevapsız (timeout) olarak işlenir. `question_id` zorunludur ve sunucudaki `current_index`'e karşılık gelen soruyla eşleşmelidir; eşleşmezse `409` döner (yarış durumu koruması).

**Yanıt `200`**

```json
{
  "result": {
    "outcome": "correct",
    "is_correct": true,
    "correct_option_id": 4721,
    "selected_option_id": 4721,
    "elapsed_ms": 1340,
    "points_earned": 173,
    "explanation": "reverse() listeyi yerinde ters çevirir; reversed() ise yeni bir iterator döner."
  },
  "session": {
    "current_index": 1,
    "score": 173,
    "correct_count": 1,
    "wrong_count": 0,
    "timeout_count": 0,
    "status": "in_progress"
  },
  "next_question": {
    "id": 1190,
    "index": 1,
    "text": "Git'te son commit'i geri almadan değişiklikleri geçici olarak saklayan komut hangisidir?",
    "options": [
      { "id": 4760, "label": "A", "text": "git stash" },
      { "id": 4761, "label": "B", "text": "git reset" },
      { "id": 4762, "label": "C", "text": "git revert" },
      { "id": 4763, "label": "D", "text": "git clean" }
    ],
    "time_limit_ms": 5000,
    "served_at": "2026-09-21T14:30:07.500Z",
    "deadline_at": "2026-09-21T14:30:12.500Z"
  }
}
```

**20. soru cevaplandığında** `next_question` `null` olur ve oturum otomatik olarak `completed` durumuna geçer; yanıta `summary` nesnesi eklenir (bkz. §7.7).

> **Kritik tasarım notu — `served_at` zamanlaması:**
> `next_question.served_at` değeri, yanıtın **üretildiği** andır. İstemcinin sayacı ise yanıtı **aldığı** anda başlar. Aradaki ağ gecikmesi kullanıcının aleyhine işlemesin diye 800 ms grace period uygulanır (§4.1). İstemci ayrıca `deadline_at` ile kendi saatini karşılaştırarak sayacını hizalar; saat sapması 2 saniyeden fazlaysa istemci `deadline_at` yerine kendi 5 saniyesini kullanır.

**Olası hatalar:**

| Durum | Yanıt |
|---|---|
| Süre 5800 ms'yi aştı | `200` + `outcome: "timeout"`, `points_earned: 0` |
| Bu soru zaten cevaplandı | `409 ALREADY_ANSWERED` |
| `question_id` sıradaki soru değil | `409 ALREADY_ANSWERED` (details içinde `expected_question_id`) |
| Oturum bitmiş | `409 SESSION_ALREADY_FINISHED` |
| Oturum 30 dk'yı aşmış | `410 SESSION_EXPIRED` |
| Token geçersiz | `401 INVALID_SESSION_TOKEN` |
| `selected_option_id` bu soruya ait değil | `400 VALIDATION_ERROR` |

---

### 7.7 `GET /api/v1/quiz-sessions/{id}/summary/`

Biten oturumun özetini döner. Sonuç ekranı bu veriyi kullanır. (Aynı `summary` nesnesi 20. cevabın yanıtına da gömülür, böylece ekstra istek gerekmez.)

**Yanıt `200`**

```json
{
  "session_id": "0b8b5a5e-31d1-4c2e-9a5d-8b4c7f2a1d90",
  "category": { "slug": "yazilim", "name": "Yazılım", "color_hex": "#6C4DFF" },
  "status": "completed",
  "score": 2840,
  "max_possible_score": 4000,
  "total_questions": 20,
  "correct_count": 16,
  "wrong_count": 3,
  "timeout_count": 1,
  "accuracy_pct": 80.0,
  "average_elapsed_ms": 1820,
  "fastest_correct_ms": 620,
  "total_elapsed_ms": 36400,
  "score_submitted": false,
  "estimated_rank": 12,
  "finished_at": "2026-09-21T14:33:41.000Z"
}
```

`estimated_rank`, bu skorun ilgili kategorideki tahmini sırasıdır (skor kaydedilse kaçıncı olurdu). Kullanıcıyı isim girmeye motive eder.

**Süre alanlarının hesabı (D15):**

- `total_elapsed_ms` = Σ `min(elapsed_ms, 5000)`; `timeout` sorular 5000 ms sayılır. Skor tablosunda beraberlik bozucudur.
- `average_elapsed_ms` = cevaplanan (doğru + yanlış) soruların ortalama kırpılmış süresi; hiç cevap yoksa `null`.
- `fastest_correct_ms` = en hızlı doğru cevap; doğru cevap yoksa `null`.

Oturum henüz `completed` değilse `409 SESSION_NOT_FINISHED` döner.

---

### 7.8 `POST /api/v1/quiz-sessions/{id}/submit-score/`

Biten oturumun skorunu takma adla skor tablosuna kaydeder.

**İstek**

```json
{ "nickname": "hizlisimsek" }
```

**Yanıt `201`**

```json
{
  "entry": {
    "id": 9021,
    "nickname": "hizlisimsek",
    "score": 2840,
    "category": { "slug": "yazilim", "name": "Yazılım" },
    "rank_in_category": 7,
    "rank_overall": 23,
    "created_at": "2026-09-21T14:34:02.000Z"
  },
  "leaderboard": {
    "scope": "category",
    "category": "yazilim",
    "top": [
      { "rank": 1, "nickname": "algoritmaci", "score": 3620, "created_at": "2026-09-19T10:11:00.000Z" },
      { "rank": 2, "nickname": "dev_ayse", "score": 3480, "created_at": "2026-09-20T18:42:00.000Z" }
    ],
    "user_entry_id": 9021
  }
}
```

Yanıt, güncel Top 10'u da içerir ki frontend ekstra istek atmadan skor tablosunu gösterebilsin. Kullanıcının satırı `user_entry_id` ile eşleştirilip vurgulanır.

**Doğrulama kuralları (nickname):**

- 2–20 karakter
- İzinli karakterler: Türkçe harfler, rakam, `_`, `-`, boşluk (ardışık boşluk kırpılır)
- Baş/son boşluklar kırpılır
- Küfür/uygunsuz kelime filtresi v1.0'da yoktur (karar: §16.1 D11)
- Benzersizlik **aranmaz** — aynı isim birden çok kez kullanılabilir

**Olası hatalar:** `400 VALIDATION_ERROR` (geçersiz takma ad), `409 SCORE_ALREADY_SUBMITTED`, `409 SESSION_NOT_FINISHED` (oturum henüz bitmemişse), `429 RATE_LIMITED`

---

### 7.9 `GET /api/v1/leaderboard/`

Skor tablosunu döner. Kimlik doğrulama gerekmez.

**Query parametreleri**

| Parametre | Tip | Varsayılan | Açıklama |
|---|---|---|---|
| `category` | string | — | Kategori slug'ı. Verilmezse tüm kategoriler birlikte (genel tablo) |
| `limit` | int | 10 | 1–50 |
| `offset` | int | 0 | |
| `period` | string | `all` | `all`, `month`, `week`, `today` (v1.0'da `all` yeterli, diğerleri hazır bırakılır) |

**Yanıt `200`**

```json
{
  "scope": "category",
  "category": { "slug": "fizik", "name": "Fizik", "color_hex": "#FF5C8A" },
  "period": "all",
  "count": 214,
  "results": [
    {
      "rank": 1,
      "nickname": "kuantumcu",
      "score": 3780,
      "correct_count": 20,
      "category": { "slug": "fizik", "name": "Fizik" },
      "created_at": "2026-09-18T09:20:00.000Z"
    }
  ]
}
```

Genel tabloda (`category` verilmediğinde) her satırda kategori bilgisi rozet olarak gösterilir.

---

### 7.10 `GET /api/v1/health/`

Basit sağlık kontrolü (deployment ve uptime izleme için).

```json
{ "status": "ok", "database": "ok", "version": "1.0.0", "time": "2026-09-21T14:34:02.000Z" }
```

---

### 7.11 Endpoint özeti

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
| GET | `/api/schema/` · `/api/docs/` | — | OpenAPI şeması ve Swagger UI |

---

## 8. Backend Detayları

### 8.1 Katman sorumlulukları

| Katman | Sorumluluk | Yapmaması gereken |
|---|---|---|
| **View (DRF)** | HTTP, doğrulama, yetkilendirme, serileştirme | İş mantığı, puan hesabı |
| **Serializer** | Girdi doğrulama ve çıktı şekillendirme | Veritabanı yazma |
| **Service (`services.py`)** | Tüm iş mantığı: oturum oluşturma, süre kontrolü, puanlama, ilerletme | HTTP'yi bilmek |
| **Model** | Veri yapısı, kısıtlar, basit `property`'ler | Karmaşık akış mantığı |

Tüm puanlama ve süre mantığı `apps/quiz/services.py` içinde toplanır ve doğrudan birim testi yazılabilir olmalıdır. Bu, mobil istemci eklendiğinde mantığın tek noktada kalmasını garanti eder.

### 8.2 Kimlik doğrulama

Özel bir DRF authentication sınıfı yazılır:

```python
class SessionTokenAuthentication(BaseAuthentication):
    """X-Session-Token başlığını QuizSession'a çözer.

    Django user'ı YOK; request.quiz_session set edilir.
    Süresi geçmiş veya bulunamayan token 401 döner.
    """
```

Oturum sahipliği kontrolü: URL'deki `{id}` ile token'dan çözülen oturumun `id`'si eşleşmelidir; eşleşmezse `403 SESSION_NOT_OWNED`.

### 8.3 Eşzamanlılık ve işlem güvenliği

Cevap gönderme akışı, çift gönderim ve yarış durumlarına karşı korunmalıdır:

```python
with transaction.atomic():
    sq = (QuizSessionQuestion.objects
          .select_for_update()
          .get(session_id=session_id, order=session.current_index))
    if sq.answered_at is not None:
        raise AlreadyAnswered()
    # ... süre hesabı, puanlama, current_index ilerletme
```

`select_for_update()` satır kilidi, aynı anda gelen iki cevabın ikisinin de işlenmesini engeller.

### 8.4 Zaman aşımı temizliği

- `expires_at` geçmiş `in_progress` oturumlar, `cleanup_stale_sessions` adlı bir yönetim komutuyla `abandoned` işaretlenir.
- Komut günde bir kez (cron / Celery beat / platform scheduler) çalıştırılır.
- v1.0 için Celery kurulmaz; basit bir cron + `manage.py` komutu yeterlidir.

### 8.5 Throttling

`settings` içinde DRF throttle sınıfları:

| Scope | Limit | Uygulandığı yer |
|---|---|---|
| `session_create` | 30/saat/IP | `POST /quiz-sessions/` |
| `answer` | 600/saat/IP | `POST .../answers/` |
| `score_submit` | 20/saat/IP | `POST .../submit-score/` |
| `anon_read` | 300/saat/IP | Kategori ve skor tablosu okumaları |

Prod'da sayaçlar Redis'te tutulur. Reverse proxy arkasında gerçek IP için `X-Forwarded-For` doğru şekilde okunmalıdır (`django-ipware` veya güvenilir proxy listesi).

### 8.6 CORS

```python
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS")
# örn. ["https://rapidquiz.app", "http://localhost:5173"]
CORS_ALLOW_HEADERS = [..., "x-session-token", "x-client-platform", "x-client-version"]
CORS_ALLOW_CREDENTIALS = False   # çerez kullanmıyoruz
```

Mobil istemciler CORS'a tabi değildir; yapılandırma yalnızca web'i ilgilendirir.

### 8.7 Django Admin

İçerik yönetimi tamamen admin üzerinden yapılır:

- **Category:** liste, sıralama, renk önizlemesi, aktif soru sayısı sütunu
- **Question:** `AnswerOption` inline (4 satır), kategori filtresi, metin araması, "tam 4 şık ve 1 doğru" formset validasyonu, `is_active` toplu aksiyonu
- **QuizSession:** salt okunur; filtreler (kategori, durum, tarih), oturum sorularını inline gösterme
- **LeaderboardEntry:** salt okunur + silme yetkisi (uygunsuz kaydı temizlemek için)

### 8.8 Ortam değişkenleri (`.env`)

```dotenv
DJANGO_SETTINGS_MODULE=config.settings.local
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DATABASE_URL=postgres://rapidquiz:rapidquiz@localhost:5432/rapidquiz

CORS_ALLOWED_ORIGINS=http://localhost:5173

REDIS_URL=redis://localhost:6379/0

QUIZ_QUESTIONS_PER_SESSION=20
QUIZ_TIME_LIMIT_MS=5000
QUIZ_GRACE_PERIOD_MS=800
QUIZ_SESSION_TTL_MINUTES=30
QUIZ_BASE_POINTS=100
QUIZ_MAX_SPEED_BONUS=100
LEADERBOARD_TOP_N=10
```

> Süre limiti, puan katsayıları ve soru sayısı **sabit kodlanmaz**; ayarlardan okunur. Böylece ileride "10 saniyelik rahat mod" gibi bir varyant eklemek kolaylaşır.

---

## 9. Frontend Detayları

### 9.1 Rota tanımları

| Yol | Görünüm | Koruma |
|---|---|---|
| `/` | `HomeView` | — |
| `/hazirlik/:category` | `CountdownView` | Geçerli kategori slug'ı |
| `/quiz/:sessionId` | `QuizView` | Store'da aktif oturum yoksa `/`'a yönlendir |
| `/sonuc/:sessionId` | `ResultView` | Oturum `completed` değilse `/quiz/:sessionId`'e yönlendir |
| `/isim/:sessionId` | `NicknameView` | Skor zaten kaydedildiyse `/skorlar`'a yönlendir |
| `/skorlar` | `LeaderboardView` | — |
| `/:pathMatch(.*)*` | `NotFoundView` | — |

**Navigasyon koruması:** `QuizView` içindeyken `onBeforeRouteLeave` ile "Çıkarsan skorun kaydedilmez, emin misin?" onayı gösterilir. Tarayıcı geri tuşu da bu guard'a takılır.

### 9.2 Pinia store — oturum durum makinesi

```
idle ──startSession()──> preparing ──oturum geldi──> question
                              │                        │
                              │ hata                   │ answer() gönderildi
                              ▼                        ▼
                            error                   answering
                                                       │ yanıt geldi
                                                       ▼
                                                    feedback ──(1.2 sn)──┐
                                                       │                 │
                                          son soru ise │        soru var │
                                                       ▼                 │
                                                   finished ◄────────────┘
                                                       │ submitScore()
                                                       ▼
                                                   submitted
```

**`useQuizStore` state:**

```ts
interface QuizState {
  status: 'idle' | 'preparing' | 'question' | 'answering' | 'feedback' | 'finished' | 'submitted' | 'error'
  sessionId: string | null
  token: string | null
  category: Category | null
  question: Question | null
  questionIndex: number          // 0-tabanlı
  totalQuestions: number
  score: number
  correctCount: number
  wrongCount: number
  timeoutCount: number
  lastResult: AnswerResult | null
  summary: SessionSummary | null
  deadlineAt: number | null      // epoch ms
  clockSkewMs: number            // sunucu-istemci saat farkı
  error: ApiError | null
}
```

**Kalıcılık:** `sessionId` + `token` `sessionStorage`'a yazılır (localStorage değil — sekme kapanınca oturum düşmeli). Sayfa yenilendiğinde store bu değerleri okur ve `GET /current-question/` ile kaldığı yerden devam eder. `sessionStorage` erişimi try/catch ile sarılır; gizli sekmede çalışmazsa uygulama yine de çalışmalıdır (yenileme sonrası oturum kaybolur, kabul edilebilir).

### 9.3 Geri sayım (`useCountdown`)

Kritik nokta: `setInterval` tarayıcı arka plana atıldığında kısılır ve sayaç kayar. Bu yüzden:

- Sayaç `requestAnimationFrame` döngüsüyle çalışır ve **her karede `performance.now()` farkını** okur (tick sayma değil).
- Kalan süre = `deadlineAt - (Date.now() + clockSkewMs)`.
- `clockSkewMs`, oturum başlarken `served_at` ile istemci zamanı karşılaştırılarak hesaplanır. Sapma 2 saniyeyi aşarsa güvenilmez kabul edilir ve sayaç basitçe istemci tarafında 5000 ms'den geri sayar.
- `visibilitychange` olayında sayaç yeniden hizalanır (sekmeden dönünce doğru süreyi gösterir).
- Sayaç 0'a ulaştığında otomatik `selected_option_id: null` ile cevap gönderilir. **İstemci tarafında "süre doldu" kararı verilmez** — outcome'ı sunucu belirler.

### 9.4 API istemcisi

```ts
// src/api/client.ts
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,   // https://api.rapidquiz.app/api/v1
  timeout: 8000,
  headers: {
    'X-Client-Platform': 'web',
    'X-Client-Version': __APP_VERSION__,
  },
})

// İstek interceptor: aktif oturum token'ını ekle
// Yanıt interceptor: {error: {code, message}} zarfını ApiError'a çevir,
//                    401/410 durumunda store'u sıfırla ve ana sayfaya yönlendir
```

**Yeniden deneme politikası:** Cevap gönderme isteği ağ hatası alırsa **tek kez**, 400 ms sonra yeniden denenir. İkinci deneme de başarısız olursa kullanıcıya "Bağlantı koptu, devam etmek için dokun" ekranı gösterilir ve `GET /current-question/` ile senkronizasyon yapılır. Cevap gönderimi idempotent değildir ama sunucudaki `ALREADY_ANSWERED` koruması sayesinde çift gönderim zarar vermez — istemci bu hatayı alırsa sessizce senkronizasyona geçer.

### 9.5 Erişilebilirlik

- Şıklar gerçek `<button>` elemanlarıdır; klavyeyle `1-4` veya `A-D` tuşlarıyla da seçilebilir (masaüstünde hız için önemli).
- Geri sayım halkası `aria-hidden`; yanında `aria-live="polite"` ile "3 saniye kaldı" bildirimi (yalnızca 3 ve 1 saniyede duyurulur, sürekli değil).
- Cevap geri bildirimi yalnızca renkle değil, ikon (✓ / ✕) ve metinle de verilir — renk körlüğü için zorunlu.
- Tüm interaktif elemanlarda görünür `:focus-visible` halkası.
- `prefers-reduced-motion: reduce` altında konfeti, pulse ve kayan puan animasyonları kapatılır; geçişler anlık olur.
- Dokunma hedefleri en az 44×44 px.

### 9.6 Performans hedefleri

| Metrik | Hedef |
|---|---|
| İlk yüklemede JS bundle (gzip) | < 120 KB |
| Lighthouse Performance (mobil) | ≥ 90 |
| Soru geçişi (yanıt → yeni soru render) | < 100 ms (yanıt elde olduğunda) |
| Kritik font yüklemesi | `font-display: swap`, yalnızca kullanılan ağırlıklar (subset) |

Sonraki soru `answers/` yanıtıyla birlikte geldiği için soru geçişinde **ek ağ isteği yoktur** — bu, 5 saniyelik oyunun akıcılığı için temel tasarım kararıdır.

---

## 10. UI Tasarım Sistemi

### 10.1 Tasarım yönü

Hedef kitle genç kullanıcılardır. Arayüz **aydınlık, canlı ve enerjik** olmalıdır; koyu/ağır "hacker" estetiğinden kaçınılır.

| İlke | Uygulama |
|---|---|
| Aydınlık zemin | Ana arka plan açık lavanta-beyaz (`#F7F5FF`), koyu tema v1.0'da yok |
| Yüksek doygunluk | Mor, turkuaz, mercan, amber — pastel değil, canlı tonlar |
| Yumuşak geometri | Köşe yarıçapı 16–28 px, kartlarda yumuşak renkli gölgeler |
| Büyük tipografi | Soru metni 24–32 px; küçük gri metinden kaçınılır |
| Hareket = geri bildirim | Her animasyonun bir işlevi var; süsleme amaçlı hareket yok |
| Renk tek başına anlam taşımaz | Doğru/yanlış daima ikon + metinle desteklenir |

### 10.2 Renk tokenları

```css
:root {
  /* Marka */
  --color-primary:        #6C4DFF;   /* elektrik moru */
  --color-primary-strong: #5438E0;
  --color-primary-soft:   #EFEBFF;
  --color-accent:         #FF5C8A;   /* mercan pembe */
  --color-accent-soft:    #FFE9F0;

  /* Kategori renkleri — canlı ton (zemin, gradyan, kenarlık, ikon için) */
  --color-cat-yazilim:    #6C4DFF;
  --color-cat-yapayzeka:  #00C2A8;
  --color-cat-bilgisayar: #2B8CFF;
  --color-cat-ulkeler:    #FF8A3D;
  --color-cat-fizik:      #FF5C8A;

  /* Kategori renkleri — koyu ton (ÜSTÜNDE BEYAZ METİN olacak dolgular için) */
  --color-cat-yazilim-strong:    #5438E0;
  --color-cat-yapayzeka-strong:  #00806F;
  --color-cat-bilgisayar-strong: #1A6FD4;
  --color-cat-ulkeler-strong:    #C25510;
  --color-cat-fizik-strong:      #D62E5E;

  /* Zemin ve yüzeyler */
  --color-bg:             #F7F5FF;
  --color-surface:        #FFFFFF;
  --color-surface-alt:    #F1EEFC;
  --color-border:         #E4DFF7;

  /* Metin */
  --color-text:           #1B1233;   /* --color-bg üstünde ~16.6:1 */
  --color-text-muted:     #5A5273;   /* --color-bg üstünde ~6.7:1 */
  --color-text-on-color:  #FFFFFF;

  /* Durum */
  --color-success:        #0FA968;
  --color-success-soft:   #E3F8EE;
  --color-danger:         #E11D48;
  --color-danger-soft:    #FFE7EC;
  --color-warning:        #F59E0B;
  --color-warning-soft:   #FFF4E0;

  /* Geri sayım renkleri (süreye göre) */
  --color-timer-safe:     #0FA968;   /* 5.0 – 3.0 sn */
  --color-timer-warn:     #F59E0B;   /* 3.0 – 1.5 sn */
  --color-timer-critical: #E11D48;   /* 1.5 – 0 sn */

  /* Gradyanlar */
  --gradient-hero:  linear-gradient(135deg, #6C4DFF 0%, #FF5C8A 100%);
  --gradient-timer: linear-gradient(90deg, #0FA968 0%, #F59E0B 60%, #E11D48 100%);

  /* Gölgeler — renkli ve yumuşak */
  --shadow-sm:  0 2px 8px rgba(108, 77, 255, 0.08);
  --shadow-md:  0 8px 24px rgba(108, 77, 255, 0.12);
  --shadow-lg:  0 16px 40px rgba(108, 77, 255, 0.16);
  --shadow-glow: 0 0 0 4px rgba(108, 77, 255, 0.18);

  /* Köşe yarıçapı */
  --radius-sm: 10px;
  --radius-md: 16px;
  --radius-lg: 24px;
  --radius-xl: 28px;
  --radius-pill: 999px;

  /* Boşluk ölçeği (4px tabanlı) */
  --space-1: 4px;   --space-2: 8px;   --space-3: 12px;
  --space-4: 16px;  --space-5: 24px;  --space-6: 32px;
  --space-7: 48px;  --space-8: 64px;

  /* Hareket */
  --ease-out:    cubic-bezier(0.16, 1, 0.3, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
  --dur-fast:   120ms;
  --dur-base:   240ms;
  --dur-slow:   400ms;
}
```

**Kontrast kuralı (WCAG AA — normal metin 4.5:1, ≥24px kalın metin 3:1):**

| Dolgu rengi | Beyaz metin kontrastı | Kullanım |
|---|---|---|
| `--color-primary` `#6C4DFF` | 5.1:1 | ✅ Her boyutta beyaz metin |
| `--color-primary-strong` `#5438E0` | 7.0:1 | ✅ Her boyutta |
| `--color-danger` `#E11D48` | 4.7:1 | ✅ Her boyutta |
| `--color-cat-*-strong` (5 renk) | 4.5–4.9:1 | ✅ Her boyutta |
| `--color-success` `#0FA968` | 3.1:1 | ⚠️ Yalnızca büyük/kalın metin; küçük metinde `--color-text` kullan |
| `--color-cat-*` (canlı tonlar) | 2.3–3.3:1 | ❌ Beyaz metin **kullanılmaz** |
| `--color-warning` `#F59E0B` | 2.1:1 | ❌ Beyaz metin **kullanılmaz** |

**Pratik kural:** Canlı kategori renkleri **zemin, gradyan, kenarlık, ilerleme çubuğu ve ikon** için; üstlerinde metin taşıyacak dolgular için `-strong` varyantı kullanılır. Amber (`--color-warning`) üstünde daima koyu metin (`--color-text`) kullanılır. Kategori kartlarındaki gradyanlar `-strong` → canlı ton yönünde kurulur, böylece metnin oturduğu bölge daima yeterli kontrasta sahip olur.

### 10.3 Tipografi

| Rol | Font | Ağırlık | Boyut (mobil / masaüstü) |
|---|---|---|---|
| Ekran başlığı / puan | Space Grotesk | 700 | 40 / 56 px |
| Başlık (H1) | Space Grotesk | 700 | 28 / 36 px |
| Başlık (H2) | Space Grotesk | 600 | 22 / 26 px |
| Soru metni | Inter | 600 | 22 / 28 px |
| Şık metni | Inter | 500 | 16 / 18 px |
| Gövde | Inter | 400 | 15 / 16 px |
| Yardımcı / etiket | Inter | 500 | 13 / 14 px |
| Sayaç rakamı | Space Grotesk | 700 | 32 / 40 px, `tabular-nums` |

- Satır yüksekliği: başlıklarda 1.15, gövdede 1.5
- Türkçe karakter desteği zorunlu (her iki font da destekler)
- Fontlar self-host edilir (`woff2`, latin + latin-ext subset), Google Fonts'a runtime bağımlılık olmaz

### 10.4 Komponent envanteri

**Temel (`components/base/`)**

| Komponent | Varyantlar | Not |
|---|---|---|
| `BaseButton` | `primary`, `secondary`, `ghost`, `danger` · boyut `md`, `lg` | `lg` min-height 56px; basılınca `scale(0.97)` |
| `BaseCard` | `flat`, `elevated`, `gradient` | |
| `BaseBadge` | kategori rengi, sıra rozeti (altın/gümüş/bronz) | |
| `BaseInput` | metin | Hata durumu + yardım metni |
| `BaseSpinner` | | Yükleme |
| `BaseTabs` | | Skor tablosu sekmeleri |
| `EmptyState` | | "Henüz skor yok" |
| `ErrorState` | | Hata + "Tekrar dene" |

**Quiz (`components/quiz/`)**

| Komponent | Sorumluluk |
|---|---|
| `CategoryCard` | Kategori adı, ikon, gradyan zemin, soru sayısı, oynanamaz durumu |
| `CountdownRing` | SVG dairesel progress; renk geçişi, son 2 sn pulse, `stroke-dashoffset` animasyonu |
| `QuestionProgress` | `Soru 7/20` + ince ilerleme çubuğu |
| `QuestionCard` | Soru metni kapsayıcısı; geçişte yandan kayarak girer |
| `OptionButton` | A/B/C/D rozeti + metin; durumlar: `idle`, `selected`, `correct`, `wrong`, `disabled` |
| `FeedbackOverlay` | Doğru/yanlış/süre doldu geri bildirimi, ikon + metin |
| `ScorePopup` | `+173` kayan puan rozeti |
| `ScoreCounter` | Sonuç ekranında 0'dan yukarı sayan puan |
| `StatTile` | Doğru / Yanlış / Kaçırılan sayıları |

**Skor tablosu (`components/leaderboard/`)**

| Komponent | Sorumluluk |
|---|---|
| `LeaderboardTable` | Liste + boş/yükleniyor durumları |
| `LeaderboardRow` | Sıra, takma ad, puan, kategori rozeti; `highlighted` prop'u kullanıcının satırını parlatır |
| `RankMedal` | İlk 3 için madalya görseli |

### 10.5 Anahtar animasyonlar

| Yer | Animasyon | Süre |
|---|---|---|
| Kategori kartı tıklama | `scale(0.96)` → sayfa geçişi | 120 ms |
| Hazırlık ekranı | "3-2-1-BAŞLA" rakamları `scale(1.6 → 1)` + fade | 3 × 700 ms + 400 ms |
| Soru girişi | Karttan sağdan sola kayma + fade in | 240 ms, `--ease-out` |
| Geri sayım son 2 sn | Halka `scale(1 → 1.04 → 1)` pulse, sonsuz | 600 ms döngü |
| Doğru cevap | Şık yeşile döner + kısa konfeti + `+puan` yukarı kayar | 400 ms |
| Yanlış cevap | Şık kırmızıya döner + hafif yatay shake (±4px) | 300 ms |
| Süre doldu | Ekran kenarında kırmızı flaş + "Süre doldu!" | 400 ms |
| Sonuç puanı | 0'dan hedefe sayma (ease-out) | 1200 ms |
| Skor tablosu satırları | Kademeli (stagger) fade-in, satır başına 40 ms gecikme | — |

Tümü `prefers-reduced-motion: reduce` altında devre dışı bırakılır.

### 10.6 Responsive davranış

| Kırılım | Genişlik | Davranış |
|---|---|---|
| Mobil | < 640 px | Tek sütun, kategori grid 2 sütun, içerik kenar boşluğu 16 px |
| Tablet | 640–1024 px | Kategori grid 3 sütun, içerik maksimum 640 px genişlik, ortalanmış |
| Masaüstü | > 1024 px | İçerik maksimum 720 px; quiz ekranı dikey ortalanmış "kart" görünümü |

Tasarım **mobil öncelikli** yazılır. Quiz ekranı her kırılımda tek ekrana sığmalı, dikey kaydırma olmamalıdır.

---

## 11. Mobil Uygulama Hazırlığı

Mobil uygulama v1.1'de gelecek, ancak backend baştan itibaren buna hazır tasarlanır. Aşağıdakiler **v1.0'da uygulanacak** hazırlıklardır:

| Konu | Karar |
|---|---|
| Protokol | Saf JSON REST — HTML render eden hiçbir endpoint yok |
| Kimlik | Çerez ve CSRF yok; `X-Session-Token` başlığı. Mobilde token güvenli depoda (Keychain / Keystore) tutulur |
| Sürümleme | `/api/v1/` yolu. Mobil sürümler yavaş güncellenir; v1 en az 6 ay desteklenir |
| İstemci tanımı | Her istekte `X-Client-Platform` ve `X-Client-Version`. Sunucu, desteklenmeyen eski sürümlere `426 UPGRADE_REQUIRED` dönebilecek şekilde hazır bırakılır |
| Sözleşme paylaşımı | `openapi.yaml` CI'da üretilir; mobil istemci bundan model üretir |
| Zaman | Tüm zaman damgaları UTC + ISO 8601. Sunucu saati esas; istemci saat sapmasını `served_at` ile hesaplar |
| Ağ dayanıklılığı | `GET /current-question/` sayesinde uygulama arka plana atılıp dönse de oturum kaldığı yerden devam eder |
| Yük | Yanıtlar küçük tutulur; soru yanıtı < 2 KB. Toplu soru listesi endpoint'i yok |
| Görseller | v1.0'da sorularda görsel yok. İleride eklenirse ayrı CDN URL'i ve `image_url` alanı ile |
| Push / bildirim | v1.0 kapsamı dışı; veri modeli buna bağımlılık içermez |
| Offline | v1.0'da desteklenmez (sunucu otoriteli süre gereği). Mobilde bağlantı yoksa net hata ekranı gösterilir |

**Mobil-spesifik dikkat noktaları (v1.1 için not):**

- Uygulama arka plana alındığında istemci sayacı durmaz — sunucu zamanı işler; dönünce soru muhtemelen `timeout` olmuş olur. Bu davranış kullanıcıya "Uygulamadan çıkınca süre işlemeye devam eder" şeklinde ilk oyunda bildirilir.
- Düşük bant genişliğinde grace period yeterli olmayabilir; `QUIZ_GRACE_PERIOD_MS` ayarı mobil trafiğe göre yeniden değerlendirilir.

---

## 12. Örnek Seed Verisi

Sorular `apps/catalog/fixtures/questions/<kategori-slug>.json` dosyalarında tutulur ve `python manage.py seed_questions` komutuyla yüklenir. Komut **idempotent**tir: aynı `external_ref` değerine sahip soru varsa günceller, yoksa oluşturur.

### 12.1 Fixture formatı

```json
{
  "category": {
    "slug": "yazilim",
    "name": "Yazılım",
    "description": "Diller, algoritmalar, araçlar",
    "color_hex": "#6C4DFF",
    "icon": "code",
    "display_order": 1
  },
  "questions": [
    {
      "external_ref": "yazilim-001",
      "text": "HTTP'de 404 durum kodu ne anlama gelir?",
      "difficulty": 1,
      "explanation": "404 Not Found, istenen kaynağın sunucuda bulunamadığını belirtir.",
      "options": [
        { "text": "İstenen kaynak bulunamadı", "is_correct": true },
        { "text": "İstek başarıyla tamamlandı", "is_correct": false },
        { "text": "Sunucu iç hatası oluştu", "is_correct": false },
        { "text": "Yetkilendirme gerekli", "is_correct": false }
      ]
    }
  ]
}
```

> `external_ref`, `Question` modelinde `CharField(40, unique=True, null=True)` olarak bulunur ve yalnızca seed yönetimi içindir; API'de dönülmez. Şık sırası **veritabanında** fixture'daki sıradır, ancak API her oturum için şıkları karıştırarak gönderir — yani "doğru şık hep ilk sırada" olması sorun değildir.

### 12.2 Kategori başına örnek sorular

#### Yazılım

```json
[
  {
    "external_ref": "yazilim-001",
    "text": "HTTP'de 404 durum kodu ne anlama gelir?",
    "difficulty": 1,
    "options": [
      { "text": "İstenen kaynak bulunamadı", "is_correct": true },
      { "text": "İstek başarıyla tamamlandı", "is_correct": false },
      { "text": "Sunucu iç hatası oluştu", "is_correct": false },
      { "text": "Yetkilendirme gerekli", "is_correct": false }
    ]
  },
  {
    "external_ref": "yazilim-002",
    "text": "Sıralı bir dizide ikili aramanın (binary search) zaman karmaşıklığı nedir?",
    "difficulty": 2,
    "options": [
      { "text": "O(log n)", "is_correct": true },
      { "text": "O(n)", "is_correct": false },
      { "text": "O(n log n)", "is_correct": false },
      { "text": "O(1)", "is_correct": false }
    ]
  },
  {
    "external_ref": "yazilim-003",
    "text": "Git'te çalışma dizinindeki değişiklikleri commit etmeden geçici olarak saklayan komut hangisidir?",
    "difficulty": 2,
    "options": [
      { "text": "git stash", "is_correct": true },
      { "text": "git revert", "is_correct": false },
      { "text": "git rebase", "is_correct": false },
      { "text": "git clean", "is_correct": false }
    ]
  }
]
```

#### Yapay Zekâ

```json
[
  {
    "external_ref": "yapay-zeka-001",
    "text": "Denetimli öğrenme (supervised learning) için eğitim verisinde ne bulunmak zorundadır?",
    "difficulty": 1,
    "options": [
      { "text": "Etiketlenmiş örnekler", "is_correct": true },
      { "text": "Yalnızca görsel veriler", "is_correct": false },
      { "text": "Ödül sinyali", "is_correct": false },
      { "text": "Etiketsiz kümeler", "is_correct": false }
    ]
  },
  {
    "external_ref": "yapay-zeka-002",
    "text": "Bir modelin eğitim verisinde çok başarılı olup yeni veride kötü sonuç vermesine ne denir?",
    "difficulty": 1,
    "options": [
      { "text": "Aşırı öğrenme (overfitting)", "is_correct": true },
      { "text": "Eksik öğrenme (underfitting)", "is_correct": false },
      { "text": "Normalizasyon", "is_correct": false },
      { "text": "Çapraz doğrulama", "is_correct": false }
    ]
  },
  {
    "external_ref": "yapay-zeka-003",
    "text": "Transformer mimarisini tanıtan 2017 tarihli makalenin adı nedir?",
    "difficulty": 3,
    "options": [
      { "text": "Attention Is All You Need", "is_correct": true },
      { "text": "ImageNet Classification with Deep CNNs", "is_correct": false },
      { "text": "Generative Adversarial Networks", "is_correct": false },
      { "text": "Deep Residual Learning", "is_correct": false }
    ]
  }
]
```

#### Bilgisayar Mühendisliği

```json
[
  {
    "external_ref": "bilgisayar-muhendisligi-001",
    "text": "1 byte kaç bitten oluşur?",
    "difficulty": 1,
    "options": [
      { "text": "8", "is_correct": true },
      { "text": "4", "is_correct": false },
      { "text": "16", "is_correct": false },
      { "text": "32", "is_correct": false }
    ]
  },
  {
    "external_ref": "bilgisayar-muhendisligi-002",
    "text": "İşlemcide, çalıştırılacak bir sonraki komutun adresini tutan yazmaç hangisidir?",
    "difficulty": 2,
    "options": [
      { "text": "Program sayacı (Program Counter)", "is_correct": true },
      { "text": "Yığın göstericisi (Stack Pointer)", "is_correct": false },
      { "text": "Akümülatör", "is_correct": false },
      { "text": "Durum yazmacı (Status Register)", "is_correct": false }
    ]
  },
  {
    "external_ref": "bilgisayar-muhendisligi-003",
    "text": "OSI referans modelinde IP protokolü hangi katmanda yer alır?",
    "difficulty": 2,
    "options": [
      { "text": "Ağ katmanı (3. katman)", "is_correct": true },
      { "text": "Taşıma katmanı (4. katman)", "is_correct": false },
      { "text": "Veri bağı katmanı (2. katman)", "is_correct": false },
      { "text": "Uygulama katmanı (7. katman)", "is_correct": false }
    ]
  }
]
```

#### Ülkeler

```json
[
  {
    "external_ref": "ulkeler-001",
    "text": "Avustralya'nın başkenti hangi şehirdir?",
    "difficulty": 1,
    "options": [
      { "text": "Canberra", "is_correct": true },
      { "text": "Sydney", "is_correct": false },
      { "text": "Melbourne", "is_correct": false },
      { "text": "Brisbane", "is_correct": false }
    ]
  },
  {
    "external_ref": "ulkeler-002",
    "text": "Yüzölçümü bakımından dünyanın en büyük ülkesi hangisidir?",
    "difficulty": 1,
    "options": [
      { "text": "Rusya", "is_correct": true },
      { "text": "Kanada", "is_correct": false },
      { "text": "Çin", "is_correct": false },
      { "text": "ABD", "is_correct": false }
    ]
  },
  {
    "external_ref": "ulkeler-003",
    "text": "Birleşmiş Milletler üyesi ülkeler arasında bayrağı kare şeklinde olan tek ülke hangisidir?",
    "difficulty": 3,
    "options": [
      { "text": "İsviçre", "is_correct": true },
      { "text": "Nepal", "is_correct": false },
      { "text": "Avusturya", "is_correct": false },
      { "text": "Belçika", "is_correct": false }
    ]
  }
]
```

#### Fizik

```json
[
  {
    "external_ref": "fizik-001",
    "text": "Işığın boşluktaki hızı yaklaşık olarak kaçtır?",
    "difficulty": 1,
    "options": [
      { "text": "300.000 km/s", "is_correct": true },
      { "text": "150.000 km/s", "is_correct": false },
      { "text": "3.000 km/s", "is_correct": false },
      { "text": "30.000.000 km/s", "is_correct": false }
    ]
  },
  {
    "external_ref": "fizik-002",
    "text": "Newton'un ikinci hareket yasası hangi bağıntıyla ifade edilir?",
    "difficulty": 1,
    "options": [
      { "text": "F = m · a", "is_correct": true },
      { "text": "E = m · c²", "is_correct": false },
      { "text": "P = F / A", "is_correct": false },
      { "text": "W = F · x", "is_correct": false }
    ]
  },
  {
    "external_ref": "fizik-003",
    "text": "SI birim sisteminde elektrik akımının birimi nedir?",
    "difficulty": 2,
    "options": [
      { "text": "Amper", "is_correct": true },
      { "text": "Volt", "is_correct": false },
      { "text": "Ohm", "is_correct": false },
      { "text": "Coulomb", "is_correct": false }
    ]
  }
]
```

### 12.3 Soru yazım kuralları

Kalan soruları üretirken uyulacak kurallar:

1. **Kısalık:** Soru metni en fazla 140 karakter olmalı. 5 saniyede okunup cevaplanabilmeli.
2. **Şık uzunluğu:** Her şık en fazla 40 karakter. Uzun şıklar okuma süresini yer.
3. **Tek doğru:** Tam 4 şık, tam 1 doğru. "Hepsi" / "Hiçbiri" şıkları kullanılmaz.
4. **Çeldiriciler makul olmalı:** Açıkça saçma şıklar sorunun zorluğunu yapay şekilde düşürür.
5. **Zamansız bilgi:** "Şu anki cumhurbaşkanı kim?" gibi eskiyecek sorular kullanılmaz. Ülkeler kategorisinde başkent, yüzölçümü, bayrak gibi kalıcı bilgiler tercih edilir.
6. **Tarafsızlık:** Siyasi, dini veya tartışmalı içerik yok.
7. **Zorluk dağılımı:** Kategori başına yaklaşık %40 kolay (1), %40 orta (2), %20 zor (3).
8. **Doğruluk kontrolü:** Her soru için kaynak kontrolü yapılır; şüpheli bilgi havuza girmez.

---

## 13. Test Stratejisi

### 13.1 Backend

| Seviye | Kapsam | Araç |
|---|---|---|
| Birim | `services.py` içindeki puanlama ve süre mantığı | pytest |
| Birim | Model kısıtları (4 şık / 1 doğru), nickname doğrulama | pytest |
| Entegrasyon | Tüm endpoint'ler: mutlu yol + her hata kodu | pytest + DRF APIClient |
| Entegrasyon | Eşzamanlılık: aynı soruya iki paralel cevap | pytest + threading/transaction testi |

**Zorunlu test senaryoları:**

- [ ] Oturum oluşturulduğunda tam 20 `QuizSessionQuestion` kaydı üretilir, tekrar eden soru yoktur
- [ ] Soru yanıtında hiçbir yerde `is_correct` sızmaz (yanıt JSON'ı üzerinde doğrudan assert)
- [ ] 4900 ms'de gelen doğru cevap puan alır; 5200 ms'de gelen `timeout` olur
- [ ] Grace period içinde (5100 ms) gelen doğru cevap kabul edilir, puanı 100 (minimum) olur
- [ ] Aynı soruya ikinci cevap `409 ALREADY_ANSWERED` döner ve puanı değiştirmez
- [ ] `current-question` çağrısı `served_at`'i sıfırlamaz (süre yenileme sömürüsü)
- [ ] `current-question`, süresi geçmiş soruyu `timeout` işaretleyip sonrakine geçer
- [ ] Yanlış token ile erişim `401`, başka oturumun id'si ile `403` döner
- [ ] 20. cevaptan sonra oturum `completed` olur, `next_question` `null` gelir
- [ ] `submit-score` ikinci kez çağrılınca `409 SCORE_ALREADY_SUBMITTED` döner
- [ ] Skor tablosuna yazılan puan, istemciden gelen değil, oturumdaki puandır
- [ ] Sıralama doğru: eşit puanda daha kısa `total_elapsed_ms` üstte
- [ ] 20 aktif sorusu olmayan kategoride oturum açma `422` döner
- [ ] Throttle limitleri aşıldığında `429` ve `Retry-After` döner
- [ ] `X-Forwarded-For` başlığı doğru çözülür: proxy arkasında iki farklı istemci IP'si ayrı throttle sayaçları kullanır (§14.4)

### 13.2 Frontend

| Seviye | Kapsam | Araç |
|---|---|---|
| Birim | `useCountdown` — sekme gizlenip dönünce doğru süre | Vitest + fake timers |
| Birim | Pinia store durum geçişleri | Vitest |
| Komponent | `OptionButton` durumları, `CountdownRing` renk eşikleri | Vue Test Utils |
| E2E | Tam oyun akışı: kategori → 20 soru → skor → isim → tablo | Playwright (mock API) |
| E2E | Süre dolması senaryosu, bağlantı kopması senaryosu | Playwright |

**Zorunlu E2E senaryoları:**

- [ ] 20 soru baştan sona tamamlanır, sonuç ekranında doğru dağılım görünür
- [ ] Bir soruya cevap verilmeden 5 saniye beklenir → otomatik geçiş olur, "Süre doldu" gösterilir
- [ ] Soru ekranında sayfa yenilenir → aynı soruyla devam edilir, süre sıfırlanmaz
- [ ] Şıkka çift tıklanır → yalnızca bir cevap gönderilir
- [ ] Klavyeyle (A/B/C/D) cevap verilebilir
- [ ] `prefers-reduced-motion` açıkken animasyonlar çalışmaz
- [ ] Skor tablosunda kullanıcının satırı vurgulanır

### 13.3 Kalite kapıları (CI)

Her PR'da çalışacak kontroller:

**Backend:** `ruff check` → `ruff format --check` → `pytest --cov` (kapsam ≥ %85, `services.py` için ≥ %95) → `manage.py spectacular --validate`
**Frontend:** `eslint` → `prettier --check` → `vue-tsc --noEmit` → `vitest run --coverage` → `playwright test` → `vite build`

---

## 14. Ortamlar ve Deployment

### 14.1 Ortamlar

**Platform kararı: DigitalOcean App Platform.** Backend bir **Service** (Dockerfile'dan derlenir), frontend bir **Static Site** bileşeni olarak deploy edilir.

| Ortam | Backend | Frontend | Veritabanı |
|---|---|---|---|
| Local | Docker Compose, `:8000` | `vite dev`, `:5173` | Docker Compose PostgreSQL 16 |
| Staging | DO App Platform Service (Basic, 1 instance) | DO App Platform Static Site | DO Dev Database (PG) |
| Production | DO App Platform Service (Basic/Professional, ≥2 instance) | DO App Platform Static Site (global CDN dahil) | DO Managed PostgreSQL (yönetilen küme, otomatik yedek) |

**Neden iki ayrı App:** Backend ve frontend ayrı repolarda olduğu için DigitalOcean'da da iki ayrı App oluşturulur (`rapid-quiz-api`, `rapid-quiz-web`). Bu, frontend'in deploy'unun backend'i yeniden başlatmamasını ve statik sitenin ücretsiz/ucuz katmanda kalmasını sağlar. (Alternatif olarak tek App içinde iki bileşen de tanımlanabilir; ayrı App tercih edilmiştir.)

### 14.2 Yerel geliştirme kurulumu

**Backend**

Tamamı Docker ile (production imajının birebir aynısı çalışır):

```bash
git clone <backend-repo> && cd rapid-quiz-api
cp .env.example .env
docker compose up --build            # api + db ayağa kalkar
docker compose exec api python manage.py migrate
docker compose exec api python manage.py seed_questions
docker compose exec api python manage.py createsuperuser
# API:    http://localhost:8000/api/v1/
# Docs:   http://localhost:8000/api/docs/
# Admin:  http://localhost:8000/admin/
```

Veya yalnızca veritabanı Docker'da, Django yerel virtualenv'de (daha hızlı iterasyon):

```bash
docker compose up -d db              # PostgreSQL 16
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python manage.py migrate && python manage.py seed_questions
python manage.py runserver
```

**Frontend**

```bash
git clone <frontend-repo> && cd rapid-quiz-web
cp .env.example .env   # VITE_API_BASE_URL=http://localhost:8000/api/v1
npm install
npm run dev            # http://localhost:5173
```

### 14.3 Backend Docker yapılandırması

DigitalOcean App Platform, repo kökündeki `Dockerfile`'ı algılayıp imajı kendi build ortamında derler. Bu yüzden imaj **kendi kendine yeten** (self-contained) ve **yerelde de aynı şekilde çalışan** bir imaj olmalıdır.

#### `Dockerfile` (çok aşamalı)

```dockerfile
# ---------- 1. aşama: bağımlılıklar ----------
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml ./
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# ---------- 2. aşama: çalışma imajı ----------
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    PORT=8080

# libpq-dev yerine yalnızca çalışma zamanı kütüphanesi
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 appuser

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
COPY --chown=appuser:appuser . .

# Statik dosyalar (yalnızca admin + Swagger UI için) imaja gömülür
RUN SECRET_KEY=build-only DATABASE_URL=postgres://u:p@localhost:5432/db \
    python manage.py collectstatic --noinput

USER appuser
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
    CMD curl -fsS "http://localhost:${PORT}/api/v1/health/" || exit 1

CMD ["sh", "-c", "gunicorn config.wsgi:application \
     --bind 0.0.0.0:${PORT} \
     --workers ${GUNICORN_WORKERS:-3} \
     --threads ${GUNICORN_THREADS:-2} \
     --timeout 30 \
     --graceful-timeout 20 \
     --access-logfile - --error-logfile - \
     --log-level info"]
```

**Dikkat edilecek noktalar:**

| Konu | Karar | Gerekçe |
|---|---|---|
| Port | `PORT` ortam değişkeninden okunur, varsayılan `8080` | App Platform konteynere `PORT` enjekte eder; sabit port yazmak deploy'u kırar |
| Kullanıcı | root değil, `appuser` (uid 10001) | Güvenlik; App Platform root olmayan kullanıcı ile sorunsuz çalışır |
| `collectstatic` | Build zamanında, sahte env değerleriyle | Çalışma anında dosya sistemi yazımı gerekmesin; `production.py` bu sahte değerlerle import edilebilir olmalı |
| Migration | Dockerfile'da **çalıştırılmaz** | Migration, birden çok instance ayağa kalkarken yarış yaratır; ayrı `PRE_DEPLOY` job'ında çalışır (§14.5) |
| Worker sayısı | `(2 × vCPU) + 1` kuralı, env ile ayarlanabilir | Basic instance'ta 3 worker makul başlangıç |
| Timeout | 30 sn | Endpoint'lerin hepsi hızlı; uzun timeout kaynak tutar |
| `HEALTHCHECK` | Dockerfile'da tanımlı, ayrıca app spec'te de var | Yerelde `docker compose ps` sağlığı gösterir; DO kendi health check'ini kullanır |

#### `.dockerignore`

```
.git
.gitignore
.venv
__pycache__/
*.py[cod]
.pytest_cache/
.ruff_cache/
.mypy_cache/
htmlcov/
.coverage
.env
.env.*
!.env.example
*.sqlite3
media/
staticfiles/
docs/
tests/
.github/
README.md
docker-compose*.yml
```

> `tests/` imaja alınmaz — imaj boyutu küçülür ve test kodu production'a sızmaz. CI testleri ayrı bir adımda (imaj dışında) çalışır.

#### `docker-compose.yml` (yalnızca yerel geliştirme)

```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: rapidquiz
      POSTGRES_USER: rapidquiz
      POSTGRES_PASSWORD: rapidquiz
    ports: ["5432:5432"]
    volumes: ["pgdata:/var/lib/postgresql/data"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U rapidquiz"]
      interval: 5s
      retries: 10

  api:
    build: { context: ., target: runtime }
    env_file: .env
    environment:
      DJANGO_SETTINGS_MODULE: config.settings.local
      DATABASE_URL: postgres://rapidquiz:rapidquiz@db:5432/rapidquiz
      PORT: "8000"
    ports: ["8000:8000"]
    depends_on:
      db: { condition: service_healthy }
    volumes: ["./:/app"]        # yerelde canlı kod; production imajında yok

volumes:
  pgdata:
```

> Production'da Redis kullanılıyorsa compose'a `redis:7-alpine` servisi de eklenir. Yerelde throttle sayaçları için LocMem yeterlidir; Redis opsiyoneldir.

---

### 14.4 Production Django ayarları

`config/settings/production.py` içinde:

```python
DEBUG = False
SECRET_KEY = env("SECRET_KEY")                      # DO'da SECRET tipinde env var

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")           # api.rapidquiz.app, *.ondigitalocean.app
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS")   # yalnızca admin paneli için

# App Platform, TLS'i kendi katmanında sonlandırıp X-Forwarded-Proto gönderir
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31_536_000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"

# DO Managed PostgreSQL TLS zorunlu
DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["CONN_MAX_AGE"] = 60
DATABASES["default"].setdefault("OPTIONS", {})["sslmode"] = env("DB_SSLMODE", default="require")

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Gerçek istemci IP'si (throttling doğru çalışsın diye)
# App Platform X-Forwarded-For başlığını ekler; en sağdaki güvenilir olmayan
# değerler yerine django-ipware ile çözülür.
LOGGING = {...}   # JSON formatında stdout
```

**Kritik:** Throttling IP bazlı olduğu için `X-Forwarded-For` yanlış okunursa **tüm kullanıcılar tek IP gibi görünür** ve herkes birbirinin limitini tüketir. `django-ipware` kullanılmalı ve `IPWARE_TRUSTED_PROXY_LIST` App Platform proxy'sine göre ayarlanmalıdır. Bu, §13.1'e ek bir test maddesi gerektirir.

---

### 14.5 DigitalOcean — Backend App

#### App spec: `.do/app.yaml`

```yaml
name: rapid-quiz-api
region: fra                      # Frankfurt — TR kullanıcılarına en düşük gecikme

services:
  - name: api
    dockerfile_path: Dockerfile
    source_dir: /
    github:
      repo: <org>/rapid-quiz-api
      branch: main
      deploy_on_push: true

    http_port: 8080
    instance_count: 2
    instance_size_slug: apps-s-1vcpu-1gb

    health_check:
      http_path: /api/v1/health/
      initial_delay_seconds: 20
      period_seconds: 10
      timeout_seconds: 3
      success_threshold: 1
      failure_threshold: 3

    envs:
      - key: DJANGO_SETTINGS_MODULE
        scope: RUN_TIME
        value: config.settings.production
      - key: SECRET_KEY
        scope: RUN_TIME
        type: SECRET
        value: <dashboard'dan girilir>
      - key: DATABASE_URL
        scope: RUN_TIME
        value: ${rapidquiz-db.DATABASE_URL}     # bindable variable
      - key: ALLOWED_HOSTS
        scope: RUN_TIME
        value: api.rapidquiz.app,${APP_DOMAIN}
      - key: CORS_ALLOWED_ORIGINS
        scope: RUN_TIME
        value: https://rapidquiz.app,https://www.rapidquiz.app
      - key: CSRF_TRUSTED_ORIGINS
        scope: RUN_TIME
        value: https://api.rapidquiz.app
      - key: REDIS_URL
        scope: RUN_TIME
        type: SECRET
        value: <varsa managed cache bağlantısı>
      - key: GUNICORN_WORKERS
        scope: RUN_TIME
        value: "3"
      - key: SENTRY_DSN
        scope: RUN_TIME
        type: SECRET
        value: <opsiyonel>

jobs:
  # Her deploy'dan ÖNCE, trafik yeni sürüme yönlenmeden çalışır
  - name: migrate
    kind: PRE_DEPLOY
    dockerfile_path: Dockerfile
    source_dir: /
    github:
      repo: <org>/rapid-quiz-api
      branch: main
    instance_size_slug: apps-s-1vcpu-0.5gb
    run_command: python manage.py migrate --noinput
    envs:
      - key: DJANGO_SETTINGS_MODULE
        scope: RUN_TIME
        value: config.settings.production
      - key: SECRET_KEY
        scope: RUN_TIME
        type: SECRET
        value: <aynı secret>
      - key: DATABASE_URL
        scope: RUN_TIME
        value: ${rapidquiz-db.DATABASE_URL}

  # Süresi geçmiş oturumların temizliği (§8.4)
  - name: cleanup-stale-sessions
    kind: SCHEDULED
    dockerfile_path: Dockerfile
    source_dir: /
    github:
      repo: <org>/rapid-quiz-api
      branch: main
    instance_size_slug: apps-s-1vcpu-0.5gb
    schedule: "0 3 * * *"          # her gün 03:00 UTC
    run_command: python manage.py cleanup_stale_sessions
    envs:
      - key: DJANGO_SETTINGS_MODULE
        scope: RUN_TIME
        value: config.settings.production
      - key: DATABASE_URL
        scope: RUN_TIME
        value: ${rapidquiz-db.DATABASE_URL}

databases:
  - name: rapidquiz-db
    engine: PG
    version: "16"
    production: true               # staging'de false (dev database)
    cluster_name: rapidquiz-pg

ingress:
  rules:
    - match:
        path:
          prefix: /
      component:
        name: api

alerts:
  - rule: DEPLOYMENT_FAILED
  - rule: DOMAIN_FAILED
```

**Neden `PRE_DEPLOY` job'ı:** `instance_count: 2` ile iki konteyner aynı anda ayağa kalkar. Migration'ı konteyner başlangıcına koyarsak ikisi aynı anda migration çalıştırmaya kalkar. `PRE_DEPLOY` job'ı, yeni sürüm trafiğe açılmadan **bir kez** çalışır ve başarısız olursa deploy durur — doğru davranış budur.

**Seed verisi:** `seed_questions` komutu her deploy'da çalıştırılmaz. İlk kurulumda ve soru havuzu güncellendiğinde **manuel** olarak çalıştırılır:

```bash
doctl apps console <APP_ID> --component api
# konteyner içinde:
python manage.py seed_questions
```

Alternatif olarak geçici bir `POST_DEPLOY` job'ı olarak tanımlanıp iş bitince spec'ten çıkarılabilir. Komut idempotent olduğu için (§12.1) tekrar çalıştırmak zararsızdır.

#### Oluşturma ve güncelleme

```bash
doctl apps create --spec .do/app.yaml            # ilk kurulum
doctl apps update <APP_ID> --spec .do/app.yaml   # spec değişikliği
doctl apps list
doctl apps logs <APP_ID> --type run --follow     # canlı loglar
doctl apps logs <APP_ID> --type build
```

`.do/app.yaml` repoda tutulur ve **versiyonlanır**; dashboard'dan elle yapılan değişiklikler bir sonraki `apps update` ile ezileceği için tüm yapılandırma bu dosyada tutulmalıdır. Tek istisna `SECRET` tipli değerlerdir — bunlar dashboard'dan girilir ve spec'te placeholder kalır.

---

### 14.6 DigitalOcean — Frontend Static Site

Frontend derlenmiş statik dosyalardan ibarettir (Vue SPA). App Platform statik siteyi global CDN üzerinden sunar ve ayrı bir konteyner maliyeti oluşturmaz.

#### App spec: `.do/app.yaml` (frontend repo'sunda)

```yaml
name: rapid-quiz-web
region: fra

static_sites:
  - name: web
    source_dir: /
    github:
      repo: <org>/rapid-quiz-web
      branch: main
      deploy_on_push: true

    environment_slug: node-js
    build_command: npm ci && npm run build
    output_dir: dist

    index_document: index.html
    catchall_document: index.html     # SPA: tüm yollar index.html'e düşer
    error_document: index.html

    envs:
      - key: VITE_API_BASE_URL
        scope: BUILD_TIME             # Vite env'leri derleme zamanında gömülür
        value: https://api.rapidquiz.app/api/v1
      - key: NODE_VERSION
        scope: BUILD_TIME
        value: "22"

alerts:
  - rule: DEPLOYMENT_FAILED
  - rule: DOMAIN_FAILED
```

**Kritik noktalar:**

| Konu | Karar |
|---|---|
| `catchall_document` | **Zorunlu.** Vue Router history modunda `/skorlar` gibi bir yola doğrudan girildiğinde 404 almamak için tüm istekler `index.html`'e yönlendirilir |
| `VITE_API_BASE_URL` scope'u | `BUILD_TIME` olmalı. Vite değişkenleri derleme anında bundle'a gömülür; `RUN_TIME` yazmak işe yaramaz |
| API adresi gizli değildir | `VITE_*` değişkenleri tarayıcıya gider. **Buraya asla secret konulmaz** |
| Ortam ayrımı | Staging static site'ı `https://staging-api.rapidquiz.app` değerini kullanır; her ortam kendi App'inde ayrı env değeriyle derlenir |
| Node sürümü | `NODE_VERSION` ile sabitlenir; build'in sürüm değişiminden etkilenmemesi için |
| Cache | App Platform statik varlıkları CDN'den sunar. Vite hash'li dosya adları ürettiği için uzun cache güvenlidir; `index.html` kısa cache'lenmelidir |

> **Not:** DigitalOcean'da statik site içeren ilk üç App ücretsizdir (her biri için aylık 1 GiB çıkış trafiği dahil); sonrası için ek ücret ve GiB başına transfer ücreti uygulanır. Güncel rakamlar için DO fiyat sayfası kontrol edilmelidir.

---

### 14.7 Veritabanı ve cache

#### Managed PostgreSQL

| Konu | Karar |
|---|---|
| Sürüm | PostgreSQL 16 |
| Ortam | Production: Managed Database kümesi (`production: true`). Staging: Dev Database (daha ucuz, yedeksiz) |
| Bağlantı | `${rapidquiz-db.DATABASE_URL}` bindable değişkeni ile otomatik enjekte edilir — bağlantı bilgisi elle yazılmaz |
| TLS | Zorunlu (`sslmode=require`). DO'nun verdiği `DATABASE_URL` bunu zaten içerir |
| Trusted Sources | Veritabanı kümesinde yalnızca `rapid-quiz-api` App'i güvenilir kaynak olarak eklenir. **Public erişim kapatılır** |
| Bağlantı havuzu | Instance sayısı × gunicorn worker sayısı, kümenin bağlantı limitini aşmamalı. 2 instance × 3 worker = 6 bağlantı; `CONN_MAX_AGE=60` ile yeniden kullanılır. Ölçeklenirken DO'nun connection pool özelliği devreye alınır |
| Yedek | Production kümesinde günlük otomatik yedek + point-in-time recovery. Yedekten dönüş prosedürü en az bir kez test edilir |
| Migration | Yalnızca `PRE_DEPLOY` job'ından. Elle `doctl apps console` ile migration çalıştırmak istisnai durumlara saklanır |

#### Cache / throttle sayaçları

Throttle sayaçları için iki seçenek:

1. **Redis/Valkey yok (başlangıç):** DRF throttle sayaçları LocMem'de tutulur. `instance_count: 2` olduğunda **her instance kendi sayacını tutar**, yani gerçek limit ilan edilenin iki katı olur. Kötüye kullanım riski düşükken kabul edilebilir.
2. **Yönetilen cache (önerilen, production):** DO Managed Caching (Valkey/Redis) kümesi açılır, `REDIS_URL` secret olarak tanımlanır ve DRF throttle backend'i Redis'e alınır. Limitler tüm instance'lar arasında tutarlı olur.

> **Karar:** Yayına Seçenek 1 ile çıkılır, skor tablosunda kötüye kullanım görülürse Seçenek 2'ye geçilir. Kod tarafında `CACHES` ayarı `REDIS_URL` varsa Redis, yoksa LocMem kullanacak şekilde yazılır — geçiş yalnızca bir env değişkeni eklemekle yapılır.

---

### 14.8 Domain, TLS ve CORS

| Bileşen | Domain | Not |
|---|---|---|
| Frontend | `rapidquiz.app`, `www.rapidquiz.app` | Static site App'ine PRIMARY domain olarak eklenir |
| Backend | `api.rapidquiz.app` | Service App'ine eklenir |
| Staging | `staging.rapidquiz.app`, `staging-api.rapidquiz.app` | Ayrı App'ler |

- DNS DigitalOcean'da yönetiliyorsa domain App'e eklendiğinde kayıtlar otomatik oluşur; harici DNS'te `CNAME` kaydı elle eklenir.
- **TLS sertifikaları App Platform tarafından otomatik sağlanır ve yenilenir** (Let's Encrypt). Ek yapılandırma gerekmez.
- Frontend ve backend **farklı alt alan adlarında** olduğu için CORS zorunludur. `CORS_ALLOWED_ORIGINS` yalnızca frontend domain'lerini içermeli, `*` kullanılmamalıdır.
- `CORS_ALLOW_CREDENTIALS = False` kalır (çerez kullanmıyoruz, §8.6).
- İlk deploy'da domain'ler hazır olmadan `*.ondigitalocean.app` adresleri kullanılır; bu adresler de `ALLOWED_HOSTS` ve `CORS_ALLOWED_ORIGINS`'e geçici olarak eklenir, domain bağlandıktan sonra çıkarılır.

---

### 14.9 CI/CD

**Temel akış:** `main` dalına merge → App Platform GitHub entegrasyonu (`deploy_on_push: true`) otomatik build ve deploy başlatır. GitHub Actions yalnızca **kalite kapısı** olarak çalışır; deploy'u DO yapar.

| Tetikleyici | GitHub Actions | DigitalOcean |
|---|---|---|
| PR açıldı/güncellendi | Backend: lint + test + `spectacular --validate` + `docker build` (imaj push edilmez, sadece derlenir)<br>Frontend: lint + tip kontrolü + test + `vite build` | — |
| `develop`'a merge | Aynı kontroller | Staging App'leri otomatik deploy eder |
| `main`'e merge | Aynı kontroller | Production App'leri otomatik deploy eder (PRE_DEPLOY migration dahil) |

**Neden PR'da `docker build` çalıştırılıyor:** App Platform imajı kendi tarafında derler. Dockerfile bozulursa bunu deploy anında değil, PR aşamasında görmek gerekir.

**Deploy'u bloke etme:** Production'da otomatik deploy istenmiyorsa `deploy_on_push: false` yapılır ve deploy GitHub Actions'tan `doctl apps create-deployment <APP_ID>` ile, manuel onaya bağlı bir environment üzerinden tetiklenir.

**Rollback:** App Platform her deploy'u versiyonlar; dashboard'dan veya `doctl apps list-deployments` + rollback ile önceki sürüme dönülebilir. **Ancak migration'lar geri alınmaz** — geriye dönük uyumsuz migration yazmaktan kaçınılmalıdır (sütun silme/yeniden adlandırma iki aşamalı yapılır).

Backend CI ayrıca `openapi.yaml` dosyasını üretir; dosya değişmişse PR'a otomatik commit atar. Böylece frontend her zaman güncel sözleşmeden tip üretir.

---

### 14.10 İzleme, log ve maliyet

**Loglar**

- Uygulama JSON formatında **stdout**'a yazar; App Platform bunları toplar (`doctl apps logs` veya dashboard).
- App Platform log saklama süresi kısadır. Kalıcı log için DO'nun log forwarding özelliğiyle harici bir servise (Papertrail, Datadog vb.) aktarılır — v1.0'da opsiyonel.
- Hata izleme: Sentry (`SENTRY_DSN` secret'ı). `WARNING` ve üstü gönderilir.

**Uyarılar (alerts)**

App spec'teki `alerts` bloğuna ek olarak dashboard'dan şunlar açılır:

| Uyarı | Eşik |
|---|---|
| `DEPLOYMENT_FAILED` | Her başarısız deploy |
| `DOMAIN_FAILED` | Sertifika/DNS sorunu |
| CPU kullanımı | 5 dakika boyunca > %80 |
| Bellek kullanımı | 5 dakika boyunca > %85 |
| Yanıt süresi (p99) | > 1000 ms |
| 5xx oranı | 5 dakikada > %1 |

> **Bu uygulamaya özel:** Yanıt süresi izlemesi kritik. `POST /answers/` yavaşlarsa 5 saniyelik oyun doğrudan bozulur. p99 hedefi **< 300 ms**'tir ve bu metrik ayrı izlenmelidir.

**Maliyet planlaması**

| Kalem | Ortam | Not |
|---|---|---|
| Static Site (frontend) | Prod + staging | İlk üç statik site App'i ücretsiz (App başına 1 GiB/ay çıkış dahil) |
| Service (backend) | Prod: 2 × Basic (1 vCPU / 1 GB) | Trafiğe göre `instance_count` ayarlanır |
| Service (backend) | Staging: 1 × Basic (512 MB) | |
| Managed PostgreSQL | Prod | Yönetilen küme + otomatik yedek |
| Dev Database | Staging | Aylık sabit ücret, yedeksiz |
| PRE_DEPLOY / SCHEDULED job | Her ikisi | Yalnızca çalıştığı süre kadar ücretlendirilir |
| Managed Caching (Valkey) | Prod, opsiyonel | §14.7 Seçenek 2'ye geçilirse |

Güncel birim fiyatlar için DigitalOcean App Platform fiyatlandırma sayfası kontrol edilmelidir; rakamlar zaman içinde değişmektedir.

**Ölçekleme notu:** Uygulama durumsuzdur (oturum bilgisi veritabanında, konteynerde değil), bu yüzden `instance_count` artırmak güvenlidir. Darboğaz önce veritabanı bağlantı limitinde görülür; o noktada DO connection pooling devreye alınır.

---

## 15. Yol Haritası ve Görev Listesi

Aşağıdaki görevler, Claude Code'a **sırayla** verilebilecek şekilde yazılmıştır. Her görev tek başına tamamlanabilir ve doğrulanabilir bir çıktı üretir.

### Milestone 0 — Temel kurulum (Backend)

- [x] **B0.1** Django projesini oluştur: `config/settings/{base,local,production}.py` ayrımı, `django-environ` ile `.env` okuma, `pyproject.toml` + ruff yapılandırması
- [x] **B0.2** PostgreSQL için `docker-compose.yml` ve `.env.example` hazırla; `DATABASE_URL` ile bağlan (§14.3)
- [x] **B0.2b** Çok aşamalı `Dockerfile` ve `.dockerignore` yaz (§14.3): non-root kullanıcı, `PORT` env'inden port okuma, build zamanında `collectstatic`, gunicorn CMD. `docker build` + `docker run` ile yerelde çalıştığını doğrula
- [x] **B0.2c** `requirements.txt` üretimini kur (`pip-compile` veya `uv pip compile`) — Dockerfile bunu kullanır, sürümler kilitli olmalı
- [x] **B0.3** DRF, drf-spectacular, django-cors-headers kur ve yapılandır; `/api/v1/health/` endpoint'ini yaz
- [x] **B0.4** Standart hata zarfını üreten `common/exceptions.py` ve özel exception sınıflarını yaz (§7.2'deki tüm kodlar)
- [x] **B0.5** pytest + pytest-django + factory_boy kurulumu; `health` endpoint'i için ilk test

### Milestone 1 — İçerik modeli (Backend)

- [x] **B1.1** `catalog` app: `Category`, `Question`, `AnswerOption` modellerini ve migration'ları yaz (§6.2)
- [x] **B1.2** "Tam 4 şık, tam 1 doğru" kuralını model `clean()` ve admin formset validasyonunda uygula
- [x] **B1.3** Django admin'i yapılandır: `AnswerOption` inline, kategori filtresi, aktif soru sayısı sütunu
- [x] **B1.4** `GET /api/v1/categories/` endpoint'i ve serializer'ı (`available_question_count`, `is_playable` dahil)
- [x] **B1.5** `seed_questions` yönetim komutu (idempotent, `external_ref` ile upsert, fixture doğrulaması)
- [x] **B1.6** 5 kategori için fixture dosyalarını oluştur — §12'deki örneklerle başla, kategori başına 20'ye tamamla *(taslak hazır, insan doğrulaması bekliyor — Q3)*
- [x] **B1.7** Testler: model kısıtları, seed komutu idempotency, categories endpoint'i

### Milestone 2 — Quiz motoru (Backend) — *en kritik aşama*

- [x] **B2.1** `quiz` app: `QuizSession`, `QuizSessionQuestion` modelleri ve migration'ları (§6.2)
- [x] **B2.2** `SessionTokenAuthentication` sınıfı ve sahiplik kontrolü permission'ı
- [x] **B2.3** `services.create_session()`: rastgele 20 soru seçimi, oturum ve soru kayıtlarının oluşturulması, yetersiz soru kontrolü
- [x] **B2.4** `services.serve_question()`: `served_at` yazma (yalnızca ilk serviste), şık karıştırma, `deadline_at` hesabı
- [x] **B2.5** `services.submit_answer()`: `select_for_update` ile kilit, süre hesabı, grace period, puanlama formülü, sayaç güncelleme, `current_index` ilerletme (§4.2)
- [x] **B2.6** `services.finalize_session()`: cevaplanmamışları `timeout` işaretleme, `status=completed`, özet hesaplama
- [x] **B2.7** `POST /quiz-sessions/` endpoint'i (§7.4)
- [x] **B2.8** `GET /quiz-sessions/{id}/current-question/` endpoint'i — süresi geçmiş soruyu otomatik kapatma davranışı dahil (§7.5)
- [x] **B2.9** `POST /quiz-sessions/{id}/answers/` endpoint'i — `next_question` gömülü, 20. soruda `summary` gömülü (§7.6)
- [x] **B2.10** `GET /quiz-sessions/{id}/summary/` endpoint'i, `estimated_rank` hesabı (§7.7)
- [x] **B2.11** Throttle sınıfları ve limitleri (§8.5)
- [x] **B2.12** `cleanup_stale_sessions` yönetim komutu
- [x] **B2.13** §13.1'deki zorunlu test senaryolarının tamamını yaz — özellikle `is_correct` sızıntısı ve süre sömürüsü testleri

### Milestone 3 — Skor tablosu (Backend)

- [x] **B3.1** `LeaderboardEntry` modeli, bileşik indeks ve sıralama kuralı (§6.2)
- [x] **B3.2** `common/nickname.py`: takma ad doğrulama kuralları (§7.8) — küfür filtresi yok
- [x] **B3.3** `POST /quiz-sessions/{id}/submit-score/` endpoint'i — tek seferlik kayıt garantisi, Top 10'un yanıta gömülmesi
- [x] **B3.4** `GET /api/v1/leaderboard/` endpoint'i — kategori filtresi, sayfalama, genel/kategori kapsamı
- [x] **B3.5** Admin'de `LeaderboardEntry` salt okunur görünüm + silme aksiyonu
- [x] **B3.6** Testler: tek seferlik kayıt, sıralama doğruluğu, puanın sunucudan alınması, filtre doğrulaması

### Milestone 4 — API sözleşmesinin dondurulması

- [x] **B4.1** Tüm endpoint'ler için drf-spectacular açıklamaları, örnek request/response'lar, hata şemaları
- [x] **B4.2** `openapi.yaml` üretimi ve CI'da doğrulama (otomatik commit yerine: dosya eskiyse CI başarısız olur)
- [x] **B4.3** `README.md`: kurulum, komutlar, ortam değişkenleri, API özeti

### Milestone 5 — Frontend iskeleti

- [ ] **F5.1** Vite + Vue 3 + TypeScript projesini oluştur; ESLint, Prettier, Vitest, Playwright yapılandır
- [ ] **F5.2** `tokens.css` — §10.2'deki tüm tasarım tokenlarını tanımla; `base.css` reset ve tipografi
- [ ] **F5.3** Fontları self-host et (Space Grotesk, Inter — latin + latin-ext subset, woff2)
- [ ] **F5.4** `api/client.ts`: Axios instance, token interceptor, hata zarfı dönüşümü, tek seferlik retry
- [ ] **F5.5** `openapi.yaml`'dan TypeScript tip üretimi (`npm run gen:types`)
- [ ] **F5.6** Router ve rota korumaları (§9.1)
- [ ] **F5.7** `components/base/` temel komponentleri: `BaseButton`, `BaseCard`, `BaseBadge`, `BaseInput`, `BaseSpinner`, `BaseTabs`, `EmptyState`, `ErrorState`

### Milestone 6 — Oyun akışı (Frontend)

- [ ] **F6.1** `useQuizStore` — §9.2'deki durum makinesi, `sessionStorage` kalıcılığı (try/catch ile)
- [ ] **F6.2** `useCountdown` — `requestAnimationFrame` tabanlı, saat sapması düzeltmeli, `visibilitychange` hizalamalı sayaç
- [ ] **F6.3** `HomeView` + `CategoryCard` — kategori listesi, oynanamaz kategori durumu
- [ ] **F6.4** `CountdownView` — 3-2-1 animasyonu, arka planda oturum oluşturma ve ilk soruyu önden yükleme
- [ ] **F6.5** `CountdownRing` — SVG dairesel progress, renk eşikleri, son 2 sn pulse
- [ ] **F6.6** `QuestionCard` + `OptionButton` — 4 durum, klavye kısayolları (A-D / 1-4), çift tıklama koruması
- [ ] **F6.7** `QuizView` — soru akışı, cevap gönderme, `FeedbackOverlay`, `ScorePopup`, 1.2 sn sonra otomatik geçiş
- [ ] **F6.8** Hata ve kopma yönetimi: "Bağlantı koptu" ekranı, `current-question` ile senkronizasyon, `410`/`401` durumunda ana sayfaya dönüş
- [ ] **F6.9** `onBeforeRouteLeave` çıkış onayı
- [ ] **F6.10** Testler: `useCountdown` birim testleri, store geçiş testleri

### Milestone 7 — Sonuç ve skor tablosu (Frontend)

- [ ] **F7.1** `ResultView` — `ScoreCounter` sayma animasyonu, `StatTile` dağılımı, performans başlığı, `estimated_rank` gösterimi
- [ ] **F7.2** `NicknameView` — doğrulama, sunucu hata mesajlarının gösterimi, "kaydetmeden geç"
- [ ] **F7.3** `LeaderboardView` + `LeaderboardTable` + `LeaderboardRow` + `RankMedal` — sekmeler, kullanıcı satırının vurgulanması, ilk 10 dışındaki kullanıcının ayrı satırda gösterimi
- [ ] **F7.4** Boş ve hata durumları

### Milestone 8 — Cila ve yayın

- [ ] **P8.1** Tüm animasyonların uygulanması (§10.5) ve `prefers-reduced-motion` kontrolü
- [ ] **P8.2** Erişilebilirlik geçişi: klavye navigasyonu, odak halkaları, `aria-live`, kontrast doğrulaması (§9.5)
- [ ] **P8.3** Responsive kontrol: 360px, 768px, 1440px genişliklerde quiz ekranının kaydırmasız sığması
- [ ] **P8.4** Lighthouse ve bundle boyutu optimizasyonu (§9.6 hedefleri)
- [ ] **P8.5** E2E senaryolarının tamamı (§13.2)
- [ ] **P8.6** Kategori başına soru havuzunu 40'a çıkar, tüm soruların doğruluğunu kontrol et

### Milestone 9 — DigitalOcean deployment

- [x] **D9.1** `config/settings/production.py`: §14.4'teki tüm güvenlik ve TLS ayarları, `SECURE_PROXY_SSL_HEADER`, whitenoise manifest storage
- [x] **D9.2** `django-ipware` entegrasyonu ve `X-Forwarded-For` çözümlemesi + testi (§14.4 — throttling'in doğru çalışması buna bağlı)
- [x] **D9.3** `CACHES` ayarını koşullu yaz: `REDIS_URL` varsa Redis, yoksa LocMem (§14.7)
- [ ] **D9.4** Backend `.do/app.yaml` yaz: service, `PRE_DEPLOY` migrate job'ı, `SCHEDULED` cleanup job'ı, managed PG database bloğu, health check, alerts (§14.5)
- [ ] **D9.5** `doctl` ile staging App'i oluştur; Dev Database bağla; deploy'un uçtan uca geçtiğini ve `/api/v1/health/` health check'inin yeşil olduğunu doğrula
- [ ] **D9.6** Staging'de `seed_questions`'ı `doctl apps console` ile bir kez çalıştır ve kategori endpoint'inin `is_playable: true` döndüğünü doğrula
- [ ] **D9.7** Frontend `.do/app.yaml` yaz: static site, `build_command`, `output_dir: dist`, **`catchall_document: index.html`**, `VITE_API_BASE_URL` (`BUILD_TIME` scope) (§14.6)
- [ ] **D9.8** Frontend staging static site'ını oluştur; derin bir yola (`/skorlar`) doğrudan girildiğinde 404 almadığını doğrula
- [ ] **D9.9** Domain'leri bağla (`rapidquiz.app`, `api.rapidquiz.app`), TLS sertifikalarının otomatik geldiğini doğrula, `ALLOWED_HOSTS` ve `CORS_ALLOWED_ORIGINS`'i son haline getir
- [ ] **D9.10** Tarayıcıdan gerçek bir CORS akışı test et: frontend domain'inden `POST /quiz-sessions/` çağrısının preflight dahil geçtiğini doğrula
- [ ] **D9.11** GitHub Actions kalite kapılarını yaz (§14.9) — backend'de `docker build` adımı dahil
- [ ] **D9.12** Production App'lerini oluştur: Managed PostgreSQL kümesi, Trusted Sources'ta yalnızca API App'i, public erişim kapalı, `instance_count: 2`
- [ ] **D9.13** Sentry ve dashboard uyarılarını kur (§14.10); `POST /answers/` p99 yanıt süresi için ayrı izleme ekle
- [ ] **D9.14** Rollback ve yedekten dönüş prosedürünü bir kez uçtan uca test et, `README.md`'ye yaz
- [ ] **D9.15** Staging'de tam manuel oyun turu, ardından production deploy

### Önerilen sıra

```
B0 → B1 → B2 → B3 → B4 ─┬─→ F5 → F6 → F7 → P8 → D9
                         │
     (F5 backend'in B4'ünü beklemeden mock API ile paralel başlayabilir)

     D9.1–D9.6 (backend deploy) B3 biter bitmez başlatılabilir — frontend'i beklemez.
     Staging'in erken ayağa kalkması, frontend'in gerçek API'ye karşı geliştirilmesini sağlar.
```

**Paralel çalışma notu:** Frontend, `openapi.yaml` hazır olmadan mock veriyle (MSW veya statik JSON) ilerleyebilir. Sözleşme §7'de yazılı olduğu için mock'lar gerçek API ile uyumlu kurulabilir.

---

## 16. Kararlar ve Açık Konular

### 16.1 Alınmış kararlar

| # | Karar | Gerekçe |
|---|---|---|
| D1 | Süre ve puan tamamen sunucuda hesaplanır | İstemci manipülasyonu skor tablosunu anlamsızlaştırır |
| D2 | Sonraki soru, cevap yanıtına gömülür | Soru geçişinde ek ağ gecikmesi olmaması için — 5 sn'lik oyunda kritik |
| D3 | Oturum başında 20 soru sabitlenir | Yenileme/geri gelme durumunda tutarlılık ve tekrarsızlık |
| D4 | 800 ms grace period | Yavaş bağlantının haksız ceza vermemesi; avantaj sağlamaması için süre kırpılır |
| D5 | Çerez yerine `X-Session-Token` başlığı | Mobil istemci uyumluluğu ve CSRF karmaşıklığının ortadan kalkması |
| D6 | `sessionStorage` (localStorage değil) | Sekme kapanınca oturumun düşmesi beklenen davranış |
| D7 | Takma adda benzersizlik aranmaz | Kayıt yok; benzersizlik zorlamak kullanıcıyı gereksiz yere engeller |
| D8 | Zorluk seviyesi modellenir ama v1.0'da kullanılmaz | İleride migration gerektirmemesi için baştan alan açılır |
| D9 | Koyu tema v1.0'da yok | Ürün yönü aydınlık ve canlı; iki tema bakımı erken maliyet |
| D10 | Celery kurulmaz | Tek zamanlı iş var (stale session temizliği); cron + management command yeterli |
| D11 | Takma adda küfür filtresi yok | Basitlik; uygunsuz kayıtlar admin'den silinir |
| D12 | Ses efekti yok | v1.0 kapsamı dışı |
| D13 | Stil: CSS değişkenleri + scoped CSS (Tailwind yok) | Tasarım sistemi zaten token tabanlı, bağımlılık azalır |
| D14 | Deployment: DigitalOcean App Platform | §14'te detaylandırıldı |
| D15 | Süre istatistikleri: `total_elapsed_ms`'de timeout = 5000 ms; `average_elapsed_ms` yalnızca cevaplanan sorulardan (yanlış dahil, timeout hariç) | Beraberlik bozucu adil kalsın: süreyi tüketen hızlı sayılmasın |

### 16.2 Açık konular — karar bekliyor

| # | Konu | Seçenekler | Öneri |
|---|---|---|---|
| Q2 | Mobil framework | React Native, Flutter, Capacitor (mevcut Vue'yu sarmalama) | **Capacitor**, hızlı bir v1.1 için en ucuz yol; ayrı bir native deneyim isteniyorsa Flutter |
| Q3 | Soru havuzunun üretimi | Elle yazma, LLM ile üretip insan doğrulaması | LLM ile taslak + **mutlaka insan doğrulaması**. Doğrulanmamış soru havuza girmez |
| Q4 | Skor tablosu dönemi | Yalnızca `all`, veya haftalık/aylık | v1.0'da `all`; `period` parametresi API'de hazır bırakılır |
| Q7 | Domain ve marka adı | `rapidquiz.app` vb. | Ürün adı **Rapid Quiz** olarak sabitlendi; domain kontrolü yapılmalı |

### 16.3 Bilinen riskler

| Risk | Etki | Azaltma |
|---|---|---|
| Ağ gecikmesi 5 sn'lik deneyimi bozar | Yüksek | Sonraki sorunun önden gelmesi (D2) + grace period (D4) + yavaş bağlantıda net geri bildirim |
| Soru havuzunun küçüklüğü tekrara yol açar | Orta | Kategori başına hedef 40+ soru; havuz büyüdükçe tekrar düşer |
| Anonim skor tablosu bot saldırısına açık | Orta | Throttling + sunucu otoriteli puan + gerekirse v1.1'de hCaptcha/Turnstile |
| Uygunsuz takma adlar | Orta | Sunucu filtresi + admin'den silme yetkisi |
| Soru içeriğinde hata | Orta | Yayın öncesi doğruluk kontrolü; kullanıcıdan "soruyu bildir" v1.2'de |

---

## Ek A — Terimler

| Terim | Anlam |
|---|---|
| **Oturum (session)** | Bir kullanıcının tek bir kategoride oynadığı 20 soruluk tur |
| **Grace period** | Ağ gecikmesini telafi eden, 5 saniyenin üstüne eklenen 800 ms'lik tolerans |
| **Outcome** | Bir sorunun sonucu: `correct`, `wrong`, `timeout`, `pending` |
| **Hız bonusu** | Doğru cevapta kalan süreye göre verilen 0–100 arası ek puan |
| **Slug** | Kategorinin URL ve API'de kullanılan kimliği (`yapay-zeka`) |
| **Token** | Oturumu yetkilendiren, `X-Session-Token` başlığında taşınan rastgele dize |

---

*Bu doküman projenin tek referans kaynağıdır. Mimari veya sözleşme değişikliklerinde önce bu doküman güncellenir, sonra kod yazılır.*



