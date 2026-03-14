"""
Hellobooks AI Backend — Flask API
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from rag_engine import get_engine

app = Flask(
    __name__,
    template_folder=str(Path(__file__).parent.parent / "frontend" / "templates"),
    static_folder=str(Path(__file__).parent.parent / "frontend" / "static"),
)
CORS(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = (data or {}).get("question", "").strip()

    if not question:
        return jsonify({"error": "Question is required."}), 400

    try:
        engine = get_engine()
        result = engine.query(question)
        return jsonify({
            "answer": result["answer"],
            "sources": result["sources"],
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/rebuild", methods=["POST"])
def rebuild():
    try:
        engine = get_engine()
        engine.rebuild_index()
        return jsonify({"message": "Knowledge base index rebuilt successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "Hellobooks AI"})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
