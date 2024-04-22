from flask import Flask, jsonify, send_from_directory, render_template
from cryptography.fernet import Fernet
from configparser import ConfigParser
from flask_cors import CORS
import os


config = ConfigParser()
config.read('config.ini')

key = config['values']['key'].encode('utf-8')
basedir = config['values']['basedir']
port = config['values']['port']


app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "http://localhost:8000"}})


fernet = Fernet(key)

encrypt_path = lambda path: fernet.encrypt(path.encode()).decode()
decrypt_path = lambda path: fernet.decrypt(path.encode()).decode()


def generate_json(directory):

    json_data = {}
    for item in os.listdir(os.path.join(basedir, directory)):
        item_path = os.path.join(directory, item)
        full_item_path = os.path.join(basedir, item_path)

        json_data[item] = {
            "type": "folder" if os.path.isdir(full_item_path) else "file",
            "encoded_path": encrypt_path(item_path)
        }

    return json_data


@app.route('/')
def display_index():
    return render_template('index.html')


@app.route('/admin', host='127.0.0.1')
def display_admin():
    return render_template('admin.html')


@app.route('/<path:encoded_path>')
def serve_json_or_image(encoded_path):
    try:
        directory = decrypt_path(encoded_path)
        full_directory = os.path.join(basedir, directory)

        if os.path.isdir(full_directory):
            json_data = generate_json(directory)
            return jsonify(json_data)
        
        elif os.path.isfile(full_directory):

            if directory.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                return send_from_directory(
                    os.path.dirname(full_directory), 
                    os.path.basename(full_directory)
                )
            
            else:
                return jsonify({'error': 'File is not an image'})
            
        else:
            return jsonify({'error': 'Path does not exist'})
        
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    print(f'root encryped path:\n{encrypt_path("")}')
    app.run(debug=True, host='0.0.0.0')