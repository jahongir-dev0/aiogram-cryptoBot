import json
import os
from datetime import datetime

SIGNAL_HISTORY_FILE = "signal_history.json"

# Signal tarixini o‘qish
def read_signal_history():
    if not os.path.exists(SIGNAL_HISTORY_FILE):
        return []
    with open(SIGNAL_HISTORY_FILE, "r") as f:
        return json.load(f)

# Yangi signalni tarixga qo‘shish
def save_signal_history(signal, symbols):
    history = read_signal_history()

    # Foydalanuvchi tanlagan signalni saqlash
    if signal['pair'] in symbols:
        history.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "signal": signal
        })
        with open(SIGNAL_HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=4)
