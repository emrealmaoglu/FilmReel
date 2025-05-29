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