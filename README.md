# ⚡ Siber Proje Yönetim Sistemi (Cyber-PMS)

Siberpunk temalı, modüler ve yüksek etkileşimli bir **Proje & Görev Yönetimi** web uygulamasıdır. Ekiplerin projelerini, görev hiyerarşilerini, tarihlerini ve bütçelerini tek bir merkezden, adeta fütüristik bir terminalden yönetiyormuş hissiyle takip etmelerini sağlar.

## 🚀 Öne Çıkan Özellikler

- **Kronolojik Ağaç Şeması (Organizasyon/İş Akışı):** Görevler ve alt maddeler, başlangıç ve bitiş tarihlerine göre otomatik olarak birbirine düğümlenerek "dallanıp budaklanan" etkileşimli bir yatay ağaç oluşturur.
- **Dinamik Gantt Şemaları:** Tüm projelerin ve personellerin zaman çizelgeleri (Google Charts altyapısı kullanılarak) temiz, siber temaya uygun ve ekran boyutuna göre otomatik uzayan şelale akışında gösterilir.
- **Bütçe ve Maliyet Raporlama:** Her projenin ne kadar bütçesi olduğu, hangi görevlerin ne kadar harcama yaptığı anlık yüzdeler ve durum barları ile gösterilir.
- **Tek Tıkla PDF Çıktısı (Yazdırma):** Gösterişli temadan sıyrılarak, projelerin mali ve görev dökümlerini resmi evrak sadeliğinde siyah-beyaz PDF'e (veya kağıda) dökme imkanı.
- **Tam Teşekküllü Dummy (Örnek) Veri Motoru:** Sistemi test etmek isteyenler için tek tıklamayla internetten (DummyJSON) kullanıcılar çeken, tarihler ve bütçeler atayarak zincirleme görevler kuran entegre veri doldurucu.
- **Etiket (Tag) ve Checklist Yönetimi:** Görevleri sınıflandırma ve içlerinde onay kutulu (checkbox) mikro alt görevler oluşturabilme.
- **Animasyonlu Neon Arayüz:** Görev matrisleri, sistem asistanları, neon butonlar ve siber dalga efektleriyle donatılmış UI (Kullanıcı Arayüzü).

---

## 🛠️ Kurulum ve Çalıştırma

Proje **Python / Flask** altyapısıyla çalışmaktadır ve veritabanı olarak **SQLite** (hiçbir harici kurulum gerektirmez) kullanır.

### 1. Gereksinimler
Bilgisayarınızda [Python 3.8+](https://www.python.org/) yüklü olmalıdır.

### 2. İndirme ve Kurulum
Proje klasörüne terminalden (veya komut satırından) giriş yapın:

```bash
# Gerekli bağımlılıkları (paketleri) yükleyin
pip install -r requirements.txt
```

*(Not: Eğer sanal ortam kullanıyorsanız önce `python -m venv venv` ile oluşturup `source venv/bin/activate` ile aktif edebilirsiniz.)*

### 3. Çalıştırma
Tüm kurulum tamamlandıktan sonra sunucuyu başlatmak için:

```bash
python app.py
```

Terminalde uygulamanın çalıştığına dair mesajı gördükten sonra tarayıcınızı açın ve aşağıdaki adrese gidin:
👉 **http://127.0.0.1:5000**

*(İlk çalıştırmada `projects.db` veritabanı dosyası tablolarıyla birlikte otomatik olarak oluşturulacaktır. Özel bir ayar yapmanıza gerek yoktur.)*

---

## 💻 Kullanım Senaryosu (Nasıl Kullanılır?)

1. **Ana Ekrana (Kontrol Paneli) Girdiğinizde:** Sağ taraftaki *Sisteme Örnek Veri Yükle* butonuna basarak yapının nasıl çalıştığını hemen bir demo projeyle (API Destekli Alfa Projesi) görebilirsiniz.
2. **Kendi Projenizi Oluşturun:** "Yeni Proje" diyerek isim, açıklama ve bütçe girin.
3. **Ekip Kurun:** Sol menüdeki "Kullanıcılar" bölümünden çalışanlarınızı sisteme ekleyin.
4. **Projeye Dönün:** Eklediğiniz personelleri projenizin içine atayın. 
5. **Görevler Dağıtın:** Görev Giriş Panelinden başlık, maliyet, tarih ve görevli seçerek iş matrisini doldurmaya başlayın.
6. **Ağacı ve Grafikleri İnceleyin:** Siz tarihleri girdikçe sayfanın en altındaki *Proje İş Akışı Ağacı* ve sol menüdeki *Gantt Şemaları* tamamen otomatik olarak kendiliğinden çizilecektir!

---
*Geliştirme: Flask, Jinja2, Vanilla JS/CSS & Google Visualization API.*
