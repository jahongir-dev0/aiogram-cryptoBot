from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Signal Olish 📊"),
        ],
        [
            KeyboardButton(text="Avto Signal 💿"),
            KeyboardButton(text="Stop Signal 🤚"),
        ],
        [
            KeyboardButton(text="Signal Sozlamalari ⚙️")
        ]

    ], resize_keyboard=True
)