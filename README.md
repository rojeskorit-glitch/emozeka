# Emozeka — Herkesin Kullanabileceği AI Sitesi

Bu proje Vercel üzerinde çalışır.
API anahtarı tarayıcıda görünmez, sadece senin Vercel hesabında durur.

## Kurulum (5 dakika)

### 1. Groq API Key al
1. https://console.groq.com adresine git
2. Ücretsiz kayıt ol
3. API Keys → Create API Key
4. Key'i kopyala (bir daha kimseyle paylaşma)

> Eski key'i buraya yazdıysan mutlaka sil ve yenisini oluştur.

### 2. Vercel'e yükle

**Yöntem A — Sürükle bırak (en kolay)**
1. https://vercel.com → ücretsiz kayıt ol (GitHub ile)
2. Dashboard → Add New → Project
3. "Deploy" yerine klasörü sürükleyebilirsin veya GitHub'a atıp bağla

**Yöntem B — GitHub ile (önerilen)**
1. Bu klasörü GitHub'a yükle (yeni repo)
2. vercel.com → New Project → GitHub reposunu seç
3. Deploy'a bas

### 3. API Key'i Vercel'e ekle
1. Vercel projen → Settings → Environment Variables
2. Name: `GROQ_API_KEY`
3. Value: senin Groq key'in
4. Save
5. Redeploy (Deployments → son deployment → Redeploy)

### 4. Site hazır
Vercel sana bir link verir:
`https://emozeka-xxxx.vercel.app`

Bu linki herkes kullanabilir. Key kimseye görünmez.

## Dosya yapısı

```
emozeka-site/
├── api/
│   └── chat.js      ← Backend (Groq'a istek atar)
├── index.html       ← Sohbet arayüzü
└── README.md
```

## Önemli notlar
- Groq ücretsiz kotası sınırlıdır. Çok kişi kullanırsa kota bitebilir.
- İstersen rate limit ekleyebilirsin.
- Domain bağlamak istersen Vercel → Domains.
