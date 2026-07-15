from database import Database

# Создаем базу со всеми таблицами
db = Database()
print("✅ База данных создана!")

# Проверяем
import sqlite3
conn = sqlite3.connect("boxing_bot.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("\n📋 Созданные таблицы:")
for table in tables:
    print(f"  ✅ {table[0]}")

conn.close()