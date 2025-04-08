from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Folder to store uploaded images
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

# Function to check allowed file types
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to load IPC data from JSON file
def load_ipc_data():
    with open("ipc_sections.json", "r", encoding="utf-8") as file:
        return json.load(file)

ipc_data = load_ipc_data()  # Load IPC data on startup

# Function to analyze crime and match IPC sections
def analyze_crime_image(image_path, caption):
    caption_lower = caption.lower()  # Convert input text to lowercase for better matching
    
    for crime, details in ipc_data.items():
        if crime in caption_lower:  # Check if crime name is in user description
            return details  # Return matching IPC section details
    
    return {
        "error": "No matching IPC section found. Please contact legal authorities."
    }

# API Route to analyze uploaded crime report
@app.route("/analyze", methods=["POST"])
def analyze():
    if "image" not in request.files or "caption" not in request.form or "location" not in request.form:
        return jsonify({"error": "Missing required data"}), 400

    file = request.files["image"]
    caption = request.form["caption"]
    location = request.form["location"]

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Get IPC section details based on the caption
        legal_info = analyze_crime_image(filepath, caption)

        return jsonify({
            "message": "Report submitted!",
            "legal_info": legal_info
        })

    return jsonify({"error": "Invalid file type"}), 400

if __name__ == "__main__":
    app.run(debug=True)
