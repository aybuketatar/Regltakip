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

    gunun_tavsiyesi = random.choice(TAVSIYELER)
    ozel_notlar = []
    if current_user.regl_duzeni == "duzensiz":
        ozel_notlar.append("⚠️ Reglin düzensiz olduğu için takvim takibi çok önemli.")
    if current_user.ilac_kullaniyor_mu == "evet":
        ozel_notlar.append(f"💊 '{current_user.ilac_ismi}' ilacını almayı unutma.")

@app.route('/cikis')
@login_required
def cikis():
    logout_user()
    return redirect(url_for('ana_sayfa'))

with app.app_context():
    db.create_all()

if __name__ == '__main__':

    app.run(debug=True)
