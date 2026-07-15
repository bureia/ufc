import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command

from config import BOT_TOKEN
from database import Database
from handlers import BoxingHandlers
from states import FightStates

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
db = Database()

handlers = BoxingHandlers(bot, db)

async def register_handlers():
    dp.message.register(handlers.cmd_start, Command("start"))
    dp.message.register(handlers.cmd_start, Command("menu"))
    
    dp.message.register(handlers.handle_promo, FightStates.waiting_for_promo)
    dp.message.register(handlers.process_opponent, FightStates.waiting_for_opponent)
    
    dp.callback_query.register(handlers.check_subscription, lambda c: c.data == "check_sub")
    dp.callback_query.register(handlers.main_menu, lambda c: c.data == "main_menu")
    dp.callback_query.register(handlers.get_fighter_menu, lambda c: c.data == "get_fighter")
    dp.callback_query.register(handlers.open_case, lambda c: c.data.startswith("case_"))
    dp.callback_query.register(handlers.enter_promo, lambda c: c.data == "enter_promo")
    dp.callback_query.register(handlers.start_fight_request, lambda c: c.data == "start_fight")
    dp.callback_query.register(handlers.handle_fight_response, lambda c: c.data.startswith("fight_"))
    dp.callback_query.register(handlers.select_fighter, lambda c: c.data.startswith("select_fighter_"))
    dp.callback_query.register(handlers.select_attack, lambda c: c.data.startswith("attack_"))
    dp.callback_query.register(handlers.select_defense, lambda c: c.data.startswith("defense_"))
    
    dp.message.register(lambda m, s: s.clear() if m.text == "/cancel" else None, Command("cancel"))

async def main():
    await register_handlers()
    logger.info("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())