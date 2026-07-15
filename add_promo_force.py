import sqlite3
from database import Database

# Создаем базу
db = Database()

# Подключаемся напрямую
conn = sqlite3.connect("boxing_bot.db")
cursor = conn.cursor()

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

print("Добавляем промокоды:")
for code, promo_type, fighter_id, case_type in promos:
    try:
        cursor.execute(
            "INSERT OR REPLACE INTO promo_codes (code, type, fighter_id, case_type, used, used_by) VALUES (?, ?, ?, ?, ?, ?)",
            (code, promo_type, fighter_id, case_type, 0, None)
        )
        print(f"✅ {code}")
    except Exception as e:
        print(f"❌ Ошибка: {code} - {e}")

conn.commit()
conn.close()

print("\n✅ Все промокоды добавлены!")
print("Промокоды для бойцов:")
print("  habib2024 - Хабиб Нурмагомедов")
print("  conor2024 - Конор Макгрегор")
print("  tyson2024 - Майк Тайсон")
print("  ali2024 - Мохаммед Али")
print("  mayweather2024 - Флойд Мейвезер")
print("  fury2024 - Тайсон Фьюри")
print("  joshua2024 - Энтони Джошуа")
print("  lomachenko2024 - Василий Ломаченко")
print("\nПромокоды для кейсов:")
print("  legend2024 - Кейс LEGEND'S")
print("  legend2025 - Кейс LEGEND'S")
print("  hero2024 - Кейс Hero Box")
print("  hero2025 - Кейс Hero Box")