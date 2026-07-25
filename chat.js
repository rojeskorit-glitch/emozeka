// Vercel Serverless Function
// Environment Variable: GROQ_API_KEY

export default async function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Sadece POST desteklenir' });
  }

  const apiKey = process.env.GROQ_API_KEY;

  if (!apiKey) {
    return res.status(500).json({ error: 'Sunucu yapılandırması eksik (GROQ_API_KEY)' });
  }

  try {
    const { messages } = req.body;

    if (!messages || !Array.isArray(messages)) {
      return res.status(400).json({ error: 'messages dizisi gerekli' });
    }

    // Mesaj sayısını sınırla (kötüye kullanımı azalt)
    const limitedMessages = messages.slice(-20);

    const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: 'llama-3.3-70b-versatile',
        messages: [
          {
            role: 'system',
            content: `Sen Emozeka'sın. Samimi, zeki, yardımcı ve biraz esprili bir kişisel yapay zeka asistanısın. Türkçe konuşursun. Kısa ve net cevaplar vermeyi tercih edersin ama gerektiğinde detaylı da anlatırsın. İnsan gibi doğal konuş. Aşırı resmi olma.`
          },
          ...limitedMessages
        ],
        temperature: 0.7,
        max_tokens: 1024
      })
    });

    if (!response.ok) {
      const errText = await response.text();
      console.error('Groq error:', errText);
      return res.status(response.status).json({
        error: 'Yapay zeka servisine ulaşılamadı. Biraz sonra tekrar dene.'
      });
    }

    const data = await response.json();
    const reply = data.choices?.[0]?.message?.content;

    if (!reply) {
      return res.status(500).json({ error: 'Boş cevap alındı' });
    }

    return res.status(200).json({ reply });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: 'Sunucu hatası' });
  }
}
