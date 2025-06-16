import os
import uuid
import threading
import subprocess
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

# Output directory
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def run_auto_editor(input_path, output_path):
    try:
        print(f"[INFO] Starting auto-editor for {input_path}")
        subprocess.run([
            'auto-editor', input_path,
            '--output_file', output_path,
            '--no-open'
        ], check=True)
        print(f"[INFO] Finished processing {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] auto-editor failed: {e}")


@app.route('/trim', methods=['POST'])
def trim_video():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    unique_id = uuid.uuid4().hex
    input_filename = f"input_{unique_id}.mp4"
    output_filename = f"output_{unique_id}.mp4"
    input_path = os.path.join(OUTPUT_DIR, input_filename)
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    file.save(input_path)
    print(f"[INFO] File saved to {input_path}")

    # Start trimming in background
    threading.Thread(target=run_auto_editor, args=(input_path, output_path)).start()

    return jsonify({
        "message": "Video is being processed in background",
        "output_filename": output_filename,
        "download_url": f"/download/{output_filename}"
    })


@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        return jsonify({"error": "File not ready or not found"}), 404

    return send_file(path, as_attachment=True)


@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "Server is running"}), 200


if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=5000)
