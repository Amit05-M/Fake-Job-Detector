from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from analyzer import analyze_job_post

app = Flask(__name__, static_folder="static", static_url_path="/static")
CORS(app)

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()

    if not data or "job_text" not in data:
        return jsonify({"error": "No job text provided"}), 400

    job_text = data["job_text"].strip()

    if len(job_text) < 50:
        return jsonify({"error": "Job post is too short to analyze"}), 400

    try:
        result = analyze_job_post(job_text)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)