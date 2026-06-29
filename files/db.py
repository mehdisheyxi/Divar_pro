# db.py
# مدیریت دیتابیس SQLite برای ذخیره‌ی آگهی‌های قیمت موبایل در شهرهای مختلف

import sqlite3
from datetime import datetime, timezone

from config import DB_PATH, ALL_CITIES, BENCHMARK_CITY


SCHEMA = """
CREATE TABLE IF NOT EXISTS cities (
    id INTEGER PRIMARY KEY,        -- city_id واقعی دیوار
    name TEXT NOT NULL UNIQUE,
    is_benchmark INTEGER NOT NULL DEFAULT 0   -- 1 = مثل "کل ایران"، خارج از رتبه‌بندی شهرها
);

CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_at TEXT NOT NULL            -- ISO 8601 timestamp (UTC)
);

CREATE TABLE IF NOT EXISTS listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL REFERENCES runs(id),
    city_id INTEGER NOT NULL REFERENCES cities(id),
    model_key TEXT NOT NULL,        -- مثلا '1'
    model_name TEXT NOT NULL,       -- مثلا 'iphone 17 pro max'
    title TEXT,
    price_raw TEXT,                 -- متن خام قیمت از دیوار
    price_toman INTEGER,            -- قیمت پارس‌شده (تومان)، NULL اگر قابل تفسیر نبود
    scraped_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_listings_run ON listings(run_id);
CREATE INDEX IF NOT EXISTS idx_listings_city_model ON listings(city_id, model_name);
"""


def get_connection(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path=DB_PATH):
    """ساخت جدول‌ها (اگر نبودند) و پر کردن جدول شهرها از config.py"""
    conn = get_connection(db_path)
    try:
        conn.executescript(SCHEMA)

        for name, city_id in ALL_CITIES.items():
            is_benchmark = 1 if name in BENCHMARK_CITY else 0
            conn.execute(
                """
                INSERT INTO cities (id, name, is_benchmark)
                VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET name=excluded.name,
                                               is_benchmark=excluded.is_benchmark
                """,
                (city_id, name, is_benchmark),
            )
        conn.commit()
    finally:
        conn.close()


def create_run(db_path=DB_PATH):
    """یک رکورد run جدید می‌سازد و id آن را برمی‌گرداند."""
    conn = get_connection(db_path)
    try:
        run_at = datetime.now(timezone.utc).isoformat()
        cur = conn.execute("INSERT INTO runs (run_at) VALUES (?)", (run_at,))
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def insert_listing(conn, run_id, city_id, model_key, model_name, title, price_raw, price_toman):
    """درج یک آگهی. conn باز نگه داشته می‌شود (برای درج گروهی سریع‌تر)."""
    scraped_at = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """
        INSERT INTO listings
            (run_id, city_id, model_key, model_name, title, price_raw, price_toman, scraped_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (run_id, city_id, model_key, model_name, title, price_raw, price_toman, scraped_at),
    )


def insert_listings_bulk(listings, db_path=DB_PATH):
    """
    listings: لیستی از دیکشنری‌ها با کلیدهای:
        run_id, city_id, model_key, model_name, title, price_raw, price_toman
    """
    conn = get_connection(db_path)
    try:
        for item in listings:
            insert_listing(
                conn,
                run_id=item["run_id"],
                city_id=item["city_id"],
                model_key=item["model_key"],
                model_name=item["model_name"],
                title=item.get("title"),
                price_raw=item.get("price_raw"),
                price_toman=item.get("price_toman"),
            )
        conn.commit()
    finally:
        conn.close()


def list_runs(db_path=DB_PATH):
    conn = get_connection(db_path)
    try:
        rows = conn.execute("SELECT id, run_at FROM runs ORDER BY id").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    print(f"دیتابیس آماده شد: {DB_PATH}")
    print("شهرها:")
    conn = get_connection()
    for row in conn.execute("SELECT * FROM cities"):
        print(dict(row))
    conn.close()
