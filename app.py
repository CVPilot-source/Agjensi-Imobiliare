import os
import json
import sqlite3
from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types

app = Flask(__name__, template_folder=".")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "leads.db")

# Listime SHEMBULL (DEMO) - Te shenuara qarte si shembuj fiktive
SAMPLE_PROPERTIES = [
    {
        "id": "DEMO-01",
        "title": "[SHEMBULL DEMO] Apartament 2+1 pranë Bllokut",
        "city": "Tiranë",
        "zone": "Ish-Blloku / Rruga Brigada VIII",
        "type": "Apartament",
        "transaction": "Shitje",
        "price": 175000,
        "currency": "EUR",
        "price_label": "175,000 € (Çmim Shembull)",
        "area_m2": 98,
        "bedrooms": 2,
        "bathrooms": 2,
        "is_sample": True,
        "sample_badge": "LISTIM SHEMBULL / DEMO",
        "description": "Ky është një listim ilustrues (shembull demo) për qëllime testimi. Apartament 2+1 me orientim jug-lindje dhe ballkon.",
        "image": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=800&q=80"
    },
    {
        "id": "DEMO-02",
        "title": "[SHEMBULL DEMO] Apartament 1+1 pranë Liqenit Artificial",
        "city": "Tiranë",
        "zone": "Rruga e Kosovarëve",
        "type": "Apartament",
        "transaction": "Qira",
        "price": 650,
        "currency": "EUR/muaj",
        "price_label": "650 € / muaj (Çmim Shembull)",
        "area_m2": 68,
        "bedrooms": 1,
        "bathrooms": 1,
        "is_sample": True,
        "sample_badge": "LISTIM SHEMBULL / DEMO",
        "description": "Pronë fiktive ilustruese. Apartament i mobiluar pranë parkut të Liqenit Artificial, kati i 4-t me ashensor.",
        "image": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=800&q=80"
    },
    {
        "id": "DEMO-03",
        "title": "[SHEMBULL DEMO] Apartament 2+1 me Pamje Deti në Vollga",
        "city": "Durrës",
        "zone": "Shëtitorja Vollga",
        "type": "Apartament",
        "transaction": "Shitje",
        "price": 135000,
        "currency": "EUR",
        "price_label": "135,000 € (Çmim Shembull)",
        "area_m2": 105,
        "bedrooms": 2,
        "bathrooms": 1,
        "is_sample": True,
        "sample_badge": "LISTIM SHEMBULL / DEMO",
        "description": "Listim demonstrues (jo ofertë reale). Apartament me verande dhe pamje ballore në shëtitoren e Vollgës.",
        "image": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80"
    },
    {
        "id": "DEMO-04",
        "title": "[SHEMBULL DEMO] Vilë 2-Katëshe në Lungomare",
        "city": "Vlorë",
        "zone": "Lungomare / Uji i Ftohtë",
        "type": "Vilë",
        "transaction": "Shitje",
        "price": 290000,
        "currency": "EUR",
        "price_label": "290,000 € (Çmim Shembull)",
        "area_m2": 210,
        "bedrooms": 3,
        "bathrooms": 3,
        "is_sample": True,
        "sample_badge": "LISTIM SHEMBULL / DEMO",
        "description": "Shembull demo për prezantim. Vilë dykatëshe me oborr të gjelbëruar dhe 2 poste parkimi.",
        "image": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80"
    },
    {
        "id": "DEMO-05",
        "title": "[SHEMBULL DEMO] Ambient Biznesi në Rrugën Kryesore",
        "city": "Tiranë",
        "zone": "Rruga e Kavajës",
        "type": "Ambient Biznesi",
        "transaction": "Qira",
        "price": 1200,
        "currency": "EUR/muaj",
        "price_label": "1,200 € / muaj (Çmim Shembull)",
        "area_m2": 85,
        "bedrooms": 0,
        "bathrooms": 1,
        "is_sample": True,
        "sample_badge": "LISTIM SHEMBULL / DEMO",
        "description": "Listim shembull (DEMO). Ambient me fasadë xhami në katin 0, i përshtatshëm për zyrë ose klinikë.",
        "image": "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=800&q=80"
    },
    {
        "id": "DEMO-06",
        "title": "[SHEMBULL DEMO] Garsoniere / Studio pranë Pedonales",
        "city": "Shkodër",
        "zone": "Pedonalja Kole Idromeno",
        "type": "Apartament",
        "transaction": "Qira",
        "price": 350,
        "currency": "EUR/muaj",
        "price_label": "350 € / muaj (Çmim Shembull)",
        "area_m2": 45,
        "bedrooms": 1,
        "bathrooms": 1,
        "is_sample": True,
        "sample_badge": "LISTIM SHEMBULL / DEMO",
        "description": "Shembull fiktiv demonstrues. Studio e restauruar në zemër të qendrës historike.",
        "image": "https://images.unsplash.com/photo-1493809842364-78817add7ffb?auto=format&fit=crop&w=800&q=80"
    }
]


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            city_zone TEXT,
            transaction_type TEXT,
            property_type TEXT,
            budget TEXT,
            property_ref TEXT,
            message TEXT,
            source TEXT DEFAULT 'contact_form',
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


init_db()


def save_lead_to_db(data: dict) -> int:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    c.execute(
        """
        INSERT INTO leads (
            full_name, phone, email, city_zone, transaction_type,
            property_type, budget, property_ref, message, source, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("full_name", "").strip(),
            data.get("phone", "").strip(),
            data.get("email", "").strip(),
            data.get("city_zone", "").strip(),
            data.get("transaction_type", "").strip(),
            data.get("property_type", "").strip(),
            str(data.get("budget", "")).strip(),
            data.get("property_ref", "").strip(),
            data.get("message", "").strip(),
            data.get("source", "contact_form").strip(),
            now_iso,
        ),
    )
    lead_id = c.lastrowid
    conn.commit()
    conn.close()
    return lead_id


@app.route("/")
def index():
    cities = sorted(list({p["city"] for p in SAMPLE_PROPERTIES}))
    prop_types = sorted(list({p["type"] for p in SAMPLE_PROPERTIES}))
    return render_template(
        "index.html",
        properties=SAMPLE_PROPERTIES,
        cities=cities,
        prop_types=prop_types,
    )


@app.route("/api/properties", methods=["GET"])
def get_properties():
    city = request.args.get("city", "").strip()
    prop_type = request.args.get("type", "").strip()
    transaction = request.args.get("transaction", "").strip()
    max_budget_str = request.args.get("max_budget", "").strip()

    max_budget = None
    if max_budget_str:
        try:
            max_budget = float(max_budget_str)
        except ValueError:
            max_budget = None

    filtered = []
    for p in SAMPLE_PROPERTIES:
        if city and p["city"].lower() != city.lower():
            continue
        if prop_type and p["type"].lower() != prop_type.lower():
            continue
        if transaction and p["transaction"].lower() != transaction.lower():
            continue
        if max_budget is not None and p["price"] > max_budget:
            continue
        filtered.append(p)

    return jsonify({
        "notice": "Të gjitha listimet e mëposhtme janë SHEMBUJ DEMO fiktivë dhe jo oferta reale.",
        "count": len(filtered),
        "properties": filtered,
    })


@app.route("/api/leads", methods=["GET", "POST"])
def handle_leads():
    if request.method == "POST":
        payload = request.get_json(silent=True) or request.form.to_dict()
        full_name = payload.get("full_name", "").strip()
        phone = payload.get("phone", "").strip()

        if not full_name or not phone:
            return jsonify({
                "ok": False,
                "error": "Ju lutem plotësoni emrin dhe numrin e telefonit."
            }), 400

        lead_id = save_lead_to_db(payload)
        return jsonify({
            "ok": True,
            "lead_id": lead_id,
            "message": "Kërkesa juaj (Lead) u ruajt me sukses në databazën SQLite!"
        }), 201

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM leads ORDER BY id DESC LIMIT 50")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify({"ok": True, "count": len(rows), "leads": rows})


def build_system_instruction() -> str:
    catalog_lines = []
    for p in SAMPLE_PROPERTIES:
        catalog_lines.append(
            f"- ID: {p['id']} | {p['title']} | Qyteti/Zona: {p['city']} ({p['zone']}) | "
            f"Lloji: {p['type']} | Transaksioni: {p['transaction']} | "
            f"Çmimi Shembull: {p['price_label']} | Sipërfaqja: {p['area_m2']} m²"
        )
    catalog_text = "\n".join(catalog_lines)

    return f"""Ti je Asistenti Virtual AI i agjencisë imobiliare demo "AlbEstate Demo".
Përgjigju gjithmonë në gjuhën shqipe, me ton miqësor, të qartë dhe të shkurtër (i përshtatshëm për ekran telefoni).

DETYRA JOTE KRYESORE:
1. Pyet dhe zbuloni në mënyrë të natyrshme këto 3 të dhëna nga vizitori:
   - A kërkon të BLEJË apo të marrë me QIRA?
   - Në cilin QYTET ose ZONË po kërkon?
   - Cili është BUXHETI i tij/saj?
2. RREGULL STRIKT: MOS SHPIK kurrë prona, adresa apo çmime që nuk janë në listën e mëposhtme!
3. Kur përmend një pronë nga lista, thekso gjithmonë qartë se është një "LISTIM SHEMBULL (DEMO)" me çmim ilustrues.
4. Pasi vizitori të ketë dhënë buxhetin, zonën dhe qëllimin (blerje/qira), sugjero vetëm listimet shembull nga katalogu që përshtaten (ose thuaj që nuk ka një shembull fiks në katalog për atë kriter) dhe ftoje vizitorin të lërë kontaktin në formularin e faqes ose direkt përmes butonit "Ruaj Kërkesën si Lead" në chat.

KATALOGU VETËM ME LISTIME SHEMBULL (DEMO):
{catalog_text}
"""


def fallback_assistant_reply(messages: list) -> str:
    """Përgjigje kur GEMINI_API_KEY nuk është vendosur ende në mjedis, pa shpikur asnjë pronë."""
    user_text = " ".join([m.get("content", "") for m in messages if m.get("role") == "user"]).lower()

    has_intent = any(w in user_text for w in ["blej", "blerje", "shitje", "qira", "qera"])
    has_zone = any(w in user_text for w in ["tiran", "durr", "vlor", "shkod", "bllok", "liqen", "vollg", "lungomare", "kavaj"])
    has_budget = any(ch.isdigit() for ch in user_text)

    missing = []
    if not has_intent:
        missing.append("nëse kërkoni të **blini** apo të merrni me **qira**")
    if not has_zone:
        missing.append("**qytetin ose zonën** që preferoni (p.sh. Tiranë, Durrës, Vlorë, Shkodër)")
    if not has_budget:
        missing.append("**buxhetin** tuaj orientues në Euro")

    matches = []
    for p in SAMPLE_PROPERTIES:
        if "qira" in user_text and p["transaction"].lower() != "qira":
            continue
        if ("blej" in user_text or "blerje" in user_text) and p["transaction"].lower() != "shitje":
            continue
        if p["city"].lower()[:4] in user_text:
            matches.append(f"• {p['id']}: {p['title']} — {p['price_label']}")

    note = "(Shënim: Variabla e mjedisit GEMINI_API_KEY nuk është konfiguruar ende në server; po përgjigjem me asistentin bazë demo.)\n\n"

    if missing:
        ask_str = ", ".join(missing)
        reply = (
            f"{note}Përshëndetje! Për t'ju ndihmuar sa më mirë me katalogun tonë demo, "
            f"ju lutem më tregoni {ask_str}."
        )
        if matches:
            reply += "\n\nNdërkohë, ja disa **listime shembull (DEMO)** nga ai qytet:\n" + "\n".join(matches[:3])
        return reply

    if not matches:
        matches = [f"• {p['id']}: {p['title']} ({p['city']}) — {p['price_label']}" for p in SAMPLE_PROPERTIES[:3]]

    return (
        f"{note}Faleminderit për detajet mbi buxhetin, zonën dhe llojin e transaksionit! "
        f"Duke qenë se nuk shpikim prona apo çmime, më poshtë janë vetëm **listime shembull (DEMO)** nga katalogu ynë ilustrues:\n"
        + "\n".join(matches)
        + "\n\nMund të klikoni butonin **'Ruaj Kërkesën si Lead'** më poshtë ose të plotësoni formularin e kontaktit që një agjent t'ju kontaktojë!"
    )


@app.route("/api/chat", methods=["POST"])
def chat_with_ai():
    data = request.get_json(silent=True) or {}
    messages = data.get("messages", [])
    if not messages or not isinstance(messages, list):
        return jsonify({"ok": False, "error": "Mesazhi mungon."}), 400

    # Lexohet VETEM nga variabla e mjedisit GEMINI_API_KEY
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()

    if not api_key:
        reply_text = fallback_assistant_reply(messages)
        return jsonify({
            "ok": True,
            "using_gemini": False,
            "reply": reply_text
        })

    try:
        client = genai.Client(api_key=api_key)
        contents = []
        for msg in messages[-12:]:
            role = "user" if msg.get("role") == "user" else "model"
            text = str(msg.get("content", "")).strip()
            if text:
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=text)]
                    )
                )

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=build_system_instruction(),
        temperature=0.2,
        max_output_tokens=2048,
            ),
        )
        reply_text = response.text or "Më falni, nuk munda të gjeneroj një përgjigje për momentin."
        return jsonify({
            "ok": True,
            "using_gemini": True,
            "reply": reply_text
        })
    except Exception as exc:
        return jsonify({
            "ok": False,
            "using_gemini": False,
            "error": f"Gabim gjatë thirrjes së Gemini API: {str(exc)}"
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
