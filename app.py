# pyre-ignore-all-errors
"""
Smart File Organizer — Flask Backend (REST API).

Composition root: creates all service layers and exposes HTTP endpoints.
"""

import os
import sys
import subprocess
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

from core.adapters.file_system_adapter import FileSystemAdapter
from core.ollama_client import OllamaClient
from core.repository.metadata_repository import MetadataRepository
from core.services.content_analysis_service import ContentAnalysisService
from core.services.ml_tagging_service import MLTaggingService
from core.services.search_service import SearchService
from core.services.file_processing_service import FileProcessingService

# ---------------------------------------------------------------------------
# App config
# ---------------------------------------------------------------------------
frontend_build = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "build")

if os.path.exists(frontend_build):
    app = Flask(__name__, static_folder=frontend_build, static_url_path="/")
    @app.route("/")
    def serve_index():
        return app.send_static_file("index.html")
    
    @app.errorhandler(404)
    def catch_all(e):
        # Allow React Router to handle undefined backend paths
        return app.send_static_file("index.html")
else:
    app = Flask(__name__)

CORS(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"txt", "pdf", "doc", "docx"}

# ---------------------------------------------------------------------------
# Compose service layers
# ---------------------------------------------------------------------------
fs_adapter = FileSystemAdapter()
repository = MetadataRepository(db_path="smart_organizer.db")
content_analysis = ContentAnalysisService(fs_adapter)
ollama_client = OllamaClient()
ml_tagging = MLTaggingService(ollama_client)
search_service = SearchService(repository)
file_processing = FileProcessingService(
    fs_adapter=fs_adapter,
    repository=repository,
    content_analysis=content_analysis,
    ml_tagging=ml_tagging,
)


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------

@app.route("/api/files", methods=["GET"])
def get_files():
    """Return all registered files with their tags."""
    files = file_processing.get_all_files()
    return jsonify(files)


@app.route("/api/upload", methods=["POST"])
def upload_file():
    """Upload a file (doc/pdf/txt), save it, and register in the database."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    if not _allowed_file(file.filename):
        return jsonify({"error": f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

    filename = secure_filename(file.filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)

    file_data = file_processing.add_file(save_path)
    return jsonify(file_data), 201


@app.route("/api/files/delete", methods=["POST"])
def delete_files():
    """Bulk delete physical files and their DB records."""
    data = request.get_json()
    if not data or "paths" not in data:
        return jsonify({"error": "Missing 'paths' in request body"}), 400
    
    paths = data["paths"]
    if not isinstance(paths, list):
        return jsonify({"error": "'paths' must be a list"}), 400

    file_processing.delete_files(paths)
    return jsonify({"success": True})



@app.route("/api/analyze", methods=["POST"])
def analyze_file():
    """Extract text and generate tags for a file."""
    data = request.get_json()
    if not data or "path" not in data:
        return jsonify({"error": "Missing 'path' in request body"}), 400

    file_path = data["path"]
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    tags = file_processing.process_file(file_path)
    return jsonify({"path": file_path, "tags": tags})


@app.route("/api/analyze/batch", methods=["POST"])
def analyze_batch():
    """Analyze multiple files at once."""
    data = request.get_json()
    if not data or "paths" not in data:
        return jsonify({"error": "Missing 'paths' in request body"}), 400

    results = []
    for file_path in data["paths"]:
        if os.path.exists(file_path):
            tags = file_processing.process_file(file_path)
            results.append({"path": file_path, "tags": tags})
        else:
            results.append({"path": file_path, "tags": [], "error": "File not found"})

    return jsonify(results)


@app.route("/api/tags/edit", methods=["POST"])
def edit_tags():
    """Manually edit/update tags for a file."""
    data = request.get_json()
    if not data or "path" not in data or "tags" not in data:
        return jsonify({"error": "Missing 'path' or 'tags' in request body"}), 400

    file_path = data["path"]
    tags = data["tags"]
    
    if not isinstance(tags, list):
        return jsonify({"error": "'tags' must be a list of strings"}), 400

    updated_tags = file_processing.update_tags(file_path, tags)
    return jsonify({"path": file_path, "tags": updated_tags})


@app.route("/api/open", methods=["POST"])
def open_file_local():
    """Open a file using the operating system's default viewer."""
    data = request.get_json()
    if not data or "path" not in data:
        return jsonify({"error": "Missing 'path'"}), 400
        
    file_path = os.path.abspath(data["path"])
    if not os.path.exists(file_path):
        return jsonify({"error": f"File not found: {file_path}"}), 404
        
    try:
        if sys.platform == "win32":
            os.startfile(file_path)  # type: ignore
        elif sys.platform == "darwin":
            subprocess.call(["open", str(file_path)])  # type: ignore
        else:
            subprocess.call(["xdg-open", str(file_path)])  # type: ignore
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/search", methods=["GET"])
def search_files():
    """Search files by tags (FTS5 full-text search)."""
    query = request.args.get("q", "").strip()
    results = search_service.search(query)
    return jsonify(results)


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Smart File Organizer — Backend running on http://localhost:5000")
    app.run(debug=True, port=5000)
