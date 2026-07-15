import sqlite3
import os

# Проверяем наличие файла
if os.path.exists("boxing_bot.db"):
    print("✅ Файл boxing_bot.db существует")
    
    # Проверяем содержимое
    conn = sqlite3.connect("boxing_bot.db")
    cursor = conn.cursor()
    
    # Проверяем таблицу promo_codes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='promo_codes'")
    if cursor.fetchone():
        print("✅ Таблица promo_codes существует")
        
        cursor.execute("SELECT COUNT(*) FROM promo_codes")
        count = cursor.fetchone()[0]
        print(f"📊 В таблице {count} промокодов")
        
        if count > 0:
            cursor.execute("SELECT * FROM promo_codes")
            for row in cursor.fetchall():
                print(f"  {row}")
        else:
            print("❌ В таблице нет промокодов!")
    else:
        print("❌ Таблица promo_codes не существует!")
    
    conn.close()
else:
    print("❌ Файл boxing_bot.db не существует!")