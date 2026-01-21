"""
Web UI using Flask
Simple interface for resume matching
"""

import os
import json
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

from core.matcher import Matcher
from core.database import Database
from core.resume_parser import ResumeParser
from core.jd_parser import JDParser
from config import Config

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size
UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Initialize database
db = Database()


@app.route("/")
def index():
    """Serve main page"""
    return render_template("index.html")


@app.route("/api/match", methods=["POST"])
def api_match():
    """API endpoint for matching"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        resume_text = data.get("resume", "").strip()
        jd_text = data.get("jd", "").strip()
        save_match = data.get("save", False)
        
        if not resume_text or not jd_text:
            return jsonify({"error": "Both resume and JD are required"}), 400
        
        # Perform matching
        matcher = Matcher()
        result = matcher.match(resume_text, jd_text, include_recommendations=True)
        
        # Save to database if requested
        if save_match:
            record = db.save_match(
                resume_text=resume_text,
                jd_text=jd_text,
                score=result["score"],
                explanation=result["explanation"],
                recommendations=result.get("recommendations", []),
            )
            result["id"] = record.id
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/upload-resume", methods=["POST"])
def api_upload_resume():
    """Upload resume file"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400
        
        # Check file extension
        allowed_extensions = {".pdf", ".txt", ".md"}
        filename = secure_filename(file.filename)
        ext = os.path.splitext(filename)[1].lower()
        
        if ext not in allowed_extensions:
            return jsonify({"error": f"File type not allowed. Allowed: {allowed_extensions}"}), 400
        
        # Save file
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        
        # Extract text
        resume_text = ResumeParser.parse(filepath)
        
        return jsonify({"text": resume_text, "filename": filename})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/matches", methods=["GET"])
def api_list_matches():
    """List all stored matches"""
    try:
        limit = request.args.get("limit", 50, type=int)
        order_by = request.args.get("order", "score")
        
        matches = db.list_matches(limit=limit, order_by=order_by)
        stats = db.get_stats()
        
        return jsonify({
            "stats": stats,
            "matches": [
                {
                    "id": m.id,
                    "score": m.score,
                    "explanation": m.explanation,
                    "timestamp": m.timestamp.isoformat(),
                    "recommendations": json.loads(m.recommendations) if m.recommendations else [],
                }
                for m in matches
            ],
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/match/<int:match_id>", methods=["GET"])
def api_get_match(match_id):
    """Get specific match details"""
    try:
        match = db.get_match(match_id)
        
        if not match:
            return jsonify({"error": "Match not found"}), 404
        
        return jsonify({
            "id": match.id,
            "score": match.score,
            "explanation": match.explanation,
            "recommendations": json.loads(match.recommendations) if match.recommendations else [],
            "timestamp": match.timestamp.isoformat(),
            "resume_preview": match.resume_text[:500],
            "jd_preview": match.jd_text[:500],
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/match/<int:match_id>", methods=["DELETE"])
def api_delete_match(match_id):
    """Delete a match"""
    try:
        success = db.delete_match(match_id)
        
        if not success:
            return jsonify({"error": "Match not found"}), 404
        
        return jsonify({"success": True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=Config.FLASK_DEBUG, port=Config.FLASK_PORT)
