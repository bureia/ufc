import sqlite3
import os

# 1. Удаляем старую базу если есть
if os.path.exists("boxing_bot.db"):
    os.remove("boxing_bot.db")
    print("🗑️ Старая база удалена")

# 2. Создаем новую базу со всеми таблицами
from database import Database
db = Database()
print("✅ Новая база создана")

# 3. Добавляем промокоды напрямую
conn = sqlite3.connect("boxing_bot.db")
cursor = conn.cursor()

# Убеждаемся что таблица существует
cursor.execute('''
    CREATE TABLE IF NOT EXISTS promo_codes (
        code TEXT PRIMARY KEY,
        type TEXT,
        fighter_id INTEGER,
        case_type TEXT,
        used BOOLEAN DEFAULT FALSE,
        used_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

# Добавляем промокоды
promos = [
    ("habib2024", "fighter", 1, None),
    ("conor2024", "fighter", 2, None),
    ("tyson2024", "fighter", 3, None),
    ("ali2024", "fighter", 4, None),
    ("mayweather2024", "fighter", 5, None),
    ("fury2024", "fighter", 6, None),
    ("joshua2024", "fighter", 7, None),
    ("lomachenko2024", "fighter", 8, None),
    ("legend2024", "case", None, "legend"),
    ("legend2025", "case", None, "legend"),
    ("hero2024", "case", None, "hero"),
    ("hero2025", "case", None, "hero"),
]

print("\n📝 Добавляем промокоды:")
for code, promo_type, fighter_id, case_type in promos:
    try:
        cursor.execute(
            "INSERT INTO promo_codes (code, type, fighter_id, case_type, used, used_by) VALUES (?, ?, ?, ?, ?, ?)",
            (code, promo_type, fighter_id, case_type, 0, None)
        )
        print(f"  ✅ {code}")
    except Exception as e:
        print(f"  ❌ {code}: {e}")

conn.commit()

# Проверяем что добавилось
cursor.execute("SELECT code, type FROM promo_codes")
results = cursor.fetchall()
print(f"\n📊 Всего промокодов в базе: {len(results)}")

for code, promo_type in results:
    print(f"  {code} - {promo_type}")

conn.close()

print("\n" + "="*50)
print("✅ ВСЕ ГОТОВО!")
print("="*50)
print("\nТеперь:")
print("1. Запустите бота: python bot.py")
print("2. Введите /start")
print("3. Нажмите 'ВВЕСТИ ПРОМОКОД'")
print("4. Введите: habib2024")
print("5. Должен появиться Хабиб Нурмагомедов!")