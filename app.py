# Fake Job Detector India
# Copyright (c) 2026 Amit Mastud
# GitHub: github.com/Amit05-M/fake-job-detector
# All rights reserved.

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from analyzer import analyze_job_post

app = Flask(__name__, static_folder="static", static_url_path="/static")
CORS(app)

from flask import send_from_directory

from flask import Response

@app.route('/sitemap.xml')
def sitemap():
    xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://fake-job-detector-np6q.onrender.com/</loc>
    <lastmod>2026-04-22</lastmod>
    <changefreq>monthly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>'''
    return Response(xml, mimetype='application/xml')

@app.route('/robots.txt')
def robots():
    content = "User-agent: *\nAllow: /\nSitemap: https://fake-job-detector-np6q.onrender.com/sitemap.xml"
    return Response(content, mimetype='text/plain')

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

# CORRECT
@app.route('/ads.txt')
def ads_txt():
    return send_from_directory('static', 'ads.txt')

@app.route('/about')
def about():
    return send_from_directory('static', 'about.html')

@app.route('/blog')
def blog():
    return send_from_directory('static', 'blog.html')

@app.route('/test')
def test():
    return "Working"

@app.route("/privacy")
def privacy():
    return send_from_directory("static", "privacy.html")

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    if request.method == 'GET':
        return jsonify({
            "status": "ok",
            "message": "Fake Job Detector API is running. Send POST request with job_text."
        })

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