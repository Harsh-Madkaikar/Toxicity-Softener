import os, sys
from flask import Flask, request, jsonify
from flask_cors import CORS

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NLP = os.path.join(BASE, "nlp")
if NLP not in sys.path:
    sys.path.insert(0, NLP)

from pipeline import analyze_message

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.get("/")
def home():
    return jsonify({"status": "ok", "service": "Toxicity Softener API"})

@app.get("/health")
def health():
    return jsonify({"status": "healthy"})

@app.post("/analyze")
def analyze():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    if not isinstance(message, str):
        message = str(message)
    message = message.strip()
    if not message:
        return jsonify({"error": "message is required"}), 400
    if len(message) > 5000:
        message = message[:5000]
    try:
        return jsonify(analyze_message(message))
    except Exception as exc:
        app.logger.exception("Analysis failed")
        return jsonify({"error": str(exc)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
