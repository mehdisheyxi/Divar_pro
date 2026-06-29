# interactive.py
# نسخه‌ی تعاملی: اول مدل آیفون رو با عدد انتخاب می‌کنی، بعد شهر(ها) رو،
# و بعد بلافاصله اسکرپ می‌کنه و قیمت‌ها/آنالیز رو نشون می‌ده.
#
# نحوه‌ی اجرا:
#   python interactive.py

import os
import statistics

from config import (
    IPHONE_MODELS,
    CITIES,
    BENCHMARK_CITY,
    MAX_PAGES_PER_QUERY,
    REQUEST_DELAY_SECONDS,
)
from scraper import get_iphone_city_posts
from price_utils import parse_price
import db


# همه‌ی شهرهای قابل‌انتخاب در منو (شهرهای اصلی + کل ایران به‌عنوان مرجع)
ALL_SELECTABLE_CITIES = {**CITIES, **BENCHMARK_CITY}


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def _find_model_key(model_name):
    for key, name in IPHONE_MODELS.items():
        if name == model_name:
            return key
    return ''


# ---------------------------------------------------------
# منوها
# ---------------------------------------------------------

def choose_model():
    print("📱 انتخاب مدل آیفون:\n")
    for key in sorted(IPHONE_MODELS, key=lambda k: int(k)):
        print(f"   {key}_ {IPHONE_MODELS[key]}")

    while True:
        choice = input("\nشماره‌ی مدل رو وارد کن: ").strip()
        if choice in IPHONE_MODELS:
            return IPHONE_MODELS[choice]
        print("❌ شماره‌ی نامعتبر، دوباره وارد کن.")


def choose_cities():
    print("\n🏙️  انتخاب شهر:\n")
    city_list = list(ALL_SELECTABLE_CITIES.items())  # [(name, id), ...]

    for i, (name, _id) in enumerate(city_list, start=1):
        tag = "  [مرجع کشوری]" if name in BENCHMARK_CITY else ""
        print(f"   {i}_ {name}{tag}")
    print("   0_ همه‌ی شهرها (مقایسه‌ی کامل)")

    while True:
        choice = input("\nشماره رو وارد کن (یا چند شماره با کاما، مثلا 1,3): ").strip()

        if choice == '0':
            return city_list

        try:
            indices = [int(x.strip()) for x in choice.split(',') if x.strip()]
            selected = [city_list[i - 1] for i in indices if 1 <= i <= len(city_list)]
            if selected:
                return selected
        except (ValueError, IndexError):
            pass

        print("❌ ورودی نامعتبر، دوباره وارد کن.")


# ---------------------------------------------------------
# اسکرپ + آنالیز
# ---------------------------------------------------------

def scrape_and_analyze(model_name, cities):
    print(f"\n🔎 در حال جست‌وجوی «{model_name}» در {len(cities)} شهر ...\n")

    run_id = db.create_run()
    model_key = _find_model_key(model_name)

    results_by_city = {}
    listings_for_db = []

    for city_name, city_id in cities:
        print(f"   ⏳ {city_name} ...", end=' ', flush=True)

        try:
            posts = get_iphone_city_posts(
                model=model_name,
                city_id=city_id,
                max_pages=MAX_PAGES_PER_QUERY,
                delay_seconds=REQUEST_DELAY_SECONDS,
            )
        except Exception as exc:  # noqa: BLE001
            print(f"خطا: {exc}")
            results_by_city[city_name] = []
            continue

        parsed = []
        for post in posts:
            price = parse_price(post.get('price_raw'))
            parsed.append({**post, 'price_toman': price})
            listings_for_db.append({
                "run_id": run_id,
                "city_id": city_id,
                "model_key": model_key,
                "model_name": model_name,
                "title": post.get('title'),
                "price_raw": post.get('price_raw'),
                "price_toman": price,
            })

        valid = [p for p in parsed if p['price_toman'] is not None]
        results_by_city[city_name] = valid
        print(f"{len(posts)} آگهی ({len(valid)} با قیمت معتبر)")

    if listings_for_db:
        db.insert_listings_bulk(listings_for_db)
        print(f"\n✅ نتایج ذخیره شد (run_id={run_id}) — برای روند آینده هم می‌مونه.\n")

    print_model_report(model_name, results_by_city)


def print_model_report(model_name, results_by_city):
    print("=" * 60)
    print(f"📊 گزارش قیمت: {model_name}")
    print("=" * 60)

    city_stats = {}

    for city_name, listings in results_by_city.items():
        if not listings:
            print(f"\n▪ {city_name}: هیچ آگهی با قیمت معتبر پیدا نشد.")
            continue

        prices = [l['price_toman'] for l in listings]
        avg = statistics.mean(prices)
        city_stats[city_name] = {
            "avg": avg,
            "min": min(prices),
            "max": max(prices),
            "count": len(prices),
        }

        print(f"\n▪ {city_name}  (تعداد آگهی معتبر: {len(prices)})")
        print(f"   میانگین : {avg:,.0f} تومان")
        print(f"   کمترین  : {min(prices):,.0f} تومان")
        print(f"   بیشترین : {max(prices):,.0f} تومان")

        cheapest3 = sorted(listings, key=lambda l: l['price_toman'])[:3]
        print("   نمونه ارزون‌ترین آگهی‌ها:")
        for l in cheapest3:
            print(f"      {l['price_toman']:>15,.0f} تومان | {l['title']}")

    # رتبه‌بندی بین‌شهری، فقط اگه بیش از یک شهر غیرمرجع داریم
    non_benchmark_stats = {
        c: s for c, s in city_stats.items() if c not in BENCHMARK_CITY
    }

    if len(non_benchmark_stats) > 1:
        print("\n" + "-" * 60)
        print("📈 رتبه‌بندی شهرها (از ارزون به گرون):")
        for city_name, stats in sorted(non_benchmark_stats.items(), key=lambda x: x[1]["avg"]):
            print(f"   {stats['avg']:>15,.0f} تومان  —  {city_name}")

        cheapest_city = min(non_benchmark_stats, key=lambda c: non_benchmark_stats[c]["avg"])
        priciest_city = max(non_benchmark_stats, key=lambda c: non_benchmark_stats[c]["avg"])

        print(f"\n   ✅ ارزون‌ترین شهر برای خرید «{model_name}»: {cheapest_city}")
        print(f"   ⚠️  گرون‌ترین شهر: {priciest_city}")

    if "کل ایران" in city_stats:
        print(f"\n   [مرجع کشوری] میانگین کل ایران: {city_stats['کل ایران']['avg']:,.0f} تومان")

    print("\n" + "=" * 60)


# ---------------------------------------------------------
# حلقه‌ی اصلی
# ---------------------------------------------------------

def main():
    db.init_db()

    while True:
        clear_screen()
        print("=" * 60)
        print("ابزار مقایسه‌ی قیمت آیفون بین شهرها (دیوار)")
        print("=" * 60)
        print()

        model_name = choose_model()
        cities = choose_cities()

        scrape_and_analyze(model_name, cities)

        again = input("\nدوباره برای مدل/شهر دیگه جست‌وجو کنم؟ (y/n): ").strip().lower()
        if again != 'y':
            break

    print("\nخروج. برای گزارش کامل (همه‌ی مدل‌ها + روند زمانی) از analyze.py استفاده کن.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nمتوقف شد توسط کاربر.")
