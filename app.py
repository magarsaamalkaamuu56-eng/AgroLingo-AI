import os
from flask import Flask, request, render_template_string, jsonify
from google import genai
from google.genai import types

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1_000_000

PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AgroLingo AI | Farming Assistant</title>
<style>
:root{--g:#176b45;--d:#103c2c;--m:#effaf2;--ink:#1c2e25}*{box-sizing:border-box}body{margin:0;background:#f5faf5;color:var(--ink);font:16px/1.55 system-ui,sans-serif}header,footer{padding:16px max(16px,calc((100% - 900px)/2));background:white;display:flex;justify-content:space-between;gap:10px;align-items:center}header{border-bottom:1px solid #dce9df}.brand{font-weight:850;color:var(--d);font-size:1.2rem}.brand span{color:#4c9d56}.tag{font-size:.7rem;color:var(--g);background:var(--m);padding:7px 10px;border-radius:20px}main{max-width:900px;margin:auto;padding:22px 14px}.hero{background:linear-gradient(125deg,#103c2c,#1d7049);color:white;padding:clamp(22px,5vw,42px);border-radius:22px}.eyebrow{font-size:.72rem;font-weight:800;letter-spacing:.1em;color:#aee77c}h1{font-size:clamp(2rem,6vw,3rem);line-height:1.1;margin:10px 0}h1 em{color:#d9f99d;font-style:normal}.hero p{color:#e0eee5}.panel{background:white;border:1px solid #dce9df;border-radius:18px;padding:20px;margin-top:18px;box-shadow:0 8px 25px #174b2910}.chatbox{height: min(48vh,420px);overflow:auto;padding:12px;background:#f7fbf7;border-radius:12px;border:1px solid #e0ebe1}.msg{padding:11px 13px;margin:9px 0;border-radius:13px;white-space:pre-wrap;overflow-wrap:anywhere}.user{background:#dcefe0;margin-left:12%;}.bot{background:white;border:1px solid #e1e9e2;margin-right:8%;}.controls{display:flex;gap:8px;margin-top:10px}textarea{flex:1;min-width:0;resize:vertical;min-height:48px;max-height:150px;padding:12px;border:1px solid #cbdacf;border-radius:12px;font:inherit}button{padding:12px 16px;background:var(--g);color:white;font:inherit;font-weight:800;border:0;border-radius:12px;cursor:pointer}button:disabled{opacity:.55}.hint,.small{font-size:.82rem;color:#607268}.trust{background:#eaf5ec;border-radius:14px;padding:15px;margin-top:16px}.quick{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}.quick button{background:#eaf5ec;color:var(--d);font-size:.85rem;padding:8px 10px}.status{min-height:1.4em;color:var(--g);font-size:.9rem}@media(max-width:520px){.controls{flex-direction:column}.user{margin-left:5%}.bot{margin-right:3%}header{align-items:flex-start}}
</style></head><body>
<header><div class="brand">🌱 AgroLingo <span>AI</span></div><span class="tag">AI FARMING ASSISTANT</span></header>
<main><section class="hero"><div class="eyebrow">PRACTICAL FARMING SUPPORT</div><h1>Ask about your crops.<br><em>Learn your next step.</em></h1><p>An AI-powered educational assistant for crop care, especially maize. Describe symptoms, soil, weather, or farming questions in everyday language.</p></section>
<section class="panel"><h2>💬 Chat with AgroLingo AI</h2><div class="quick"><button type="button" onclick="quickAsk('My maize leaves are turning yellow. What should I check first?')">Yellow maize leaves</button><button type="button" onclick="quickAsk('How can I check if my maize has too much or too little water?')">Water problems</button><button type="button" onclick="quickAsk('What information should I collect before asking an agricultural expert about crop disease?')">Crop disease</button></div>
<div class="chatbox" id="chat" aria-live="polite"><div class="msg bot">Hello! I’m AgroLingo AI 🌱. Ask me about maize, soil, watering, pests, plant symptoms, or general farming. I’ll explain possible causes and practical checks, but I can’t confirm a crop diagnosis from text alone.</div></div>
<form id="form"><div class="controls"><textarea id="message" maxlength="3000" placeholder="Type your farming question…" required></textarea><button id="send" type="submit">Send ➤</button></div></form><div id="status" class="status"></div><p class="hint">Tip: include the crop, plant growth stage, symptoms, recent rain, and soil moisture. Do not rely on AI alone before applying pesticides or expensive treatments.</p></section>
<section class="trust"><b>🛡️ Responsible guidance</b><p>This assistant can make mistakes. It provides educational information, not a certified diagnosis. For severe or spreading crop damage, consult a local agricultural extension worker. Never share passwords or private information.</p></section></main><footer><b>AgroLingo AI</b><span class="small">Learn, observe, and grow 🌱</span></footer>
<script>
const form=document.getElementById('form'),input=document.getElementById('message'),chat=document.getElementById('chat'),send=document.getElementById('send'),statusEl=document.getElementById('status');
function addMsg(text,who){const d=document.createElement('div');d.className='msg '+who;d.textContent=text;chat.appendChild(d);chat.scrollTop=chat.scrollHeight;return d}
function quickAsk(t){input.value=t;input.focus()}
form.addEventListener('submit',async e=>{e.preventDefault();const text=input.value.trim();if(!text)return;addMsg(text,'user');input.value='';send.disabled=true;statusEl.textContent='AgroLingo is thinking…';const pending=addMsg('Thinking…','bot');try{const r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text})});const data=await r.json();pending.textContent=data.reply||data.error||'No response received.';if(!r.ok)statusEl.textContent='The request failed. Please try again later.';else statusEl.textContent='';}catch(err){pending.textContent='I could not connect just now. Check your internet connection and try again.';statusEl.textContent='Connection error.'}finally{send.disabled=false;chat.scrollTop=chat.scrollHeight;input.focus()}});
</script></body></html>"""

SYSTEM_INSTRUCTION = """You are AgroLingo AI, a careful, helpful agriculture education assistant serving farmers, including in Ethiopia. Answer clearly and warmly in the language the user uses when possible (English or Afaan Oromo if capable). Give practical, low-cost steps first. Ask a short follow-up question when important details are missing. For crop symptoms, explain several possible causes and how to distinguish them; never claim certainty from text alone. Do not recommend specific pesticide products, hazardous mixing, or exact chemical dosages. Encourage label directions and advice from a local agricultural extension worker before chemical treatment. Consider maize and smallholder farming when relevant, but do not assume every question is about maize. If uncertain, say so. Keep answers organized and understandable. This is educational guidance, not a substitute for local expert diagnosis."""

@app.get("/")
def home():
    return render_template_string(PAGE)

@app.post("/chat")
def chat():
    body = request.get_json(silent=True) or {}
    message = str(body.get("message", "")).strip()
    if not message:
        return jsonify(error="Please enter a question."), 400
    if len(message) > 3000:
        return jsonify(error="Please keep your question under 3,000 characters."), 400
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return jsonify(reply="The AI service is not configured yet. The site owner needs to add GEMINI_API_KEY in Render → your service → Environment, then redeploy.") , 503
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash-lite"),
            contents=message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.6,
                max_output_tokens=700,
            ),
        )
        answer = (response.text or "I couldn't form an answer this time. Please try asking in a different way.").strip()
        return jsonify(reply=answer)
    except Exception as exc:
        # Keep credentials and provider error details out of the public response.
        app.logger.exception("Gemini request failed")
        return jsonify(reply="I couldn't get an AI response right now. Please try again later. If the problem continues, the site owner should check the Render logs and confirm the API key, model availability, and quota."), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
