import random
import logging
from typing import Dict, Optional

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

from config import CHANNELS
from database import Database
from fighters_data import FIGHTERS, ROUND_ACTIONS, FREE_FIGHTERS, LEGEND_FIGHTERS, HERO_FIGHTERS
from keyboards import (
    get_subscription_keyboard, get_main_menu_keyboard, get_cases_keyboard,
    get_fighter_selection_keyboard, get_fight_actions_keyboard,
    get_back_keyboard
)
from states import FightStates

logger = logging.getLogger(__name__)

active_fights: Dict[int, Dict] = {}
fight_actions: Dict[int, Dict] = {}

class BoxingHandlers:
    def __init__(self, bot: Bot, db: Database):
        self.bot = bot
        self.db = db

    async def cmd_start(self, message: Message, state: FSMContext):
        user_id = message.from_user.id
        username = message.from_user.username or message.from_user.full_name
        
        self.db.add_user(user_id, username)
        
        user = self.db.get_user(user_id)
        if user and user[2]:
            await message.answer(
                "🥊 Добро пожаловать в Boxing Telegram League!\nВыбери действие:",
                reply_markup=get_main_menu_keyboard()
            )
        else:
            await message.answer(
                "🥊 Побоксируем? Тогда следует подписаться на каналы!\n\n"
                "👇 Подпишись на наши каналы и нажми проверку",
                reply_markup=get_subscription_keyboard()
            )

    async def check_subscription(self, callback: CallbackQuery):
        user_id = callback.from_user.id
        subscribed = True
        
        for channel in CHANNELS:
            try:
                member = await self.bot.get_chat_member(channel["id"], user_id)
                if member.status in ["left", "kicked"]:
                    subscribed = False
                    break
            except Exception:
                subscribed = False
                break
        
        if subscribed:
            self.db.update_subscription(user_id, True)
            await callback.message.delete()
            await callback.message.answer(
                "🥊 Добро пожаловать в Boxing Telegram League!\nВыбери действие:",
                reply_markup=get_main_menu_keyboard()
            )
            await callback.answer("✅ Подписка подтверждена!", show_alert=True)
        else:
            await callback.answer("❌ Вы не подписаны на все каналы!", show_alert=True)

    async def main_menu(self, callback: CallbackQuery):
        try:
            await callback.message.edit_text(
                "🥊 Добро пожаловать в Boxing Telegram League!\nВыбери действие:",
                reply_markup=get_main_menu_keyboard()
            )
        except Exception:
            await callback.message.answer(
                "🥊 Добро пожаловать в Boxing Telegram League!\nВыбери действие:",
                reply_markup=get_main_menu_keyboard()
            )
        await callback.answer()

    async def get_fighter_menu(self, callback: CallbackQuery):
        try:
            await callback.message.edit_text(
                "🎯 Выбери способ получения бойца:\n\n"
                "• Бесплатный кейс - 1 раз\n"
                "• Legend's - нужен промокод\n"
                "• Hero Box - нужен промокод",
                reply_markup=get_cases_keyboard()
            )
        except Exception:
            await callback.message.answer(
                "🎯 Выбери способ получения бойца:\n\n"
                "• Бесплатный кейс - 1 раз\n"
                "• Legend's - нужен промокод\n"
                "• Hero Box - нужен промокод",
                reply_markup=get_cases_keyboard()
            )
        await callback.answer()

    async def open_case(self, callback: CallbackQuery, state: FSMContext):
        user_id = callback.from_user.id
        case_type = callback.data.split("_")[1]
        
        if case_type == "free":
            fighters = self.db.get_user_fighters(user_id)
            if fighters:
                await callback.answer("🫵 Ты уже получил Free бойца!", show_alert=True)
                return
            
            if not FREE_FIGHTERS:
                await callback.answer("❌ Нет доступных бойцов!", show_alert=True)
                return
                
            fighter = random.choice(FREE_FIGHTERS)
            if self.db.add_fighter_to_user(user_id, fighter["id"]):
                # Удаляем сообщение с кнопками
                try:
                    await callback.message.delete()
                except Exception:
                    pass
                # Показываем карточку бойца
                await self.show_fighter_card(callback.message, fighter)
            else:
                await callback.answer("❌ Ошибка при получении бойца", show_alert=True)
                    
        elif case_type in ["legend", "hero"]:
            await state.update_data(case_type=case_type)
            await state.set_state(FightStates.waiting_for_promo)
            
            try:
                await callback.message.edit_text(
                    f"🔑 Введите промокод для активации кейса {case_type.upper()}.\n"
                    "Получить промокод можно в @regioncashbot\n\n"
                    "Введите промокод в сообщении ниже.\n"
                    "Для отмены введите /cancel",
                    reply_markup=get_back_keyboard()
                )
            except Exception:
                await callback.message.answer(
                    f"🔑 Введите промокод для активации кейса {case_type.upper()}.\n"
                    "Получить промокод можно в @regioncashbot\n\n"
                    "Введите промокод в сообщении ниже.\n"
                    "Для отмены введите /cancel",
                    reply_markup=get_back_keyboard()
                )
            await callback.answer()

    async def enter_promo(self, callback: CallbackQuery, state: FSMContext):
        await state.set_state(FightStates.waiting_for_promo)
        try:
            await callback.message.edit_text(
                "🔑 Введите промокод.\n\n"
                "Получить промокод можно в @regioncashbot\n\n"
                "Введите промокод в сообщении ниже.\n"
                "Для отмены введите /cancel",
                reply_markup=get_back_keyboard()
            )
        except Exception:
            await callback.message.answer(
                "🔑 Введите промокод.\n\n"
                "Получить промокод можно в @regioncashbot\n\n"
                "Введите промокод в сообщении ниже.\n"
                "Для отмены введите /cancel",
                reply_markup=get_back_keyboard()
            )
        await callback.answer()

    async def handle_promo(self, message: Message, state: FSMContext):
        if message.text == "/cancel":
            await state.clear()
            await message.answer(
                "❌ Ввод промокода отменен",
                reply_markup=get_main_menu_keyboard()
            )
            return
            
        user_id = message.from_user.id
        promo_code = message.text.strip()
        
        loading_msg = await message.answer("⏳ Проверка промокода...")
        
        try:
            result, msg = self.db.use_promo_code(promo_code, user_id)
            
            if result == "legend":
                if not LEGEND_FIGHTERS:
                    await loading_msg.edit_text("❌ Нет доступных бойцов!")
                    await state.clear()
                    return
                    
                fighter = random.choice(LEGEND_FIGHTERS)
                if self.db.add_fighter_to_user(user_id, fighter["id"]):
                    await loading_msg.delete()
                    await self.show_fighter_card(message, fighter)
                else:
                    await loading_msg.edit_text("❌ Ошибка при открытии кейса")
                    
            elif result == "hero":
                if not HERO_FIGHTERS:
                    await loading_msg.edit_text("❌ Нет доступных бойцов!")
                    await state.clear()
                    return
                    
                fighter = random.choice(HERO_FIGHTERS)
                if self.db.add_fighter_to_user(user_id, fighter["id"]):
                    await loading_msg.delete()
                    await self.show_fighter_card(message, fighter)
                else:
                    await loading_msg.edit_text("❌ Ошибка при открытии кейса")
                    
            elif isinstance(result, int):
                fighter = self.db.get_fighter_by_id(result)
                if fighter:
                    await loading_msg.delete()
                    await self.show_fighter_card(message, fighter)
                else:
                    await loading_msg.edit_text("❌ Боец не найден")
            else:
                await loading_msg.edit_text(f"{msg}")
            
            await state.clear()
            
        except Exception as e:
            logger.error(f"Error in handle_promo: {e}")
            try:
                await loading_msg.edit_text("❌ Произошла ошибка при обработке промокода")
            except:
                await message.answer("❌ Произошла ошибка при обработке промокода")
            await state.clear()

    async def show_fighter_card(self, message: Message, fighter: Dict):
        """Показать карточку бойца"""
        caption = (
            f"❗️ {fighter['name']} ❗️\n"
            f"❤️ Здоровье: {fighter['health']} ❤️\n"
            f"👊 Урон: {fighter['damage']} 👊\n"
            f"💍 Редкость: {fighter['rarity']} 💍\n"
            f"👑 Ты собрал 1 из {len(FIGHTERS)} 👑\n\n"
            f"Нажми /start чтобы продолжить"
        )
        
        try:
            # Пытаемся отправить с фото
            photo = FSInputFile(fighter["image"])
            await message.answer_photo(
                photo=photo,
                caption=caption,
                reply_markup=get_main_menu_keyboard()
            )
        except FileNotFoundError:
            # Если фото нет, отправляем без фото
            await message.answer(
                caption,
                reply_markup=get_main_menu_keyboard()
            )
        except Exception as e:
            logger.error(f"Error showing fighter card: {e}")
            # Если ошибка с фото, отправляем без фото
            await message.answer(
                caption,
                reply_markup=get_main_menu_keyboard()
            )

    async def start_fight_request(self, callback: CallbackQuery, state: FSMContext):
        await state.set_state(FightStates.waiting_for_opponent)
        try:
            await callback.message.edit_text(
                "👊 Введите username своего противника.\n"
                "Например: @Bureia\n\n"
                "Для отмены введите /cancel"
            )
        except Exception:
            await callback.message.answer(
                "👊 Введите username своего противника.\n"
                "Например: @Bureia\n\n"
                "Для отмены введите /cancel"
            )
        await callback.answer()

    async def process_opponent(self, message: Message, state: FSMContext):
        if message.text == "/cancel":
            await state.clear()
            await message.answer(
                "❌ Бой отменен",
                reply_markup=get_main_menu_keyboard()
            )
            return
            
        user_id = message.from_user.id
        username = message.text.strip()
        
        if username.startswith("@"):
            username = username[1:]
        
        conn = None
        try:
            conn = self.db.get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
        except Exception as e:
            logger.error(f"Database error: {e}")
            await message.answer("❌ Ошибка базы данных")
            await state.clear()
            return
        finally:
            if conn:
                conn.close()
        
        if not result:
            await message.answer("🌚 Пользователь не найден")
            await state.clear()
            return
        
        opponent_id = result[0]
        
        if opponent_id == user_id:
            await message.answer("❌ Нельзя играть с самим собой!")
            await state.clear()
            return
        
        fighters1 = self.db.get_user_fighters(user_id)
        fighters2 = self.db.get_user_fighters(opponent_id)
        
        if not fighters1:
            await message.answer("❌ У вас нет бойцов! Сначала получите бойца через 'ПОЛУЧИТЬ БОЙЦА'")
            await state.clear()
            return
            
        if not fighters2:
            await message.answer("❌ У вашего противника нет бойцов!")
            await state.clear()
            return
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"fight_accept_{user_id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"fight_decline_{user_id}")
            ]
        ])
        
        try:
            await self.bot.send_message(
                opponent_id,
                f"🥊 {message.from_user.full_name} (@{message.from_user.username}) отправил вам запрос на поединок!\n"
                f"У него {len(fighters1)} бойцов",
                reply_markup=keyboard
            )
            await message.answer("✅ Запрос отправлен! Ожидайте ответа противника.")
            await state.clear()
        except Exception as e:
            await message.answer("❌ Не удалось отправить запрос. Возможно, пользователь не в боте.")
            logger.error(f"Error sending fight request: {e}")
            await state.clear()

    async def handle_fight_response(self, callback: CallbackQuery):
        try:
            parts = callback.data.split("_")
            if len(parts) < 3:
                await callback.answer("❌ Ошибка в данных", show_alert=True)
                return
                
            action = parts[1]
            opponent_id = int(parts[2])
            user_id = callback.from_user.id
            
            if action == "accept":
                fighters1 = self.db.get_user_fighters(user_id)
                fighters2 = self.db.get_user_fighters(opponent_id)
                
                if not fighters1 or not fighters2:
                    await callback.answer("❌ У одного из игроков нет бойцов!", show_alert=True)
                    return
                
                active_fights[user_id] = {
                    "opponent": opponent_id,
                    "fighters": fighters1,
                    "opponent_fighters": fighters2,
                    "round": 1,
                    "status": "selecting"
                }
                active_fights[opponent_id] = {
                    "opponent": user_id,
                    "fighters": fighters2,
                    "opponent_fighters": fighters1,
                    "round": 1,
                    "status": "selecting"
                }
                
                await self.bot.send_message(
                    user_id,
                    "🥊 Выберите бойца для боя:",
                    reply_markup=get_fighter_selection_keyboard(fighters1, user_id)
                )
                await self.bot.send_message(
                    opponent_id,
                    "🥊 Выберите бойца для боя:",
                    reply_markup=get_fighter_selection_keyboard(fighters2, opponent_id)
                )
                
                try:
                    await callback.message.delete()
                except Exception:
                    pass
                await callback.answer("✅ Бой принят! Выберите бойцов.")
                
            elif action == "decline":
                await self.bot.send_message(
                    opponent_id,
                    f"❌ {callback.from_user.full_name} отклонил ваш запрос на бой."
                )
                try:
                    await callback.message.delete()
                except Exception:
                    pass
                await callback.answer("❌ Вы отклонили бой")
        except (ValueError, IndexError) as e:
            logger.error(f"Error in handle_fight_response: {e}, data: {callback.data}")
            await callback.answer("❌ Ошибка при обработке запроса", show_alert=True)

    async def select_fighter(self, callback: CallbackQuery):
        try:
            parts = callback.data.split("_")
            if len(parts) < 4:
                await callback.answer("❌ Ошибка в данных", show_alert=True)
                return
                
            user_id = int(parts[2])
            fighter_id = int(parts[3])
            current_user_id = callback.from_user.id
            
            if user_id != current_user_id:
                await callback.answer("❌ Это не ваш выбор!")
                return
            
            if user_id not in active_fights:
                await callback.answer("❌ Бой не найден!")
                return
            
            active_fights[user_id]["selected_fighter"] = fighter_id
            try:
                await callback.message.delete()
            except Exception:
                pass
            await callback.answer("✅ Боец выбран! Ожидайте выбора противника.")
            
            opponent_id = active_fights[user_id]["opponent"]
            if opponent_id in active_fights and "selected_fighter" in active_fights[opponent_id]:
                await self.start_match(user_id, opponent_id)
        except (ValueError, IndexError) as e:
            logger.error(f"Error in select_fighter: {e}, data: {callback.data}")
            await callback.answer("❌ Ошибка при выборе бойца", show_alert=True)

    async def start_match(self, player1_id: int, player2_id: int):
        fighter1_id = active_fights[player1_id]["selected_fighter"]
        fighter2_id = active_fights[player2_id]["selected_fighter"]
        
        fighter1 = self.db.get_fighter_by_id(fighter1_id)
        fighter2 = self.db.get_fighter_by_id(fighter2_id)
        
        fight_id = self.db.create_fight(
            player1_id, player2_id, fighter1_id, fighter2_id,
            fighter1["health"], fighter2["health"]
        )
        
        for player_id in [player1_id, player2_id]:
            active_fights[player_id]["fight_id"] = fight_id
            active_fights[player_id]["round"] = 1
            active_fights[player_id]["health"] = fighter1["health"] if player_id == player1_id else fighter2["health"]
            active_fights[player_id]["damage"] = fighter1["damage"] if player_id == player1_id else fighter2["damage"]
            active_fights[player_id]["status"] = "active"
            active_fights[player_id]["fighter_name"] = fighter1["name"] if player_id == player1_id else fighter2["name"]
            active_fights[player_id]["opponent_health"] = fighter2["health"] if player_id == player1_id else fighter1["health"]
        
        message = (
            f"🥊 БОЙ НАЧИНАЕТСЯ! 🥊\n\n"
            f"👊 {fighter1['name']} ❤️{fighter1['health']} vs {fighter2['name']} ❤️{fighter2['health']}\n\n"
            f"Бой состоит из 8 раундов, удачи!\n"
            f"Выбирай атаку и защиту!"
        )
        
        await self.bot.send_message(player1_id, message)
        await self.bot.send_message(player2_id, message)
        
        await self.ask_round_actions(player1_id, 1)
        await self.ask_round_actions(player2_id, 1)

    async def ask_round_actions(self, user_id: int, round_num: int):
        round_data = ROUND_ACTIONS.get(round_num)
        if not round_data:
            round_data = ROUND_ACTIONS[1]
        
        attacks = round_data["attacks"]
        defenses = round_data["defenses"]
        
        keyboard = get_fight_actions_keyboard(attacks, defenses, user_id, round_num)
        
        await self.bot.send_message(
            user_id,
            f"⚔️ РАУНД {round_num} из 8 ⚔️\n\n"
            f"Выбери атаку и защиту:\n"
            f"(сначала выбери атаку, затем защиту)",
            reply_markup=keyboard
        )

    async def select_attack(self, callback: CallbackQuery):
        try:
            parts = callback.data.split("_", 3)
            if len(parts) < 4:
                await callback.answer("❌ Ошибка в данных", show_alert=True)
                return
                
            user_id = int(parts[1])
            round_num = int(parts[2])
            attack = parts[3]
            
            if callback.from_user.id != user_id:
                await callback.answer("❌ Это не ваш ход!")
                return
            
            if user_id not in fight_actions:
                fight_actions[user_id] = {}
            
            fight_actions[user_id]["attack"] = attack
            await callback.answer(f"✅ Атака выбрана: {attack}")
            
            if "defense" in fight_actions[user_id]:
                await self.process_round_actions(user_id, round_num)
        except (ValueError, IndexError) as e:
            logger.error(f"Error in select_attack: {e}, data: {callback.data}")
            await callback.answer("❌ Ошибка при выборе атаки", show_alert=True)

    async def select_defense(self, callback: CallbackQuery):
        try:
            parts = callback.data.split("_", 3)
            if len(parts) < 4:
                await callback.answer("❌ Ошибка в данных", show_alert=True)
                return
                
            user_id = int(parts[1])
            round_num = int(parts[2])
            defense = parts[3]
            
            if callback.from_user.id != user_id:
                await callback.answer("❌ Это не ваш ход!")
                return
            
            if user_id not in fight_actions:
                fight_actions[user_id] = {}
            
            fight_actions[user_id]["defense"] = defense
            await callback.answer(f"✅ Защита выбрана: {defense}")
            
            if "attack" in fight_actions[user_id]:
                await self.process_round_actions(user_id, round_num)
        except (ValueError, IndexError) as e:
            logger.error(f"Error in select_defense: {e}, data: {callback.data}")
            await callback.answer("❌ Ошибка при выборе защиты", show_alert=True)

    async def process_round_actions(self, user_id: int, round_num: int):
        opponent_id = active_fights[user_id]["opponent"]
        
        if opponent_id not in fight_actions or "attack" not in fight_actions[opponent_id] or "defense" not in fight_actions[opponent_id]:
            return
        
        await self.execute_round(user_id, opponent_id, round_num)

    async def execute_round(self, player1_id: int, player2_id: int, round_num: int):
        p1_attack = fight_actions[player1_id]["attack"]
        p1_defense = fight_actions[player1_id]["defense"]
        p2_attack = fight_actions[player2_id]["attack"]
        p2_defense = fight_actions[player2_id]["defense"]
        
        round_data = ROUND_ACTIONS.get(round_num, ROUND_ACTIONS[1])
        multipliers = round_data["multipliers"]
        
        p1_damage = active_fights[player1_id]["damage"]
        p2_damage = active_fights[player2_id]["damage"]
        
        p1_mult = multipliers.get(p2_defense, {}).get(p1_attack, 1)
        p2_mult = multipliers.get(p1_defense, {}).get(p2_attack, 1)
        
        damage_to_p2 = int(p1_damage * p1_mult)
        damage_to_p1 = int(p2_damage * p2_mult)
        
        p1_health = active_fights[player1_id]["health"] - damage_to_p1
        p2_health = active_fights[player2_id]["health"] - damage_to_p2
        
        if p1_health < 0:
            p1_health = 0
        if p2_health < 0:
            p2_health = 0
        
        active_fights[player1_id]["health"] = p1_health
        active_fights[player2_id]["health"] = p2_health
        active_fights[player1_id]["opponent_health"] = p2_health
        active_fights[player2_id]["opponent_health"] = p1_health
        
        fight_id = active_fights[player1_id]["fight_id"]
        self.db.update_fight_health(fight_id, p1_health, p2_health, round_num)
        
        p1_name = active_fights[player1_id]["fighter_name"]
        p2_name = active_fights[player2_id]["fighter_name"]
        
        results = [
            f"🏁 РАУНД {round_num} ОКОНЧЕН 🏁\n",
            f"\n👊 {p1_name}:",
            f"Атаковал - {p1_attack}",
            f"Защищался - {p1_defense}",
            f"❤️ Осталось Здоровье - {p1_health} HP",
            f"✋ Получил - {damage_to_p1} урона",
            f"👊 Нанёс - {damage_to_p2} урона",
            f"\n👊 {p2_name}:",
            f"Атаковал - {p2_attack}",
            f"Защищался - {p2_defense}",
            f"❤️ Осталось Здоровье - {p2_health} HP",
            f"✋ Получил - {damage_to_p2} урона",
            f"👊 Нанёс - {damage_to_p1} урона"
        ]
        
        result_text = "\n".join(results)
        
        await self.bot.send_message(player1_id, result_text)
        await self.bot.send_message(player2_id, result_text)
        
        if player1_id in fight_actions:
            del fight_actions[player1_id]
        if player2_id in fight_actions:
            del fight_actions[player2_id]
        
        if p1_health == 0 or p2_health == 0:
            if p1_health == 0 and p2_health == 0:
                winner_id = None
                result_type = "draw"
            elif p1_health == 0:
                winner_id = player2_id
                result_type = "ko"
            else:
                winner_id = player1_id
                result_type = "ko"
            
            await self.end_match(winner_id, player1_id, player2_id, result_type, p1_health, p2_health)
            return
        
        if round_num >= 8:
            if p1_health > p2_health:
                winner_id = player1_id
            elif p2_health > p1_health:
                winner_id = player2_id
            else:
                winner_id = None
            
            await self.end_match(winner_id, player1_id, player2_id, "decision", p1_health, p2_health)
            return
        
        next_round = round_num + 1
        active_fights[player1_id]["round"] = next_round
        active_fights[player2_id]["round"] = next_round
        
        await self.bot.send_message(
            player1_id,
            f"⏭️ ПЕРЕХОД К РАУНДУ {next_round} ⏭️"
        )
        await self.bot.send_message(
            player2_id,
            f"⏭️ ПЕРЕХОД К РАУНДУ {next_round} ⏭️"
        )
        
        await self.ask_round_actions(player1_id, next_round)
        await self.ask_round_actions(player2_id, next_round)

    async def end_match(self, winner_id: Optional[int], player1_id: int, player2_id: int,
                        result_type: str, p1_health: int, p2_health: int):
        fight_id = active_fights[player1_id]["fight_id"]
        
        if winner_id:
            self.db.end_fight(fight_id, winner_id, result_type)
            
            if result_type == "ko":
                result_msg = f"💥 Победу глухим нокаутом одержал @{self.db.get_username(winner_id)}! 💥"
            else:
                result_msg = f"👨‍⚖️ По единогласному решению судьи победу одержал @{self.db.get_username(winner_id)}! 👨‍⚖️"
        else:
            result_msg = "🤝 Ничья! 🤝"
            self.db.end_fight(fight_id, None, "draw")
        
        result_msg += f"\n\n❤️ Итоговое здоровье:\n@{self.db.get_username(player1_id)}: {p1_health} HP\n@{self.db.get_username(player2_id)}: {p2_health} HP"
        
        await self.bot.send_message(player1_id, result_msg)
        await self.bot.send_message(player2_id, result_msg)
        
        for player in [player1_id, player2_id]:
            if player in active_fights:
                del active_fights[player]
            if player in fight_actions:
                del fight_actions[player]