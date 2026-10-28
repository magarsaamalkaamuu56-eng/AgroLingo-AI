
import os
import base64
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def generate_ai(prompt, language="English", image=None, mime_type="image/jpeg"):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing from Render environment variables."
        )

    client = genai.Client(api_key=api_key)

    instructions = f"""
    You are Agrolingo AI, an agricultural assistant.
    Give practical, scientifically grounded advice for farmers.
    Respond entirely in {language}.
    Explain uncertainty instead of claiming an unconfirmed diagnosis.
    For pesticides and fertilizers, advise following product labels,
    protective equipment requirements, and local agricultural guidance.
    Do not invent current weather or market prices.
    """

    contents = [prompt]

    if image:
        image_bytes = base64.b64decode(image, validate=True)
        contents.append(
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type
            )
        )

    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=instructions
        )
    )

    return response.text or "No response was generated. Please try again."


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return jsonify({"ok": True, "model": MODEL})


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    language = str(data.get("language", "English"))[:40]

    if not message:
        return jsonify({"error": "Enter a question."}), 400

    try:
        answer = generate_ai(message, language)
        return jsonify({"text": answer})
    except Exception:
        app.logger.exception("Chat request failed")
        return jsonify({
            "error": "AI request failed. Check your API key, model, quota, and Render logs."
        }), 502


@app.route("/api/translate", methods=["POST"])
def translate():
    data = request.get_json(silent=True) or {}
    source = str(data.get("text", "")).strip()
    language = str(data.get("language", "English"))[:40]

    if not source:
        return jsonify({"error": "Enter text to translate."}), 400

    prompt = f"""
    Translate and simplify this agricultural text for farmers.
    Preserve important safety warnings, measurements, and quantities.
    Do not invent pesticide application rates.

    TEXT:
    {source}
    """

    try:
        return jsonify({
            "text": generate_ai(prompt, language)
        })
    except Exception:
        app.logger.exception("Translation failed")
        return jsonify({"error": "Translation failed. Check the Gemini configuration."}), 502


@app.route("/api/diagnose", methods=["POST"])
def diagnose():
    data = request.get_json(silent=True) or {}

    notes = str(data.get("notes", "")).strip()
    language = str(data.get("language", "English"))[:40]
    image = data.get("image")
    mime_type = str(data.get("mimeType", "image/jpeg"))

    if not image and not notes:
        return jsonify({
            "error": "Upload a crop photo or describe the symptoms."
        }), 400

    prompt = f"""
    Analyze the crop symptoms and attached image, if provided.

    Explain:
    1. Visible symptoms.
    2. Possible diseases, pests, or nutrient deficiencies.
    3. Confidence and alternative explanations.
    4. Practical, low-cost management options.
    5. Prevention and further information needed.

    Do not claim certainty from an image alone.
    Do not invent chemical doses.

    Farmer notes: {notes or "None provided"}
    """

    try:
        return jsonify({
            "text": generate_ai(
                prompt,
                language,
                image,
                mime_type
            )
        })
    except Exception:
        app.logger.exception("Crop diagnosis failed")
        return jsonify({
            "error": "Crop analysis failed. Check the API key, model, quota, and image."
        }), 502


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "10000"))
    )
