from flask import Flask, request, jsonify
import json
import requests
import subprocess
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 配置URL和游戏脚本路径
GAME_MODES_URLS = {
    'jiandan': "https://yinkong-online.github.io/yinyou/chuli.json",
    'kunnan': "https://yinkong-online.github.io/yinyou/chuli1.json",
    'emeng': "https://yinkong-online.github.io/yinyou/chuli2.json"
}

GAME_SCRIPTS = {
    'jiandan': "c:\\Users\\lenovo\\Desktop\\yinyou\\game\\jiandan.py",
    'kunnan': "c:\\Users\\lenovo\\Desktop\\yinyou\\game\\kunnan.py",
    'emeng': "c:\\Users\\lenovo\\Desktop\\yinyou\\game\\emeng.py"
}

# 获取JSON数据
def get_onset_times(name, mode):
    url = GAME_MODES_URLS.get(mode)
    if not url:
        return None, "Unsupported game mode"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text)
        for item in data:
            if isinstance(item, dict) and 'name' in item and item['name'] == name:
                return item['onset_times'], None
    return None, "onset_times not found for the given name"

# 获取游戏脚本路径
def get_game_script_path(mode):
    return GAME_SCRIPTS.get(mode)

@app.route('/start_game/<mode>', methods=['POST'])
def start_game(mode):
    data = request.get_json()
    name = data.get('name')
    role_names = data.get('roles')

    onset_times, error_message = get_onset_times(name, mode)
    if error_message:
        return jsonify({"error": error_message}), 404
    
    game_script_path = get_game_script_path(mode)
    if not game_script_path:
        return jsonify({"error": "Unsupported game mode"}), 400
    
    if not isinstance(role_names, list) or len(role_names) == 0:
        return jsonify({"error": "Invalid role names"}), 400

    command = ['python', game_script_path, name] + role_names
    
    try:
        subprocess.Popen(command)
    except FileNotFoundError:
        return jsonify({"error": "Game script not found"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    
    return jsonify({
        "message": f"Game started in {mode} mode",
        "mode": mode,
        "name": name,
        "roles": role_names
    }), 200

if __name__ == '__main__':
    app.run(debug=True)