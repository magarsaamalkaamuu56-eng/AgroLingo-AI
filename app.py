import os
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types

app = Flask(__name__)

API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

client = genai.Client(api_key=API_KEY) if API_KEY else None

SYSTEM_INSTRUCTION = """
You are AgroLingo AI, an agricultural assistant helping farmers
in Ethiopia.

Your responsibilities:
- Help farmers investigate maize and other crop problems.
- Explain possible crop diseases, pests, and nutrient deficiencies.
- Give practical advice about soil, irrigation, planting, and fertilizers.
- Use simple, clear English.
- When appropriate, consider the farming conditions in Ethiopia.
- Ask questions about symptoms, location, weather, and crop age
  when more information is needed.
- Explain that similar symptoms can have different causes.
- Never claim a definite diagnosis from symptoms alone.
- Recommend contacting a local agricultural extension worker
  when the problem is serious or uncertain.
- Do not invent scientific facts or pesticide instructions.
"""


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    if not client:
        return jsonify({
            "reply": "The AI is not configured yet. Please add "
                     "GEMINI_API_KEY in your Render Environment settings."
        }), 503

    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({"reply": "Please enter your farming question."}), 400

    if len(message) > 4000:
        return jsonify({
            "reply": "Please shorten your question to 4,000 characters or fewer."
        }), 400

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.4,
                max_output_tokens=700
            )
        )

        answer = response.text

        if not answer:
            answer = "I couldn't generate an answer. Please try again."

        return jsonify({"reply": answer})

    except Exception:
        app.logger.exception("Gemini request failed")
        return jsonify({
            "reply": "I couldn't contact the AI service. Please try again "
                     "later or check the Render logs and Gemini model settings."
        }), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
