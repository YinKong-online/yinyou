from flask import Flask, request, jsonify, redirect, url_for
import json
import requests
import subprocess
import os
from flask_cors import CORS  

app = Flask(__name__)
CORS(app)  

# 获取JSON数据
def get_onset_times(name, mode):
    # 根据不同的模式选择不同的URL
    if mode == 'jiandan':
        url = "https://yinkong-online.github.io/yinyou/chuli.json"
    elif mode == 'kunnan':
        url = "https://yinkong-online.github.io/yinyou/chuli1.json"
    elif mode == 'emeng':
        url = "https://yinkong-online.github.io/yinyou/chuli2.json"
    else:
        return None, "Unsupported game mode"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text)
        for item in data:
            if isinstance(item, dict) and 'name' in item and item['name'] == name:
                return item['onset_times'], None
    return None, "onset_times not found for the given name"

@app.route('/start_game/<mode>', methods=['POST'])
def start_game(mode):
    data = request.get_json()  # 获取 JSON 格式的数据
    name = data.get('name')  # 获取 'name' 字段
    role_names = data.get('roles')  # 获取 'roles' 字段

    onset_times, error_message = get_onset_times(name, mode)
    if error_message:
        return jsonify({"error": error_message}), 404
    
    if mode == 'jiandan':
        game_script_path = "c:\\Users\\lenovo\\Desktop\\yinyou\\game\\jiandan.py"
    elif mode == 'kunnan':
        game_script_path = "c:\\Users\\lenovo\\Desktop\\yinyou\\game\\kunnan.py"
    elif mode == 'emeng':
        game_script_path = "c:\\Users\\lenovo\\Desktop\\yinyou\\game\\emeng.py"
    else:
        return jsonify({"error": "Unsupported game mode"}), 400
    
    if role_names is None:
        role_names = []
    command = ['python', game_script_path, name] + role_names
    
    try:
        subprocess.Popen(command)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    return jsonify({"message": f"Game started in {mode} mode"}), 200

if __name__ == '__main__':
    app.run(debug=True)
