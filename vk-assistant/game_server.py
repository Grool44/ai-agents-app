"""
Веб-сервер для мини-игры "VK Базука".
Запуск: py game_server.py
Доступ: http://localhost:5000
"""
from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

# Файл для сохранения прогресса
DATA_FILE = "game_data.json"


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "player_name": "Игрок",
        "money": 100,
        "level": 1,
        "base_level": 1,
        "income": 1,
        "clicks": 0
    }


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/data")
def get_data():
    return jsonify(load_data())


@app.route("/api/click", methods=["POST"])
def click():
    data = load_data()
    data["money"] += 1
    data["clicks"] += 1
    save_data(data)
    return jsonify(data)


@app.route("/api/upgrade/base", methods=["POST"])
def upgrade_base():
    data = load_data()
    cost = data["base_level"] * 50
    
    if data["money"] >= cost:
        data["money"] -= cost
        data["base_level"] += 1
        data["income"] = data["base_level"] * 2
        save_data(data)
    return jsonify(data)


@app.route("/api/upgrade/level", methods=["POST"])
def upgrade_level():
    data = load_data()
    cost = data["level"] * 100
    
    if data["money"] >= cost:
        data["money"] -= cost
        data["level"] += 1
        data["income"] = data["level"] * data["base_level"]
        save_data(data)
    return jsonify(data)


@app.route("/api/set_name", methods=["POST"])
def set_name():
    data = load_data()
    name = request.json.get("name", "Игрок")[:20]
    data["player_name"] = name
    save_data(data)
    return jsonify(data)


if __name__ == "__main__":
    print("\n[OK] Игра запущена: http://localhost:5000")
    print("[OK] Открой в браузере и играй!\n")
    app.run(debug=True, port=5000)
