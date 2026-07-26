import os
from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from openai import OpenAI

app = Flask(__name__, template_folder=".")
app.config["SECRET_KEY"] = "emozeka-gizli-anahtar-123"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///emozeka.db"

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.view_func = "login"

# Groq API Entegrasyonu (Ücretsiz ve Hızlı)
client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Kullanıcı Veritabanı Modeli
class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(150), unique=True, nullable=False)
  password = db.Column(db.String(150), nullable=False)


@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))


with app.app_context():
  db.create_all()


# Sayfa Rotaları
@app.route("/")
def index():
  if current_user.is_authenticated:
    return redirect(url_for("chat_page"))
  return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
  if request.method == "POST":
    username = request.form.get("username")
    password = request.form.get("password")
    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
      login_user(user)
      return redirect(url_for("chat_page"))
    return render_template("login.html", error="Hatalı kullanıcı adı veya şifre!")
  return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
  if request.method == "POST":
    username = request.form.get("username")
    password = request.form.get("password")
    if User.query.filter_by(username=username).first():
      return render_template(
          "register.html", error="Bu kullanıcı adı zaten alınmış!"
      )
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)
    return redirect(url_for("chat_page"))
  return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
  logout_user()
  return redirect(url_for("login"))


@app.route("/chat")
@login_required
def chat_page():
  return render_template("index.html", username=current_user.username)


# Yapay Zeka Mesajlaşma ve Mod Yönetimi API Rotaları
@app.route("/chat-api", methods=["POST"])
@login_required
def emozeka_chat():
  data = request.get_json()
  user_message = data.get("message", "")
  mode = data.get("mode", "sohbet")

  if not user_message:
    return jsonify({"error": "Lütfen bir mesaj gönderin."}), 400

  # Modlara göre yapay zekaya verilecek karakter talimatları (System Prompts)
  prompts = {
      "sohbet": (
          "Sen EmoZeka adlı empatik, duygu analizi yapabilen ve kullanıcıya"
          " destek olan samimi bir sohbet asistanısın."
      ),
      "soru": (
          "Sen uzman bir öğretmen ve koçsun. Kullanıcının sorduğu akademik"
          " soruları veya problemleri adım adım, açıklayıcı ve öğretici bir"
          " şekilde çöz."
      ),
      "rap": (
          "Sen profesyonel bir hip-hop söz yazarısın (Rap Üstadı). Kullanıcının"
          " verdiği konuya veya tarza uygun, kafiyeli, ritmik ve etkileyici rap"
          " sözleri yaz."
      ),
  }

  system_prompt = prompts.get(mode, prompts["sohbet"])

  try:
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.7,
    )
    assistant_response = completion.choices[0].message.content
    return jsonify({"assistant": assistant_response})
  except Exception as e:
    return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
  app.run(debug=True, port=5000)