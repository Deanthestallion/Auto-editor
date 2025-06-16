from flask import Flask, request, send_file, jsonify
import os
import subprocess

app = Flask(__name__)

@app.route('/')
def home():
    return "Server is live with Auto-Editor"

@app.route('/trim', methods=['POST'])
def trim_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video uploaded"}), 400

    video = request.files['video']
    input_path = f"/tmp/{video.filename}"
    output_path = f"/tmp/trimmed_{video.filename}"

    video.save(input_path)

    # Use auto-editor to remove silent parts
    try:
        subprocess.run(['auto-editor', input_path, '--output_file', output_path, '--no-open'], check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Auto-Editor failed", "details": str(e)}), 500

    return send_file(output_path, as_attachment=True)
