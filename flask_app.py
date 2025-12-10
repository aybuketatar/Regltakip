from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cok-gizli-anahtar'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///regl_takip.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'giris_yap'

# Rastgele Günlük Tavsiyeler
TAVSIYELER = [
    "Bol su içmek şişkinliği azaltmaya yardımcı olur. 💧",
    "Magnezyum (muz, kakao) kramplara iyi gelir. 🍌",
    "Hafif yürüyüşler yapmak ağrıyı hafifletir. 🚶‍♀️",
    "Kafein tüketimini azaltmak gerginliği önler. ☕",
    "Sıcak su torbası en iyi arkadaşındır! 🔥",
    "C vitamini demir emilimini artırır. 🍊"
]

@login_manager.user_loader
def load_user(user_id):
    return Kullanici.query.get(int(user_id))

class Kullanici(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(100))
    kullanici_adi = db.Column(db.String(100), unique=True)
    sifre = db.Column(db.String(100))
    ilac_kullaniyor_mu = db.Column(db.String(10))
    ilac_ismi = db.Column(db.String(100), nullable=True)
    regl_duzeni = db.Column(db.String(20))
    son_regl_tarihi = db.Column(db.String(20))
    dongu_suresi = db.Column(db.Integer)
    quiz_puani = db.Column(db.Integer, default=0)

# --- YENİ QUIZ: YAŞAM TARZI ANALİZİ ---
# Not: 'puan_degeri' şıkkın ne kadar sağlıklı olduğunu gösterir.
QUIZ_SORULARI = [
    {
        "soru": "Regl döneminde ağrı şiddetin genelde nasıldır?",
        "siklar": ["A) Hiç ağrım olmaz", "B) Hafif, ilaçsız geçerim", "C) Orta, bazen ilaç alırım", "D) Çok şiddetli, yataktan çıkamam"],
        "ideal_cevap": "B) Hafif, ilaçsız geçerim" # İdeal durum referansı (Puanlama için basit mantık: Eşleşirse tam puan)
    },
    {
        "soru": "Günde ortalama ne kadar su içiyorsun?",
        "siklar": ["A) Neredeyse hiç", "B) 1 Litre kadar", "C) 2-3 Litre", "D) Sadece çay/kahve"],
        "ideal_cevap": "C) 2-3 Litre"
    },
    {
        "soru": "Uyku düzenin nasıldır?",
        "siklar": ["A) Çok düzensiz, az uyurum", "B) 6 saatten az", "C) 7-8 saat düzenli", "D) Sürekli uyumak istiyorum"],
        "ideal_cevap": "C) 7-8 saat düzenli"
    },
    {
        "soru": "Regl öncesi (PMS) ruh halin nasıl değişir?",
        "siklar": ["A) Değişim hissetmem", "B) Biraz hassaslaşırım", "C) Çok sinirli olurum", "D) Depresif hissederim"],
        "ideal_cevap": "A) Değişim hissetmem"
    },
    {
        "soru": "Egzersiz yapıyor musun?",
        "siklar": ["A) Hiç yapmam", "B) Haftada 1-2 kez", "C) Düzenli spor yaparım", "D) Sadece yürüyüş"],
        "ideal_cevap": "C) Düzenli spor yaparım"
    },
    {
        "soru": "Beslenme düzenin nasıldır?",
        "siklar": ["A) Çok fast-food yerim", "B) Dengeli beslenirim", "C) Sürekli tatlı yerim", "D) Öğün atlarım"],
        "ideal_cevap": "B) Dengeli beslenirim"
    },
    {
        "soru": "Stres seviyen gün içinde nasıldır?",
        "siklar": ["A) Çok sakin", "B) Ara sıra stresli", "C) Genelde stresli", "D) Çok yoğun stresli"],
        "ideal_cevap": "A) Çok sakin"
    }
]

@app.route('/')
def ana_sayfa():
    if current_user.is_authenticated:
        return redirect(url_for('panel'))
    return render_template('giris.html')

@app.route('/kayit', methods=['POST'])
def kayit_ol():
    yeni_kullanici = Kullanici(
        isim=request.form.get('isim'),
        kullanici_adi=request.form.get('kullanici_adi'),
        sifre=request.form.get('sifre'),
        ilac_kullaniyor_mu=request.form.get('ilacDurumu'),
        ilac_ismi=request.form.get('ilacIsmi'),
        regl_duzeni=request.form.get('duzen'),
        son_regl_tarihi=request.form.get('sonTarih'),
        dongu_suresi=int(request.form.get('donguSuresi'))
    )
    db.session.add(yeni_kullanici)
    db.session.commit()
    login_user(yeni_kullanici)
    return redirect(url_for('panel'))

@app.route('/giris', methods=['POST'])
def giris_yap():
    user = Kullanici.query.filter_by(kullanici_adi=request.form.get('giris_kadi')).first()
    if user and user.sifre == request.form.get('giris_sifre'):
        login_user(user)
        return redirect(url_for('panel'))
    return "Hatalı giriş"

@app.route('/panel')
@login_required
def panel():
    # Günlük Tavsiye Seç
    gunun_tavsiyesi = random.choice(TAVSIYELER)
    
    # Kişiye Özel Notlar
    ozel_notlar = []
    if current_user.regl_duzeni == "duzensiz":
        ozel_notlar.append("⚠️ Reglin düzensiz olduğu için takvim takibi çok önemli.")
    if current_user.ilac_kullaniyor_mu == "evet":
        ozel_notlar.append(f"💊 '{current_user.ilac_ismi}' ilacını almayı unutma.")
    
    # Quiz Sonucuna Göre Yorum
    quiz_yorum = ""
    if current_user.quiz_puani > 0:
        if current_user.quiz_puani >= 80:
            quiz_yorum = "Harika! Yaşam tarzın döngünle çok uyumlu. 🌟"
        elif current_user.quiz_puani >= 50:
            quiz_yorum = "İyi gidiyorsun ama biraz daha dikkat edebilirsin. 👍"
        else:
            quiz_yorum = "Vücudun sinyal veriyor, kendine daha iyi bakmalısın. 🆘"

    return render_template('dashboard.html', user=current_user, tavsiye=gunun_tavsiyesi, notlar=ozel_notlar, quiz_yorum=quiz_yorum)

@app.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    if request.method == 'POST':
        puan = 0
        soru_sayisi = len(QUIZ_SORULARI)
        
        # Puanlama Mantığı: İdeal cevabı seçtiyse puan ver
        for i, soru in enumerate(QUIZ_SORULARI):
            cevap = request.form.get(f'soru_{i}')
            # Basit puanlama: İdeal cevapla eşleşirse tam puan
            # (Daha gelişmiş mantıkta her şıkka ayrı puan verilebilir)
            if cevap == soru['ideal_cevap']:
                puan += 1
        
        # 100 üzerinden hesapla
        final_puan = int((puan / soru_sayisi) * 100)
        
        current_user.quiz_puani = final_puan
        db.session.commit() # Veritabanına kaydet
        return redirect(url_for('panel'))
        
    return render_template('quiz.html', sorular=QUIZ_SORULARI)

@app.route('/cikis')
@login_required
def cikis():
    logout_user()
    return redirect(url_for('ana_sayfa'))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)