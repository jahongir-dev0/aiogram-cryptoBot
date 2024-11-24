import json

def read_user_settings(user_id):
    try:
        with open("user_settings.json", "r") as file:
            data = json.load(file)
        return data.get(str(user_id), {})
    except Exception as e:
        print(f"Xato: {e}")
        return {}

def save_user_settings(user_id, settings):
    try:
        with open("user_settings.json", "r") as file:
            data = json.load(file)
        data[str(user_id)] = settings
        with open("user_settings.json", "w") as file:
            json.dump(data, file)
    except Exception as e:
        print(f"Xato: {e}")
