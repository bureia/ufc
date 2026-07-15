import sqlite3

conn = sqlite3.connect("boxing_bot.db")
cursor = conn.cursor()

# Проверяем промокоды
cursor.execute("SELECT COUNT(*) FROM promo_codes")
count = cursor.fetchone()[0]
print(f"📊 В базе {count} промокодов")

if count > 0:
    print("\nВсе промокоды:")
    cursor.execute("SELECT code, type, fighter_id, case_type, used FROM promo_codes")
    for code, promo_type, fighter_id, case_type, used in cursor.fetchall():
        status = "❌ использован" if used else "✅ активен"
        info = f"боец ID:{fighter_id}" if fighter_id else f"кейс:{case_type}"
        print(f"  {code} - {promo_type} ({info}) - {status}")
else:
    print("\n❌ ПРОМОКОДОВ НЕТ! Нужно добавить.")

# Проверяем конкретный промокод
print("\n🔍 Проверяем tdj24tjk24:")
cursor.execute("SELECT * FROM promo_codes WHERE code = 'tdj24tjk24'")
result = cursor.fetchone()
if result:
    print(f"  ✅ Найден: {result}")
else:
    print("  ❌ НЕ НАЙДЕН!")

conn.close()