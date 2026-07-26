import logging
import os
from flask import Flask, jsonify, render_template, request
from openai import OpenAI, OpenAIError

# Loglama yapılandırması
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__, template_folder=".")

# Groq API Entegrasyonu (Render ortam değişkeninden okur)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

client = OpenAI(
    api_key=GROQ_API_KEY,
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
    """Ana sayfayı render eder."""
    return render_template("index.html")

@app.route("/chat-api", methods=["POST"])
def emozeka_chat():
    """Groq API ile iletişim kurarak Roblox asistan yanıtını döndüren uç nokta."""
    try:
        data = request.get_json(silent=True)
        
        if not data or "message" not in data:
            return jsonify({"error": "Geçersiz istek formatı. JSON formatında 'message' alanı bekleniyor."}), 400

        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"error": "Lütfen ne tür bir Roblox sistemi istediğinizi yazın."}), 400

        # Groq API Çağrısı
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": ROBLOX_EXPERT_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.2,  # Kararlı ve hatasız kod üretimi için düşük tutuldu
            max_tokens=4096,  # Uzun ve kesintisiz kod blokları dönebilmesi için artırıldı
        )
        
        assistant_response = completion.choices[0].message.content
        return jsonify({"assistant": assistant_response}), 200

    except OpenAIError as oe:
        logging.error(f"Groq API Hatası: {str(oe)}")
        return jsonify({"error": f"Yapay zeka servis sağlayıcısında bir hata oluştu: {str(oe)}"}), 502
    except Exception as e:
        logging.error(f"Beklenmeyen Hata: {str(e)}")
        return jsonify({"error": f"Sunucu tarafında bir hata oluştu: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)