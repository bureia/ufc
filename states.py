from aiogram.fsm.state import State, StatesGroup

class FightStates(StatesGroup):
    waiting_for_opponent = State()
    waiting_for_promo = State()
    waiting_for_fighter_selection = State()