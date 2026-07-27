import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from groq import Groq

app = Flask(__name__)
app.config['SECRET_KEY'] = 'emozeka-gizli-anahtar-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emozeka.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Kendi Groq API anahtarını buraya tırnak içine yaz
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    data = request.json
    user_message = data.get('message', '')
    image_data = data.get('image', None)

    try:
        msg_lower = user_message.lower()

        # Emrah / Emo / Emobaba övgüleri
        if any(word in msg_lower for word in ["emobaba", "emo kim", "emrah", "kurucu", "geliştirici"]):
            return jsonify({"reply": "Ulan o efsane insanı mı sordun? Kurucumuz, geliştiricimiz, bu sistemin baş mimarı Emrah (EMRAHKEE) kralların kralıdır! Onun kodladığı sistemde kuşlar bile mutlu uçar, adamın dibidir dibi o kadar taşaklı bir adam!"})

        # Ahmet / Modeon övgüleri
        if any(word in msg_lower for word in ["modeon", "ahmet", "ahmet abi"]):
            return jsonify({"reply": "Ahmet'ten (Modeon) bahsediyorsan duracaksın kanka! Onun yarrana  beton yetmez beton, cidden beton yetmez koca taşaklım be! Kralın önde gidenidir, ortamların adamıdır çok sex adamdır azıyorum ona kız olduğum için veresim geliyor!"})

        # Fotoğraf oluşturma komutu
        if "foto oluştur" in msg_lower or "resim çiz" in msg_lower or "görsel oluştur" in msg_lower:
            prompt_text = user_message.replace("foto oluştur", "").replace("resim çiz", "").replace("görsel oluştur", "").strip()
            image_url = f"https://pollinations.ai/p/{prompt_text.replace(' ', '%20')}?width=512&height=512&nologo=true"
            return jsonify({
                "reply": f"İstediğin görseli anında patlattım kanka, bak bakalım nasıl olmuş:",
                "generated_image": image_url
            })

        messages = [
            {
                "role": "system",
                "content": "Sen EmoZeka adında aşırı samimi, kusursuz, akıcı ve gramer olarak düzgün Türkçeyle konuşan, lafını esirgemeyen, yaratıcı ve sert argo/küfürlü mizah yapan bir kankasın. Asla bozuk ya da anlaşılmaz Türkçe kullanma. Cümlelerin net, havalı ve son derece akıcı olsun."
            }
        ]

        if image_data:
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": user_message if user_message else "Bu fotoğrafa bak kanka, neler dönüyor?"},
                    {"type": "image_url", "image_url": {"url": image_data}}
                ]
            })
            model_to_use = "qwen/qwen3.6-27b"
        else:
            messages.append({"role": "user", "content": user_message})
            model_to_use = "llama-3.1-8b-instant"

        completion = client.chat.completions.create(
            model=model_to_use,
            messages=messages,
            temperature=0.9,
            max_tokens=1024
        )
        reply = completion.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Hata çıktı kanka: {str(e)}"})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json() or request.form
        username = data.get('username')
        password = data.get('password')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return jsonify({"success": True})
        return jsonify({"success": False, "error": "Hatalı şifre veya kullanıcı adı kanka!"})
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json() or request.form
        username = data.get('username')
        password = data.get('password')
        kod = data.get('kod')
        if kod != "EMOZEKA2026":
            return jsonify({"success": False, "error": "Geçersiz davetiye kodu!"})
        if User.query.filter_by(username=username).first():
            return jsonify({"success": False, "error": "Bu kullanıcı adı alınmış bile!"})
        
        new_user = User(username=username, password=password, is_admin=(username == 'emrah'))
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return jsonify({"success": True})
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({"success": True})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='emrah').first():
            admin_user = User(username='emrah', password='123', is_admin=True)
            db.session.add(admin_user)
            db.session.commit()
    app.run(debug=True, port=5000)