from flask import Flask, render_template
import random

app = Flask(__name__)

tavsiyeler = [
    "Bol su içmek şişkinliği azaltmaya yardımcı olabilir. 💧",
    "Magnezyum içeren besinler (muz, bitter çikolata) kramplara iyi gelir. 🍌",
    "Hafif yürüyüşler yapmak ağrılarını hafifletebilir. 🚶‍♀️",
    "Sıcak su torbası en yakın arkadaşın olabilir! 🔥",
    "Kafein tüketimini azaltmak gerginliği önleyebilir. ☕",
    "C vitamini demir emilimini artırır, portakal yiyebilirsin. 🍊"
]

@app.route('/')
def ana_sayfa():
    secilen_tavsiye = random.choice(tavsiyeler)
    return render_template('index.html', tavsiye=secilen_tavsiye)

if __name__ == '__main__':
    app.run(debug=True)

