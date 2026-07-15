import sqlite3
import os

# Если база существует - удаляем
if os.path.exists("boxing_bot.db"):
    os.remove("boxing_bot.db")
    print("🗑️ Старая база удалена")

# Создаем новую базу
conn = sqlite3.connect("boxing_bot.db")
cursor = conn.cursor()

print("📝 Создаем таблицы...")

# 1. Таблица пользователей
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        subscribed BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# 2. Таблица бойцов
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

# 3. Таблица бойцов пользователя
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

# 4. Таблица промокодов
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

# 5. Таблица активных боев
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

print("✅ Таблицы созданы")

# Данные бойцов (154 бойца)
fighters = [
    (1, "Пётр Ян", 2600, 270, "LEGEND", "images/1.jpg"),
    (2, "Джон Джонсон", 2850, 265, "LEGEND", "images/2.jpg"),
    (3, "Хабиб Нурмагомедов", 2950, 230, "LEGEND", "images/3.jpg"),
    (4, "Майк Тайсон", 2700, 300, "LEGEND", "images/4.jpg"),
    (5, "Мухаммед Али", 2900, 260, "LEGEND", "images/5.jpg"),
    (6, "Геннадий Головкин", 2750, 295, "LEGEND", "images/6.jpg"),
    (7, "Фёдор Емельяненко", 2850, 285, "LEGEND", "images/7.jpg"),
    (8, "Конор Макгрегор", 2400, 290, "LEGEND", "images/8.jpg"),
    (9, "Даниел Карнье", 2850, 220, "LEGEND", "images/9.jpg"),
    (10, "Дмитрий Бивол", 2700, 280, "LEGEND", "images/10.jpg"),
    (11, "Канело", 2900, 265, "EPIC", "images/11.jpg"),
    (12, "Деметриус Джонсон", 2600, 220, "EPIC", "images/12.jpg"),
    (13, "Забит Магомедшарипов", 2300, 235, "EPIC", "images/13.jpg"),
    (14, "Найт Диаз", 2400, 200, "EPIC", "images/14.jpg"),
    (15, "Олег Тактаров", 1900, 210, "RARE", "images/15.jpg"),
    (16, "Шарабутдин Магомедов", 2300, 240, "EPIC", "images/16.jpg"),
    (17, "Мирко Кро коп", 2500, 285, "EPIC", "images/17.jpg"),
    (18, "Александр Емельяненко", 2350, 265, "EPIC", "images/18.jpg"),
    (19, "Наоя Иноуэ", 2500, 295, "LEGEND", "images/19.jpg"),
    (20, "Джесси Родригес", 2450, 255, "EPIC", "images/20.jpg"),
    (21, "Шакур Стивенсон", 2100, 225, "RARE", "images/21.jpg"),
    (22, "Александр Усик", 2800, 280, "LEGEND", "images/22.jpg"),
    (23, "Артур Бетербиев", 2600, 280, "EPIC", "images/23.jpg"),
    (24, "Дзунто Накатани", 2000, 230, "RARE", "images/24.jpg"),
    (25, "Девин Гейти", 2500, 240, "EPIC", "images/25.jpg"),
    (26, "Джарон Эннис", 2550, 265, "EPIC", "images/26.jpg"),
    (27, "Дэвид Бенадес", 2600, 270, "EPIC", "images/27.jpg"),
    (28, "Джошуа Ван", 2400, 240, "EPIC", "images/28.jpg"),
    (29, "Алешандре Пантожа", 2550, 240, "EPIC", "images/29.jpg"),
    (30, "Манель Капе", 2200, 235, "RARE", "images/30.jpg"),
    (31, "Тацуро Таира", 2450, 260, "EPIC", "images/31.jpg"),
    (32, "Брэндон Ройвал", 2250, 200, "RARE", "images/32.jpg"),
    (33, "Киоджи Хоригучи", 2300, 200, "RARE", "images/33.jpg"),
    (34, "Тонер Кавана", 2200, 190, "RARE", "images/34.jpg"),
    (35, "Амир Албази", 2500, 200, "RARE", "images/35.jpg"),
    (36, "Ассу Алмабаев", 2450, 245, "EPIC", "images/36.jpg"),
    (37, "Брэндон Морено", 2600, 250, "EPIC", "images/37.jpg"),
    (38, "Алекс Перес", 2100, 230, "RARE", "images/38.jpg"),
    (39, "Тим Эллиотт", 2200, 200, "RARE", "images/39.jpg"),
    (40, "Стефан Эрцзег", 2050, 220, "RARE", "images/40.jpg"),
    (41, "Чарльз Джонсон", 2500, 190, "RARE", "images/41.jpg"),
    (42, "Тагир Уланбеков", 2550, 180, "RARE", "images/42.jpg"),
    (43, "Бруно Силва", 1900, 175, "RARE", "images/43.jpg"),
    (44, "Мераб Двалишвили", 2900, 230, "EPIC", "images/44.jpg"),
    (45, "Умар Нурмагомедов", 2550, 250, "EPIC", "images/45.jpg"),
    (46, "Шон О'Мэлли", 2350, 270, "EPIC", "images/46.jpg"),
    (47, "Кори Сэндхаген", 2300, 240, "EPIC", "images/47.jpg"),
    (48, "Ядонг Сонг", 2200, 270, "EPIC", "images/48.jpg"),
    (49, "Айеман Захаби", 2100, 245, "RARE", "images/49.jpg"),
    (50, "Дейвисон Фигередо", 2400, 265, "EPIC", "images/50.jpg"),
    (51, "Марио Баутиста", 2250, 230, "RARE", "images/51.jpg"),
    (52, "Дэвид Мартинес", 2400, 210, "RARE", "images/52.jpg"),
    (53, "Марлон Вера", 2050, 230, "RARE", "images/53.jpg"),
    (54, "Пэйтон Тэлботт", 2350, 240, "RARE", "images/54.jpg"),
    (55, "Винисиус де Оливейра", 2400, 215, "RARE", "images/55.jpg"),
    (56, "Рауль Росас Джуниор", 2200, 210, "RARE", "images/56.jpg"),
    (57, "Монтел Джексон", 2200, 215, "RARE", "images/57.jpg"),
    (58, "Фарид Башарат", 2100, 180, "RARE", "images/58.jpg"),
    (59, "Александр Волкановский", 2750, 255, "LEGEND", "images/59.jpg"),
    (60, "Мовсар Елоев", 2650, 230, "EPIC", "images/60.jpg"),
    (61, "Диего Лопес", 2500, 255, "EPIC", "images/61.jpg"),
    (62, "Лерон Мерфи", 2450, 245, "EPIC", "images/62.jpg"),
    (63, "Яир Родригес", 2400, 260, "EPIC", "images/63.jpg"),
    (64, "Алджамейн Стерлинг", 2550, 240, "EPIC", "images/64.jpg"),
    (65, "Жан Сильва", 2350, 240, "RARE", "images/65.jpg"),
    (66, "Юссеф Залал", 2350, 240, "RARE", "images/66.jpg"),
    (67, "Арнольд Аллен", 2450, 240, "EPIC", "images/67.jpg"),
    (68, "Стив Гарсия", 2400, 225, "RARE", "images/68.jpg"),
    (69, "Кевин Вальехос", 2000, 225, "RARE", "images/69.jpg"),
    (70, "Брайан Ортега", 2750, 160, "EPIC", "images/70.jpg"),
    (71, "Мелкуизель Коста", 1800, 235, "RARE", "images/71.jpg"),
    (72, "Патрисио Фрейре", 2500, 250, "EPIC", "images/72.jpg"),
    (73, "Давид Онама", 2300, 170, "RARE", "images/73.jpg"),
    (74, "Джош Эммет", 1900, 230, "RARE", "images/74.jpg"),
    (75, "Илья Топурия", 2550, 285, "LEGEND", "images/75.jpg"),
    (76, "Джастин Гэйтжи", 2400, 290, "EPIC", "images/76.jpg"),
    (77, "Арман Царукян", 2600, 265, "EPIC", "images/77.jpg"),
    (78, "Чарльз Оливейра", 2550, 260, "LEGEND", "images/78.jpg"),
    (79, "Макс Холлоуэй", 2850, 260, "LEGEND", "images/79.jpg"),
    (80, "Бенуа Сен-Дени", 2500, 235, "RARE", "images/80.jpg"),
    (81, "Пэдди Пимблетт", 2500, 235, "EPIC", "images/81.jpg"),
    (82, "Дэн Хукер", 2450, 225, "RARE", "images/82.jpg"),
    (83, "Матеуш Гэмрот", 2500, 245, "EPIC", "images/83.jpg"),
    (84, "Ренато Мойкано", 2150, 250, "RARE", "images/84.jpg"),
    (85, "Маурисио Раффи", 2350, 245, "RARE", "images/85.jpg"),
    (86, "Рафаэль Физиев", 2450, 260, "EPIC", "images/86.jpg"),
    (87, "Бенил Дариуш", 2400, 205, "RARE", "images/87.jpg"),
    (88, "Майкл Чендлер", 2000, 275, "EPIC", "images/88.jpg"),
    (89, "Мануель Торрес", 1800, 235, "RARE", "images/89.jpg"),
    (90, "Фарес Зиам", 1850, 200, "RARE", "images/90.jpg"),
    (91, "Ислам Махачев", 2850, 275, "LEGEND", "images/91.jpg"),
    (92, "Джек делла Маддалена", 2450, 250, "EPIC", "images/92.jpg"),
    (93, "Иэн Мачадо Гэрри", 2400, 255, "EPIC", "images/93.jpg"),
    (94, "Майкл Моралес", 2400, 245, "EPIC", "images/94.jpg"),
    (95, "Белал Мухаммад", 2600, 230, "EPIC", "images/95.jpg"),
    (96, "Карлос Пратес", 2600, 255, "EPIC", "images/96.jpg"),
    (97, "Шон Брэди", 2200, 225, "RARE", "images/97.jpg"),
    (98, "Камару Усман", 2650, 250, "EPIC", "images/98.jpg"),
    (99, "Леон Эдвардс", 2550, 245, "EPIC", "images/99.jpg"),
    (100, "Хоакин Бакли", 2450, 265, "EPIC", "images/100.jpg"),
    (101, "Габриэль Бонфим", 2200, 205, "RARE", "images/101.jpg"),
    (102, "Гилберт Бернс", 2300, 220, "RARE", "images/102.jpg"),
    (103, "Майкл Пейдж", 2100, 250, "RARE", "images/103.jpg"),
    (104, "Урош Медич", 2350, 190, "RARE", "images/104.jpg"),
    (105, "Даниель Родригес", 2150, 195, "RARE", "images/105.jpg"),
    (106, "Колби Ковингтон", 2300, 200, "RARE", "images/106.jpg"),
    (107, "Хамзат Чимаев", 2750, 280, "LEGEND", "images/107.jpg"),
    (108, "Дрикус Дю Плесси", 2600, 275, "EPIC", "images/108.jpg"),
    (109, "Нассурдин Имавов", 2500, 255, "EPIC", "images/109.jpg"),
    (110, "Шон Стрикленд", 2650, 240, "EPIC", "images/110.jpg"),
    (111, "Брендан Аллен", 2500, 250, "EPIC", "images/111.jpg"),
    (112, "Кайо Борральо", 2250, 250, "EPIC", "images/112.jpg"),
    (113, "Джо Пайфер", 2350, 240, "RARE", "images/113.jpg"),
    (114, "Энтони Эрнандес", 2400, 200, "RARE", "images/114.jpg"),
    (115, "Рейньер де Риддер", 2250, 190, "RARE", "images/115.jpg"),
    (116, "Исраэль Адесанья", 2500, 270, "EPIC", "images/116.jpg"),
    (117, "Роберт Уиттакер", 2200, 265, "EPIC", "images/117.jpg"),
    (118, "Джаред Каннонье", 2000, 240, "RARE", "images/118.jpg"),
    (119, "Грегори Родригес", 2400, 195, "RARE", "images/119.jpg"),
    (120, "Марио Баутиста", 2150, 205, "RARE", "images/120.jpg"),
    (121, "Дэвид Мартинес", 2250, 265, "EPIC", "images/121.jpg"),
    (122, "Роман Долидзе", 2000, 210, "RARE", "images/122.jpg"),
    (123, "Алекс Перейра", 2550, 300, "LEGEND", "images/123.jpg"),
    (124, "Магомед Анкалаев", 2600, 280, "EPIC", "images/124.jpg"),
    (125, "Иржи Прохазка", 2500, 280, "EPIC", "images/125.jpg"),
    (126, "Карлос Ульберг", 2450, 260, "EPIC", "images/126.jpg"),
    (127, "Халил Рунтри", 2450, 275, "EPIC", "images/127.jpg"),
    (128, "Ян Блахович", 2600, 250, "EPIC", "images/128.jpg"),
    (129, "Азамат Мурзаканов", 2500, 240, "EPIC", "images/129.jpg"),
    (130, "Джамал Хилл", 2350, 275, "EPIC", "images/130.jpg"),
    (131, "Богдан Гуськов", 2000, 240, "RARE", "images/131.jpg"),
    (132, "Волкан Оздемир", 2400, 205, "RARE", "images/132.jpg"),
    (133, "Доминик Рейес", 2050, 260, "RARE", "images/133.jpg"),
    (134, "Александр Ракич", 2500, 250, "EPIC", "images/134.jpg"),
    (135, "Джонни Уокер", 2350, 265, "RARE", "images/135.jpg"),
    (136, "Никита Крылов", 2400, 230, "EPIC", "images/136.jpg"),
    (137, "Дастин Джейкоби", 2100, 190, "RARE", "images/137.jpg"),
    (138, "Минган Чжан", 2000, 220, "RARE", "images/138.jpg"),
    (139, "Том Аспинэлл", 2650, 280, "EPIC", "images/139.jpg"),
    (140, "Сирил Ган", 2500, 255, "EPIC", "images/140.jpg"),
    (141, "Александр Волков", 2700, 275, "EPIC", "images/141.jpg"),
    (142, "Сергей Павлович", 2500, 290, "EPIC", "images/142.jpg"),
    (143, "Валдо Кортес-Акоста", 2450, 255, "EPIC", "images/143.jpg"),
    (144, "Кертис Блейдс", 2750, 265, "EPIC", "images/144.jpg"),
    (145, "Сергей Спивак", 2600, 250, "EPIC", "images/145.jpg"),
    (146, "Ризван Куниев", 2250, 200, "RARE", "images/146.jpg"),
    (147, "Деррик Льюис", 2250, 285, "EPIC", "images/147.jpg"),
    (148, "Анте Делия", 2150, 200, "RARE", "images/148.jpg"),
    (149, "Тайрелл Форчун", 2400, 220, "EPIC", "images/149.jpg"),
    (150, "Марчин Тыбура", 2150, 230, "RARE", "images/150.jpg"),
    (151, "Таллисон Тейшейра", 2200, 250, "RARE", "images/151.jpg"),
    (152, "Шамиль Газиев", 2050, 250, "RARE", "images/152.jpg"),
    (153, "Майкл Паркин", 2100, 190, "RARE", "images/153.jpg"),
    (154, "Маурисио Раффи", 2350, 170, "RARE", "images/154.jpg"),
]

print(f"📝 Добавляем {len(fighters)} бойцов...")

# Добавляем бойцов
for fighter in fighters:
    cursor.execute('''
        INSERT OR IGNORE INTO fighters (fighter_id, name, health, damage, rarity, image)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', fighter)

conn.commit()

# Проверяем результат
cursor.execute("SELECT COUNT(*) FROM fighters")
count = cursor.fetchone()[0]
print(f"✅ Добавлено {count} бойцов")

# Показываем первых 10
cursor.execute("SELECT fighter_id, name, rarity FROM fighters LIMIT 10")
print("\n📋 Первые 10 бойцов:")
for fighter_id, name, rarity in cursor.fetchall():
    print(f"  ID: {fighter_id} -> {name} ({rarity})")

# Считаем по редкостям
cursor.execute("SELECT rarity, COUNT(*) FROM fighters GROUP BY rarity")
print("\n📊 Статистика по редкостям:")
for rarity, count in cursor.fetchall():
    print(f"  {rarity}: {count}")

conn.close()

print("\n" + "="*50)
print("✅ БАЗА ДАННЫХ УСПЕШНО СОЗДАНА!")
print("="*50)
print("\nТеперь:")
print("1. Добавьте промокоды: python add_promos_now.py")
print("2. Запустите бота: python bot.py")