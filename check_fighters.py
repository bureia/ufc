import sqlite3

try:
    conn = sqlite3.connect("boxing_bot.db")
    cursor = conn.cursor()
    
    # Проверяем таблицы
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("📋 Таблицы в базе:")
    if tables:
        for table in tables:
            print(f"  ✅ {table[0]}")
    else:
        print("  ❌ Таблиц нет!")
    
    # Проверяем бойцов
    print("\n🔍 Проверяем таблицу fighters:")
    try:
        cursor.execute("SELECT COUNT(*) FROM fighters")
        count = cursor.fetchone()[0]
        print(f"  ✅ В таблице {count} бойцов")
        
        if count > 0:
            cursor.execute("SELECT fighter_id, name, rarity FROM fighters LIMIT 10")
            print("\n  Первые 10 бойцов:")
            for fighter_id, name, rarity in cursor.fetchall():
                print(f"    ID: {fighter_id} -> {name} ({rarity})")
    except sqlite3.OperationalError as e:
        print(f"  ❌ Ошибка: {e}")
    
    conn.close()
    
except FileNotFoundError:
    print("❌ Файл boxing_bot.db не существует!")
    print("Сначала запустите бота: python bot.py")