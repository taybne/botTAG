from aiogram.fsm.state import State, StatesGroup

class AddLocation(StatesGroup):
    name = State()
    description = State()
    city = State()
    country = State()
    photos = State()

class Feedback(StatesGroup):
    review = State()
    problem = State()