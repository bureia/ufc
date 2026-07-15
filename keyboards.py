from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import CHANNELS

def get_subscription_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для подписки"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    for channel in CHANNELS:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text=f"📢 ПОДПИСАТЬСЯ", url=f"https://t.me/{channel['id'].replace('@', '')}")
        ])
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="✅ ПРОВЕРИТЬ ПОДПИСКУ", callback_data="check_sub")
    ])
    
    return keyboard

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 ПОЛУЧИТЬ БОЙЦА", callback_data="get_fighter")],
        [InlineKeyboardButton(text="🥊 СЫГРАТЬ", callback_data="start_fight")],
        [InlineKeyboardButton(text="🔑 ВВЕСТИ ПРОМОКОД", callback_data="enter_promo")]
    ])

def get_cases_keyboard() -> InlineKeyboardMarkup:
    """Меню кейсов"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 БЕСПЛАТНЫЙ КЕЙС", callback_data="case_free")],
        [InlineKeyboardButton(text="💎 LEGEND'S", callback_data="case_legend")],
        [InlineKeyboardButton(text="📦 Hero Box", callback_data="case_hero")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
    ])

def get_fighter_selection_keyboard(fighters: list, user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора бойца"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for fighter in fighters:
        fighter_id, name, health, damage, rarity, _ = fighter
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{name} (❤️{health} 👊{damage} 💍{rarity})",
                callback_data=f"select_fighter_{user_id}_{fighter_id}"
            )
        ])
    return keyboard

def get_fight_actions_keyboard(attacks: list, defenses: list, user_id: int, round_num: int) -> InlineKeyboardMarkup:
    """Клавиатура для атаки и защиты"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    for attack in attacks:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text=f"⚔️ {attack}", callback_data=f"attack_{user_id}_{round_num}_{attack}")
        ])
    
    for defense in defenses:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text=f"🛡️ {defense}", callback_data=f"defense_{user_id}_{round_num}_{defense}")
        ])
    
    return keyboard

def get_back_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой назад"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
    ])