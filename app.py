import os
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from openai import OpenAI

# .env dosyasındaki GROQ_API_KEY değişkenini yükler
load_dotenv()

app = Flask(__name__, template_folder=".")

# Groq API Entegrasyonu
client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Sistem Talimatı (Roblox Studio & Luau Baş Uzmanı)
ROBLOX_EXPERT_PROMPT = (
    "Sen Roblox Studio ve Luau (Lua 5.1+) konusunda dünyanın en deneyimli baş yazılımcısısın. "
    "Kullanıcı senden ne tür bir sistem isterse istesin (Örn: Roblox için FiveM tarzı Araç Spawner, Inventory, Envanter vb.):\n"
    "1. İstenen sistemi SIFIRDAN ve EKSİKSİZ olarak yazacaksın.\n"
    "2. İhtiyaç duyulan TÜM bileşenleri sunacaksın: ServerScriptService içindeki Script, StarterPlayerScripts/UI içindeki LocalScript, RemoteEvent isimleri ve ReplicatedStorage düzeni.\n"
    "3. Kodlar en güncel Roblox Luau standartlarına uygun, performanslı, güvenli (Exploit/Hile korumalı Server-Side kontrolleri olan) ve tamamen HATASIZ olmalıdır.\n"
    "4. Hiçbir kodu yarım bırakma ('-- burayı sen doldur' gibi geçiştirmeler yapma), tam çalışan halini sağla.\n"
    "5. Kurulum adımlarını Studio içinde nereye ne koyulacağını belirterek adım adım açıkla."
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat-api", methods=["POST"])
def emozeka_chat():
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "Lütfen ne tür bir Roblox sistemi istediğinizi yazın."}), 400

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": ROBLOX_EXPERT_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.2, # Kodların hatasız ve mantıksal olarak tam doğru çıkması için sıcaklık düşük tutuldu
        )
        assistant_response = completion.choices[0].message.content
        return jsonify({"assistant": assistant_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)