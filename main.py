from flask import Flask, jsonify, send_from_directory
from cryptography.fernet import Fernet
import os
from flask_cors import CORS


app = Flask(__name__)


CORS(app, resources={r"/*": {"origins": "http://localhost:8000"}})

# Encryption key
key = b'ZXR9XZicngAyKUDLxNRTYSGN7cMk-k2qn_lww6FB2BY='

# Function to encrypt a path
def encrypt_path(path):
    fernet = Fernet(key)
    return fernet.encrypt(path.encode()).decode()

# Function to decrypt an encrypted path
def decrypt_path(encrypted_path):
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_path.encode()).decode()

# Function to find immediate files and folders in a directory
def find_files_and_folders(directory):
    files = []
    folders = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isfile(item_path):
            files.append(item)
        elif os.path.isdir(item_path):
            folders.append(item)
    return files, folders


def generate_json_for_directory(directory):
    files, folders = find_files_and_folders(directory)
    json_data = {}
    for item in files + folders:
        item_path = os.path.join(directory, item)
        encoded_path = encrypt_path(item_path)
        item_type = "file" if os.path.isfile(item_path) else "folder"
        json_data[item] = {"encoded_path": encoded_path, "type": item_type}
    return json_data


# Route to display encoded paths for immediate files and folders in the 'content' directory
@app.route('/')
def display_encoded_paths():
    content_dir = 'content'
    json_data = generate_json_for_directory(content_dir)
    return jsonify(json_data)

# Route to serve JSON content for a directory or serve images
@app.route('/<path:encoded_path>')
def serve_json_or_image(encoded_path):
    try:
        directory = decrypt_path(encoded_path)  # Decrypt the encoded path
        if os.path.isdir(directory):
            json_data = generate_json_for_directory(directory)
            return jsonify(json_data)
        elif os.path.isfile(directory):
            # Check if the file is an image
            if directory.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                directory = directory.split('\\')
                directory = "/".join(directory[1:])
                return send_from_directory('content', directory)
            else:
                return jsonify({'error': 'File is not an image'})
        else:
            return jsonify({'error': 'Path does not exist'})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')