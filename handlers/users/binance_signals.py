import asyncio
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State
from aiogram.dispatcher.filters import Text
from loader import dp
from utils.binance_signals import get_signals
from utils.user_settings import read_user_settings, save_user_settings
from states.state import UserStates

# Global o'zgaruvchi: aktiv signal vazifalarini saqlash
active_signal_task = {}

# Signal Sozlamalari ⚙️ handleri
@dp.message_handler(text="Signal Sozlamalari ⚙️", state="*")
async def set_signal_preferences(message: types.Message, state: FSMContext):
    try:
        user_settings = read_user_settings(message.from_user.id)

        if user_settings:
            current_symbols = user_settings.get("symbols", [])
            if current_symbols:
                symbols_text = ', '.join(current_symbols)
            else:
                symbols_text = "<b>Sozlamalar mavjud emas.</b>"
            await message.answer(f"<b>Sizning mavjud signal sozlamalaringiz: <i>{symbols_text}</i>\n\n"
                                 "Agar yangilamoqchi bo'lsangiz, iltimos, kerakli kriptolarni kiriting, Na'muna: 'BTCUSDT'</b>")
            await state.set_state(UserStates.waiting_for_symbols.state)  # Kriptolarni kiritishga o'tish
        else:
            await message.answer("<b>Siz hali signal sozlamalaringizni kiritmadingiz.\n"
                                 "Iltimos, signal sozlamalarini boshlash uchun kriptolarni kiriting, Na'muna: 'BTCUSDT'</b>")
            await state.set_state(UserStates.waiting_for_symbols.state)  # Kriptolarni kiritishga o'tish
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {e}")

# Foydalanuvchidan sozlamalarni olish va saqlash
@dp.message_handler(state=UserStates.waiting_for_symbols)
async def save_user_symbols(message: types.Message, state: FSMContext):
    try:
        user_symbols = message.text.strip()

        if user_symbols:
            symbols = user_symbols.split(",")  # Vergul bilan ajratish
            user_settings = read_user_settings(message.from_user.id)
            user_settings["symbols"] = symbols
            save_user_settings(message.from_user.id, user_settings)

            await message.answer(f"Sizning sozlamalaringiz yangilandi: {', '.join(symbols)}")
            await state.finish()  # Sozlamalar tugadi
        else:
            await message.answer("Iltimos, to‘g‘ri kriptolarni kiriting. Masalan: BTCUSDT, ETHUSDT.")
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {e}")

# Signal Olish 📊 handleri
@dp.message_handler(text="Signal Olish 📊", state="*")
async def send_binance_signals(message: types.Message, state: FSMContext):
    try:
        user_settings = read_user_settings(message.from_user.id)
        user_symbols = user_settings.get("symbols", ["BTCUSDT", "ETHUSDT", "BNBUSDT"])  # Standart juftliklar

        signals = get_signals(user_symbols)

        if signals:
            for signal in signals:
                if signal['pair'] in user_symbols:
                    await message.answer(
                        f"💡 <b>Juftlik:</b> <i>{signal['pair']}</i>\n"
                        f"📈 <b>Trend:</b> <i>{signal['trend']}</i>\n"
                        f"💲 <b>Oxirgi narx:</b> <i>{signal['price']} USDT</i>\n"
                        f"📊 <b>O‘zgarish:</b> <i>{signal['change']} (absolyut: {signal['change_absolute']} USDT)</i>\n"
                        f"📦 <b>Savdo hajmi:</b> <i>{signal['volume']}</i>\n\n"
                    )
        else:
            await message.answer("⚠️ Binance'dan signallarni olishda xatolik yuz berdi. Iltimos, keyinroq urinib ko‘ring.")
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {e}")

# Signal yuborishni har 10 soniyada yuborish
async def send_signals_periodically(chat_id: int, user_id: int):
    while True:
        try:
            user_settings = read_user_settings(user_id)
            user_symbols = user_settings.get("symbols", ["BTCUSDT", "ETHUSDT", "BNBUSDT"])  # Standart juftliklar

            signals = get_signals(user_symbols)
            if signals:
                for signal in signals:
                    await dp.bot.send_message(
                        chat_id=chat_id,  # Faqat bitta foydalanuvchiga signal yuborish
                        text=f"💡 <b>Juftlik:</b> {signal['pair']}\n"
                             f"📈 <b>Trend:</b> {signal['trend']}\n"
                             f"💲 <b>Oxirgi narx:</b> {signal['price']} USDT\n"
                             f"📊 <b>O‘zgarish:</b> {signal['change']} (absolyut: {signal['change_absolute']} USDT)\n"
                             f"📦 <b>Savdo hajmi:</b> {signal['volume']}\n"
                    )
        except Exception as e:
            print(f"Xatolik yuz berdi: {e}")
        await asyncio.sleep(10)  # Har 10 soniyada yangilanish

# Avto signal yuborishni boshlash
@dp.message_handler(text="Avto Signal 💿", state="*")
async def start_auto_signals(message: types.Message, state: FSMContext):
    try:
        user_settings = read_user_settings(message.from_user.id)
        chat_id = message.chat.id

        if message.from_user.id not in active_signal_task or active_signal_task[message.from_user.id].done():
            task = asyncio.create_task(send_signals_periodically(chat_id, message.from_user.id))
            active_signal_task[message.from_user.id] = task
            await message.answer("Avtomatik signal yuborish boshlandi.")
        else:
            await message.answer("Avto signal allaqachon ishlayapti!")
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {e}")

# Avto signal yuborishni to'xtatish
@dp.message_handler(text="Stop Signal 🤚", state="*")
async def stop_auto_signals(message: types.Message, state: FSMContext):
    try:
        user_id = message.from_user.id

        # Agar foydalanuvchi avto signalni ishga tushirgan bo'lsa
        if user_id in active_signal_task:
            task = active_signal_task[user_id]

            # Agar vazifa hali tugamagan bo'lsa
            if not task.done():
                task.cancel()
                await message.answer("Avtomatik signal yuborish to'xtatildi.")
            else:
                await message.answer("Avtomatik signal allaqachon to'xtatilgan.")
        else:
            await message.answer("Avto signal hozirda ishlamayapti.")
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {e}")
