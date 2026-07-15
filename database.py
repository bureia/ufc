import sqlite3
from typing import List, Optional, Tuple, Dict
from fighters_data import FIGHTERS

class Database:
    def __init__(self, db_name="boxing_bot.db"):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                subscribed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Проверяем, есть ли колонка subscribed
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'subscribed' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN subscribed BOOLEAN DEFAULT FALSE")
        
        # Таблица бойцов пользователя
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_fighters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                fighter_id INTEGER,
                obtained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (fighter_id) REFERENCES fighters(fighter_id),
                UNIQUE(user_id, fighter_id)
            )
        ''')
        
        # Таблица бойцов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fighters (
                fighter_id INTEGER PRIMARY KEY,
                name TEXT,
                health INTEGER,
                damage INTEGER,
                rarity TEXT,
                image TEXT
            )
        ''')
        
        # Таблица промокодов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS promo_codes (
                code TEXT PRIMARY KEY,
                type TEXT,
                fighter_id INTEGER,
                case_type TEXT,
                used BOOLEAN DEFAULT FALSE,
                used_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (fighter_id) REFERENCES fighters(fighter_id),
                FOREIGN KEY (used_by) REFERENCES users(user_id)
            )
        ''')
        
        # Проверяем, есть ли колонка used_by
        cursor.execute("PRAGMA table_info(promo_codes)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'used_by' not in columns:
            cursor.execute("ALTER TABLE promo_codes ADD COLUMN used_by INTEGER")
        
        # Таблица активных боев
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS active_fights (
                fight_id INTEGER PRIMARY KEY AUTOINCREMENT,
                player1_id INTEGER,
                player2_id INTEGER,
                player1_fighter_id INTEGER,
                player2_fighter_id INTEGER,
                current_round INTEGER DEFAULT 1,
                player1_health INTEGER,
                player2_health INTEGER,
                status TEXT DEFAULT 'active',
                winner_id INTEGER,
                result_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player1_id) REFERENCES users(user_id),
                FOREIGN KEY (player2_id) REFERENCES users(user_id)
            )
        ''')
        
        # Добавляем бойцов если их нет
        for fighter in FIGHTERS:
            cursor.execute('''
                INSERT OR IGNORE INTO fighters (fighter_id, name, health, damage, rarity, image)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (fighter["id"], fighter["name"], fighter["health"], fighter["damage"], fighter["rarity"], fighter["image"]))
        
        conn.commit()
        conn.close()

    def get_user(self, user_id: int) -> Optional[Tuple]:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result

    def add_user(self, user_id: int, username: str):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (user_id, username, subscribed) VALUES (?, ?, ?)", 
                      (user_id, username, False))
        conn.commit()
        conn.close()

    def update_subscription(self, user_id: int, subscribed: bool):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET subscribed = ? WHERE user_id = ?", (subscribed, user_id))
        conn.commit()
        conn.close()

    def get_user_fighters(self, user_id: int) -> List[Tuple]:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT f.fighter_id, f.name, f.health, f.damage, f.rarity, f.image
            FROM user_fighters uf
            JOIN fighters f ON uf.fighter_id = f.fighter_id
            WHERE uf.user_id = ?
        ''', (user_id,))
        result = cursor.fetchall()
        conn.close()
        return result

    def add_fighter_to_user(self, user_id: int, fighter_id: int) -> bool:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO user_fighters (user_id, fighter_id) VALUES (?, ?)", (user_id, fighter_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def add_promo_code(self, code: str, type: str, fighter_id: int = None, case_type: str = None):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO promo_codes (code, type, fighter_id, case_type, used, used_by) VALUES (?, ?, ?, ?, ?, ?)",
            (code, type, fighter_id, case_type, False, None)
        )
        conn.commit()
        conn.close()

    def use_promo_code(self, code: str, user_id: int) -> Tuple[Optional[int], str]:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute("SELECT type, fighter_id, case_type, used, used_by FROM promo_codes WHERE code = ?", (code,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return None, "❌ Промокод не найден"
        
        promo_type, fighter_id, case_type, used, used_by = result
        
        if used:
            conn.close()
            return None, "❌ Этот промокод уже использован!"
        
        if used_by and used_by == user_id:
            conn.close()
            return None, "❌ Вы уже использовали этот промокод!"
        
        if promo_type == "fighter" and fighter_id:
            if self.add_fighter_to_user(user_id, fighter_id):
                cursor.execute(
                    "UPDATE promo_codes SET used = TRUE, used_by = ? WHERE code = ?",
                    (user_id, code)
                )
                conn.commit()
                conn.close()
                return fighter_id, "✅ Боец успешно получен!"
            else:
                conn.close()
                return None, "❌ У вас уже есть этот боец!"
                
        elif promo_type == "case":
            cursor.execute(
                "UPDATE promo_codes SET used = TRUE, used_by = ? WHERE code = ?",
                (user_id, code)
            )
            conn.commit()
            conn.close()
            return case_type, "✅ Кейс активирован!"
        
        conn.close()
        return None, "❌ Неизвестный тип промокода"

    def create_fight(self, player1_id: int, player2_id: int, fighter1_id: int, fighter2_id: int,
                     health1: int, health2: int) -> int:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO active_fights 
            (player1_id, player2_id, player1_fighter_id, player2_fighter_id, player1_health, player2_health)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (player1_id, player2_id, fighter1_id, fighter2_id, health1, health2))
        fight_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return fight_id

    def get_fight(self, fight_id: int) -> Optional[Tuple]:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM active_fights WHERE fight_id = ?", (fight_id,))
        result = cursor.fetchone()
        conn.close()
        return result

    def update_fight_health(self, fight_id: int, player1_health: int, player2_health: int, current_round: int):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE active_fights 
            SET player1_health = ?, player2_health = ?, current_round = ?
            WHERE fight_id = ?
        ''', (player1_health, player2_health, current_round, fight_id))
        conn.commit()
        conn.close()

    def end_fight(self, fight_id: int, winner_id: Optional[int], result_type: str):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE active_fights SET status = 'finished', winner_id = ?, result_type = ? WHERE fight_id = ?",
            (winner_id, result_type, fight_id)
        )
        conn.commit()
        conn.close()

    def get_fighter_by_id(self, fighter_id: int) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fighters WHERE fighter_id = ?", (fighter_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return {
                "id": result[0],
                "name": result[1],
                "health": result[2],
                "damage": result[3],
                "rarity": result[4],
                "image": result[5]
            }
        return None
    
    def get_username(self, user_id: int) -> str:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else str(user_id)
    
    def get_db(self):
        return sqlite3.connect(self.db_name)