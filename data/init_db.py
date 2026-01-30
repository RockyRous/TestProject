import csv
import sqlite3
import re
from pathlib import Path

SOURCE_CSV = "table.csv"
DB_PATH = "products.db"

Path("").mkdir(exist_ok=True)

def parse_float(value: str):
    if not value:
        return None
    value = value.replace(",", ".")
    match = re.search(r"\d+(\.\d+)?", value)
    return float(match.group()) if match else None

def parse_int(value: str):
    if not value:
        return None
    match = re.search(r"\d+", value)
    return int(match.group()) if match else None

def clean_text(value: str):
    return value.strip() if value else None

def normalize_color(value):
    if not value:
        return None
    return value.lower().replace(" ", "").replace("-", "")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS products")
cursor.execute("""
CREATE TABLE products (
    model TEXT,
    name TEXT,
    type TEXT,
    construction_type TEXT,
    color TEXT,
    volume_l REAL,
    heaters_count INTEGER,
    programs_count INTEGER,
    power_w INTEGER,
    programs TEXT,
    features TEXT,
    equipment TEXT
)
""")

with open(SOURCE_CSV, encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        model = clean_text(row.get("Артикул"))
        if not model:
            continue  # пропускаем строки без модели

        name = clean_text(row.get("Название модели"))
        type_ = clean_text(row.get("Тип конструкции"))
        construction_type = clean_text(row.get("Тип конструкции"))
        color = normalize_color(row.get("Цвет"))

        volume_l = parse_float(row.get("Объем, л"))
        heaters_count = parse_int(row.get("Кол-во ТЭНов"))
        programs_count = parse_int(row.get("Кол-во программ"))
        power_w = parse_int(row.get("Мощность, Вт"))

        programs = clean_text(row.get("Список программ"))
        if programs:
            programs = programs.lower()
        features = clean_text(row.get("Особенности"))
        equipment = clean_text(row.get("Комплектация"))

        cursor.execute("""
            INSERT INTO products VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        """, (
            model,
            name,
            type_,
            construction_type,
            color,
            volume_l,
            heaters_count,
            programs_count,
            power_w,
            programs,
            features,
            equipment
        ))

conn.commit()

# 🔍 Печать результата
cursor.execute("SELECT * FROM products")
rows = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]

print("\n=== PRODUCTS TABLE ===")
print(" | ".join(columns))
print("-" * 120)

for row in rows:
    print(" | ".join(str(v) if v is not None else "NULL" for v in row))

conn.close()

print(f"\n✅ Database created: {DB_PATH}")
print(f"✅ Rows inserted: {len(rows)}")
