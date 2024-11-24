from aiogram.dispatcher.filters.state import State, StatesGroup

class UserStates(StatesGroup):
    waiting_for_symbols = State()  # Foydalanuvchi kriptolar state
    waiting_for_auto_signal = State()  # Foydalanuvchi avtomatik signal state
    waiting_for_signal_history = State()  # Signal tarixi state
