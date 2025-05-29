# 🎬 FilmReel - Film Öneri Sistemi

FilmReel, yapay zeka destekli bir film öneri sistemidir. Kullanıcıların beğendiği filmlere benzer içerik tabanlı öneriler sunarak, kişiselleştirilmiş film keşfi deneyimi sağlar.

## 🌟 Özellikler

- İçerik tabanlı film önerileri
- TMDB API entegrasyonu ile film detayları
- Türkçe film özetleri
- Kullanıcı dostu arayüz
- Gerçek zamanlı öneriler

## 🚀 Kurulum

1. Projeyi klonlayın:
```bash
git clone https://github.com/yourusername/FilmReel.git
cd FilmReel
```

2. Sanal ortam oluşturun ve aktifleştirin:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
.\venv\Scripts\activate  # Windows
```

3. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

4. TMDB API anahtarınızı ayarlayın:
- `.env` dosyası oluşturun
- İçine `TMDB_TOKEN=your_api_key` ekleyin

## 💻 Kullanım

1. Uygulamayı başlatın:
```bash
cd app
streamlit run app.py
```

2. Tarayıcınızda `http://localhost:8501` adresine gidin
3. Beğendiğiniz bir filmi seçin
4. "Önerileri Göster" butonuna tıklayın
5. Size önerilen 5 benzer filmi görüntüleyin

## 📁 Proje Yapısı

```
FilmReel/
├── app/
│   └── app.py              # Streamlit web uygulaması
├── src/
│   ├── data_loader.py      # Veri yükleme işlemleri
│   ├── preprocessor.py     # Veri ön işleme
│   └── recommender.py      # Öneri sistemi
├── data/
│   ├── tmdb_5000_movies.csv    # Film verileri
│   └── tmdb_5000_credits.csv   # Kredi verileri
├── requirements.txt        # Proje bağımlılıkları
└── README.md              # Proje dokümantasyonu
```

## 🛠️ Teknolojiler

- Python 3.12
- Streamlit
- scikit-learn
- pandas
- numpy
- TMDB API
- Google Translate API

## 📊 Algoritma

FilmReel, içerik tabanlı filtreleme yaklaşımını kullanır:

1. Film özetlerinden TF-IDF vektörleri oluşturulur
2. Kosinüs benzerliği hesaplanır
3. En benzer 5 film önerilir

## 🤝 Katkıda Bulunma

1. Bu depoyu fork edin
2. Yeni bir özellik dalı oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Dalınıza push edin (`git push origin feature/amazing-feature`)
5. Bir Pull Request açın

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 📧 İletişim

Emre Almaoğlu - [@emrealmaoglu](https://github.com/emrealmaoglu)

Proje Linki: [https://github.com/emrealmaoglu/FilmReel](https://github.com/emrealmaoglu/FilmReel)

## Güvenlik Kurulumu

### 1. Ortam Değişkenleri

1. `.env.example` dosyasını `.env` olarak kopyalayın:
   ```bash
   cp .env.example .env
   ```

2. `.env` dosyasındaki değerleri kendi yapılandırmanızla güncelleyin:
   - `TMDB_API_KEY`: TMDB API anahtarınız
   - `DEBUG`: Hata ayıklama modu (True/False)
   - `LOG_LEVEL`: Günlük kayıt seviyesi (INFO/DEBUG/WARNING/ERROR)

### 2. Güvenlik Önlemleri

- `.env` dosyasını asla git deposuna eklemeyin
- API anahtarlarını düzenli olarak değiştirin
- Üretim ortamında farklı API anahtarları kullanın
- Hassas bilgileri kod içinde saklamayın
- Tüm API isteklerini HTTPS üzerinden yapın

### 3. Hata Ayıklama

Hata ayıklama modunu etkinleştirmek için:
```bash
export DEBUG=True
```

## Kullanım

1. Ana sayfada beğendiğiniz bir filmi seçin
2. Sistem size benzer 5 film önerecektir
3. Her film için detaylı bilgi ve özet görüntüleyebilirsiniz

## Güvenlik İpuçları

1. API Anahtarı Yönetimi:
   - API anahtarlarını düzenli olarak değiştirin
   - Farklı ortamlar için farklı anahtarlar kullanın
   - Anahtarları güvenli bir şekilde saklayın

2. Hata Yönetimi:
   - Tüm hataları uygun şekilde yakalayın
   - Hassas bilgileri loglarda göstermeyin
   - Kullanıcı dostu hata mesajları kullanın

3. Veri Güvenliği:
   - Tüm API isteklerini HTTPS üzerinden yapın
   - Kullanıcı verilerini güvenli bir şekilde saklayın
   - Düzenli güvenlik denetimleri yapın 