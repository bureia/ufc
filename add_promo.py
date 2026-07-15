from database import Database

db = Database()

# Промокоды на бойцов
fighter_promos = {
    "tdj24tjk24": 8,
    "madboxer25": 10,
    "defolt1099": 16,
    "defolt1799": 16,
    "defolt499": 16,
    "brat22": 18,
    "brat1": 18,
    "22gruziya": 44,
    "gruziya22": 44,
    "lomafff444": 23,
    "ShonSSS": 46,
    "Toys375": 46,
    "austral934234": 59,
    "5325austral": 59,
    "dagestansila": 91,
    "r4jfdjfs44ked46": 91,
    "sweden565654": 107,
    "1577": 107,
    "Waxek77": 75,
    "alibaba4": 76,
    "hu11gan": 77,
    "lolipop94": 141,
    "va1erka2": 78,
    "you587329": 110,
}

print("Добавление промокодов на бойцов:")
for code, fighter_id in fighter_promos.items():
    try:
        db.add_promo_code(code, "fighter", fighter_id=fighter_id)
        print(f"✅ {code} -> боец ID: {fighter_id}")
    except Exception as e:
        print(f"❌ Ошибка при добавлении {code}: {e}")

# Промокоды на кейсы
case_promos = {
    "ufcchemp": "legend",
    "open220": "legend",
    "ufcchemp66": "hero",
    "open290": "legend",
    "florian1": "hero",
    "florian2": "hero",
    "florian3": "hero",
    "vax1": "hero",
    "vax2": "hero",
    "vax3": "hero",
}

print("\nДобавление промокодов на кейсы:")
for code, case_type in case_promos.items():
    try:
        db.add_promo_code(code, "case", case_type=case_type)
        print(f"✅ {code} -> кейс: {case_type}")
    except Exception as e:
        print(f"❌ Ошибка при добавлении {code}: {e}")

print("\n✅ ВСЕ ПРОМОКОДЫ ДОБАВЛЕНЫ!")
print("\n📝 Список промокодов:")
print("Бойцы:", ", ".join(fighter_promos.keys()))
print("Кейсы:", ", ".join(case_promos.keys()))