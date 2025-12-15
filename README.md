# 🐦 X.com Tweet Bot - Vercel Edition

Otomatik söz paylaşan X.com (Twitter) botu. Vercel serverless functions + cron job ile çalışır.

## 🚀 Hızlı Kurulum

### 1. GitHub'a Yükle
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/KULLANICI/x-tweet-bot.git
git push -u origin main
```

### 2. Vercel'e Deploy
1. [vercel.com](https://vercel.com)'a git
2. "New Project" → GitHub reposunu seç
3. Deploy et

### 3. Environment Variables Ekle
Vercel Dashboard → Project → Settings → Environment Variables:

| Key | Value |
|-----|-------|
| `AUTH_TOKEN` | X.com'dan aldığın auth_token cookie |
| `CT0` | X.com'dan aldığın ct0 cookie |

### 4. Cron Job
`vercel.json`'da ayarlı: **Her saat başı** tweet atar.

Değiştirmek için `vercel.json` → `crons` → `schedule`:
- `"0 */1 * * *"` = Her saat
- `"0 */2 * * *"` = Her 2 saat
- `"0 9,12,18,21 * * *"` = 09:00, 12:00, 18:00, 21:00

---

## 📁 Dosya Yapısı

```
x-tweet-bot/
├── api/
│   ├── tweet.py     # Tweet endpoint (cron çağırır)
│   └── health.py    # Health check
├── quotes.json      # Sözler (SEN DÜZENLE!)
├── tweeter.py       # Tweet modülü
├── vercel.json      # Vercel config + cron
└── requirements.txt
```

---

## 📝 Sözleri Düzenleme

`quotes.json` dosyasını düzenle:
```json
{
  "quotes": [
    {"text": "Söz metni buraya", "author": "Yazar"},
    {"text": "Başka bir söz", "author": "Başka Yazar"}
  ]
}
```

---

## 🔗 Endpoints

| Endpoint | Açıklama |
|----------|----------|
| `GET /` | Health check |
| `GET /api/health` | Health check |
| `GET /api/tweet` | Random söz seçip tweet at |

---

## ⚠️ Notlar

- **Cron Job**: Vercel Pro/Enterprise için günde 1 kez, Hobby için günde 2 kez çalışır (free tier limiti)
- **Cookie Süresi**: Cookie'ler birkaç ay geçerli kalır, expire olursa yenile
- **Test**: Deploy sonrası `/api/tweet` endpoint'ini manuel çağırarak test et
