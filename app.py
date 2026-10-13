import os
from flask import Flask, request, render_template_string

app = Flask(__name__)

GUIDES = {
    "yellow": ("Yellowing leaves",
        "Possible causes include nutrient deficiency, water stress, root problems, or natural ageing. These signs alone cannot confirm a cause.",
        ["Check whether soil is very dry or waterlogged.", "Notice whether older lower leaves or newer upper leaves turn yellow.", "Compare several affected plants with healthy plants nearby."],
        "Check soil moisture first. Avoid applying fertilizer or pesticides until the likely cause is better understood."),
    "spots": ("Brown or dark leaf spots",
        "Spots can be associated with disease, physical damage, or environmental stress. Appearance alone is not enough for a reliable diagnosis.",
        ["Look at the shape and edges of the spots.", "Check whether spots are spreading on several plants.", "Inspect both sides of leaves and note recent rain or prolonged leaf wetness."],
        "Photograph affected leaves in good light and seek local agricultural advice if the spots are spreading."),
    "wilting": ("Wilting or drooping plants",
        "Possible causes include insufficient water, waterlogged soil, root injury, or disease.",
        ["Check soil moisture below the surface.", "See whether wilting affects isolated plants or the whole field.", "Inspect plant bases for damage or unusual discoloration."],
        "Do not assume wilting always means the crop needs more water; waterlogged soil can also cause wilting."),
    "stunted": ("Slow or stunted growth",
        "Possible causes include poor soil fertility, water stress, crowding, root damage, pests, or disease.",
        ["Compare affected plants with healthy plants nearby.", "Check spacing and soil moisture.", "Look for leaf damage, insects, or damaged roots."],
        "Record where the problem occurs and consult local crop-management guidance before making major changes.")
}

PAGE = """
<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AgroLingo AI | Maize Guide</title>
<style>
:root{--g:#176b45;--d:#103c2c;--m:#effaf2;--ink:#1c2e25}*{box-sizing:border-box}body{margin:0;background:#f5faf5;color:var(--ink);font:16px/1.55 system-ui, sans-serif}
header,footer{padding:18px max(18px,calc((100% - 900px)/2));background:white;display:flex;justify-content:space-between;gap:10px;align-items:center}header{border-bottom:1px solid #dce9df}.brand{font-weight:850;color:var(--d);font-size:1.2rem}.brand span{color:#4c9d56}.tag{font-size:.7rem;color:var(--g);background:var(--m);padding:7px 10px;border-radius:20px}
main{max-width:900px;margin:auto;padding:25px 16px}.hero{background:linear-gradient(125deg,#103c2c,#1d7049);color:white;padding:clamp(25px,6vw,50px);border-radius:24px;display:flex;justify-content:space-between;gap:15px;align-items:center}.eyebrow{font-size:.72rem;font-weight:800;letter-spacing:.12em;color:#aee77c}h1{font-size:clamp(2rem,6vw,3.4rem);line-height:1.08;margin:12px 0}h1 em{color:#d9f99d;font-style:normal}.hero p{max-width:580px;color:#e0eee5}.corn{font-size:clamp(3rem,12vw,7rem)}.pills{display:flex;flex-wrap:wrap;gap:8px}.pills span{font-size:.8rem;border:1px solid #ffffff40;border-radius:20px;padding:6px 9px}
.panel{background:white;border:1px solid #dce9df;border-radius:20px;padding:clamp(20px,4vw,32px);margin-top:20px;box-shadow:0 10px 30px #174b2910}.eyebrow.dark{color:var(--g)}h2{margin:0 0 15px}label{display:block;font-weight:700;margin:15px 0 6px}select{width:100%;padding:12px;border:1px solid #cbdacf;border-radius:11px;background:#fbfdfb;font:inherit}.grid{display:grid;grid-template-columns:1fr 1fr;gap:0 14px}.wide{grid-column:1/-1}button{width:100%;padding:14px;margin-top:22px;background:var(--g);color:white;font:inherit;font-weight:800;border:0;border-radius:12px}.result{border-top:5px solid #80c75b}.notice,.action{padding:15px;border-radius:12px;background:#fff8e7;border:1px solid #f0dfae;margin:15px 0}.action{background:var(--m);border-color:#cde9d1}.trust{background:#eaf5ec;border-radius:16px;padding:18px;margin-top:20px}.trust p{margin-bottom:0}.small{font-size:.83rem;color:#607268}.reset{color:var(--g);font-weight:800;text-decoration:none}
@media(max-width:600px){.hero{align-items:flex-start}.corn{font-size:3rem}.grid{grid-template-columns:1fr}.wide{grid-column:auto}.tag{font-size:.6rem}footer{flex-direction:column;align-items:flex-start}}
</style></head><body><header><div class="brand">🌱 AgroLingo <span>AI</span></div><span class="tag">MAIZE CROP GUIDE</span></header>
<main><section class="hero"><div><div class="eyebrow">SMARTER FARMING STARTS WITH OBSERVATION</div><h1>Understand your crop.<br><em>Choose the next step.</em></h1><p>A simple educational guide to help maize farmers explore possible causes and decide what to check next.</p><div class="pills"><span>🌽 Maize-focused</span><span>📱 Mobile-friendly</span><span>📚 Evidence-aware</span></div></div><div class="corn">🌽</div></section>
<section class="panel"><div class="eyebrow dark">STEP 01</div><h2>Describe what you see</h2><form method="post" action="#result">
<label for="symptom">Main symptom</label><select id="symptom" name="symptom" required><option value="">Choose the closest match</option>
<option value="yellow" {% if symptom == 'yellow' %}selected{% endif %}>Leaves turning yellow</option><option value="spots" {% if symptom == 'spots' %}selected{% endif %}>Brown or dark spots on leaves</option><option value="wilting" {% if symptom == 'wilting' %}selected{% endif %}>Plant wilting or drooping</option><option value="stunted" {% if symptom == 'stunted' %}selected{% endif %}>Slow or stunted growth</option></select>
<div class="grid"><div><label for="stage">Plant growth stage</label><select id="stage" name="stage"><option>Not sure</option><option>Young seedlings</option><option>Growing plants</option><option>Mature plants / near harvest</option></select></div><div><label for="soil">Soil condition</label><select id="soil" name="soil"><option>Not sure</option><option>Very dry</option><option>Moist, not flooded</option><option>Very wet / waterlogged</option></select></div><div class="wide"><label for="pattern">Where are symptoms visible?</label><select id="pattern" name="pattern"><option>Not sure</option><option>Only a few plants</option><option>Patches in the field</option><option>Many plants across the field</option></select></div></div><button type="submit">Review possible causes →</button></form></section>
{% if result %}<section class="panel result" id="result"><div class="eyebrow dark">STEP 02 · INITIAL GUIDANCE</div><h2>{{ result.title }}</h2><div class="notice"><b>Possible explanations — not a diagnosis</b><p>{{ result.possible }}</p></div><h3>What to check next</h3><ul>{% for item in result.checks %}<li>{{ item }}</li>{% endfor %}</ul><div class="action"><b>Suggested next step</b><p>{{ result.next }}</p></div><a class="reset" href="/">← Check another symptom</a></section>{% endif %}
<section class="trust"><b>🛡️ Guidance with care</b><p>This is an early educational prototype, not a certified diagnostic tool. It does not yet use a trained AI model or verified local diagnosis data. For fast-spreading damage or major crop losses, consult a local agricultural extension worker.</p></section></main>
<footer><b>AgroLingo AI</b><span class="small">Built to learn, test, and improve 🌱</span></footer></body></html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    symptom = request.form.get("symptom", "") if request.method == "POST" else ""
    raw = GUIDES.get(symptom)
    result = None
    if raw:
        result = {"title": raw[0], "possible": raw[1], "checks": raw[2], "next": raw[3]}
    return render_template_string(PAGE, symptom=symptom, result=result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
