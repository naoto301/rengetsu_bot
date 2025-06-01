import json
import os

DATA_FILE = "data/users.json"
PREMIUM_FILE = "data/premium_users.json"

os.makedirs("data", exist_ok=True)

def load_json(file_path):
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user_data(user_id):
    users = load_json(DATA_FILE)
    return users.get(user_id, {"count": 0, "name": None})

def update_user_data(user_id, data):
    users = load_json(DATA_FILE)
    users[user_id] = data
    save_json(DATA_FILE, users)

def increment_user_count(user_id):
    data = get_user_data(user_id)
    data["count"] += 1
    update_user_data(user_id, data)

def detect_and_register_name(user_id, message):
    if "と呼んで" in message:
        name = message.split("と呼んで")[0].strip()[-10:]
        data = get_user_data(user_id)
        data["name"] = name
        update_user_data(user_id, data)
        return f"了解しました。これからは{name}さんとお呼びしますね。"
    return None

def is_premium_user(user_id):
    premiums = load_json(PREMIUM_FILE)
    return user_id in premiums

def register_premium(user_id, code):
    premiums = load_json(PREMIUM_FILE)
    premiums[user_id] = code
    save_json(PREMIUM_FILE, premiums)
