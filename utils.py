import os
from pathlib import Path
from aiogram.types import FSInputFile
from config import PHOTOS_DIR

def get_fighter_photo(fighter_id):
    """Получить фото бойца из папки"""
    extensions = ['.jpg', '.jpeg', '.png', '.gif']
    for ext in extensions:
        photo_path = Path(PHOTOS_DIR) / f"{fighter_id}{ext}"
        if photo_path.exists():
            return FSInputFile(str(photo_path))
    return None

def get_rarity_emoji(rarity):
    """Получить эмодзи для редкости"""
    emojis = {
        'LEGEND': '👑',
        'EPIC': '💎',
        'RARE': '⭐'
    }
    return emojis.get(rarity, '⭐')

def format_fighter_card(fighter, count, total=50):
    """Форматировать карточку бойца"""
    rarity_emoji = get_rarity_emoji(fighter['rarity'])
    return (
        f"❗️{fighter['name']}❗️\n"
        f"❤️Здоровье: {fighter['health']}❤️\n"
        f"👊Урон: {fighter['damage']}👊\n"
        f"💍Редкость: {rarity_emoji} {fighter['rarity']}💍\n"
        f"👑Ты собрал {count} из {total}👑"
    )