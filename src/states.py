from aiogram.fsm.state import State, StatesGroup

class AddKeyword(StatesGroup):
    waiting_for_keyword = State()

class AddCity(StatesGroup):
    waiting_for_city = State()

class SetPrice(StatesGroup):
    waiting_for_price = State()

class SetInterval(StatesGroup):
    waiting_for_interval = State()

class SetCategory(StatesGroup):
    waiting_for_category = State()
