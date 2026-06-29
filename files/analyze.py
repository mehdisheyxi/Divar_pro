# analyze.py
# تحلیل داده‌های ذخیره‌شده در دیتابیس:
#   1) برای هر مدل، میانگین قیمت در هر شهر + ارزون‌ترین/گرون‌ترین شهر (بدون "کل ایران")
#   2) ۱۰ آگهی گرون‌ترین و ۱۰ آگهی ارزون‌ترین در هر مدل (با ذکر شهر)
#   3) روند صعودی/نزولی هر شهر بین runها (برای هر مدل + یک "روند کلی" تجمیعی)
#
# نحوه‌ی اجرا:
#   python analyze.py

from collections import defaultdict
import statistics

import db
from config import DB_PATH


def _fetch_all_listings(conn):
    """تمام آگهی‌ها همراه با اسم شهر و زمان run."""
    query = """
        SELECT
            l.id, l.run_id, l.city_id, c.name AS city_name, c.is_benchmark,
            l.model_key, l.model_name, l.title, l.price_raw, l.price_toman,
            r.run_at
        FROM listings l
        JOIN cities c ON c.id = l.city_id
        JOIN runs r ON r.id = l.run_id
        WHERE l.price_toman IS NOT NULL
    """
    return [dict(row) for row in conn.execute(query)]


# ---------------------------------------------------------
# بخش ۱: میانگین قیمت هر مدل در هر شهر + ارزون‌ترین/گرون‌ترین شهر
# ---------------------------------------------------------

def average_price_by_city_per_model(listings, latest_run_id=None):
    """
    خروجی:
    {
        model_name: {
            city_name: {"avg": float, "count": int, "is_benchmark": bool}
        }
    }
    اگر latest_run_id داده شود فقط همان run در نظر گرفته می‌شود؛
    در غیر این صورت همه‌ی دادها (همه‌ی runها) با هم میانگین گرفته می‌شوند.
    """
    filtered = listings
    if latest_run_id is not None:
        filtered = [l for l in listings if l['run_id'] == latest_run_id]

    grouped = defaultdict(lambda: defaultdict(list))
    benchmark_flag = {}

    for l in filtered:
        grouped[l['model_name']][l['city_name']].append(l['price_toman'])
        benchmark_flag[l['city_name']] = bool(l['is_benchmark'])

    result = {}
    for model_name, city_prices in grouped.items():
        result[model_name] = {}
        for city_name, prices in city_prices.items():
            result[model_name][city_name] = {
                "avg": statistics.mean(prices),
                "count": len(prices),
                "is_benchmark": benchmark_flag[city_name],
            }
    return result


def cheapest_and_priciest_city_per_model(avg_by_model):
    """
    برای هر مدل، شهر ارزون‌ترین و گرون‌ترین را برمی‌گرداند (بدون شهرهای benchmark مثل کل ایران).
    """
    report = {}
    for model_name, city_data in avg_by_model.items():
        non_benchmark = {
            city: data for city, data in city_data.items() if not data['is_benchmark']
        }
        if not non_benchmark:
            continue

        cheapest_city = min(non_benchmark, key=lambda c: non_benchmark[c]['avg'])
        priciest_city = max(non_benchmark, key=lambda c: non_benchmark[c]['avg'])

        report[model_name] = {
            "cheapest": {"city": cheapest_city, **non_benchmark[cheapest_city]},
            "priciest": {"city": priciest_city, **non_benchmark[priciest_city]},
            "benchmark": city_data.get(_find_benchmark_city_name(city_data)),
        }
    return report


def _find_benchmark_city_name(city_data):
    for city_name, data in city_data.items():
        if data['is_benchmark']:
            return city_name
    return None


# ---------------------------------------------------------
# بخش ۲: ۱۰ آگهی گرون‌ترین / ارزون‌ترین در هر مدل
# ---------------------------------------------------------

def top_n_listings_per_model(listings, n=10, include_benchmark=False):
    """
    خروجی:
    {
        model_name: {
            "most_expensive": [ {title, price_toman, city_name, run_at}, ... ],
            "cheapest": [ ... ]
        }
    }
    """
    by_model = defaultdict(list)
    for l in listings:
        if not include_benchmark and l['is_benchmark']:
            continue
        by_model[l['model_name']].append(l)

    report = {}
    for model_name, items in by_model.items():
        sorted_desc = sorted(items, key=lambda x: x['price_toman'], reverse=True)
        sorted_asc = sorted(items, key=lambda x: x['price_toman'])

        report[model_name] = {
            "most_expensive": sorted_desc[:n],
            "cheapest": sorted_asc[:n],
        }
    return report


# ---------------------------------------------------------
# بخش ۳: روند صعودی/نزولی بین runها
# ---------------------------------------------------------

def trend_per_city_per_model(listings):
    """
    برای هر (مدل، شهر)، سری زمانی میانگین قیمت در هر run را برمی‌گرداند،
    به‌همراه درصد تغییر بین اولین و آخرین run.

    خروجی:
    {
        model_name: {
            city_name: {
                "series": [ {"run_at": ..., "avg": float}, ... ]  (به ترتیب زمان)
                "pct_change": float یا None (اگر فقط یک run وجود داشت)
                "direction": "صعودی" / "نزولی" / "ثابت" / "نامعلوم"
            }
        }
    }
    """
    grouped = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    # grouped[model][city][run_at] = [prices...]

    for l in listings:
        grouped[l['model_name']][l['city_name']][l['run_at']].append(l['price_toman'])

    result = {}
    for model_name, city_runs in grouped.items():
        result[model_name] = {}
        for city_name, run_prices in city_runs.items():
            series = [
                {"run_at": run_at, "avg": statistics.mean(prices)}
                for run_at, prices in sorted(run_prices.items())
            ]

            if len(series) < 2:
                pct_change = None
                direction = "نامعلوم (فقط یک run)"
            else:
                first_avg = series[0]['avg']
                last_avg = series[-1]['avg']
                pct_change = ((last_avg - first_avg) / first_avg) * 100 if first_avg else None

                if pct_change is None:
                    direction = "نامعلوم"
                elif pct_change > 1:
                    direction = "صعودی"
                elif pct_change < -1:
                    direction = "نزولی"
                else:
                    direction = "ثابت"

            result[model_name][city_name] = {
                "series": series,
                "pct_change": pct_change,
                "direction": direction,
            }
    return result


def overall_city_trend(trend_data, exclude_benchmark_cities=None):
    """
    شاخص "روند کلی" هر شهر: میانگین درصد تغییر روی همه‌ی مدل‌هایی که
    حداقل دو run داشتند. این یک عدد/جهت واحد برای هر شهر می‌دهد.

    خروجی:
    {
        city_name: {"avg_pct_change": float, "direction": str, "n_models": int}
    }
    """
    exclude_benchmark_cities = exclude_benchmark_cities or set()

    per_city_changes = defaultdict(list)
    for model_name, city_data in trend_data.items():
        for city_name, data in city_data.items():
            if city_name in exclude_benchmark_cities:
                continue
            if data['pct_change'] is not None:
                per_city_changes[city_name].append(data['pct_change'])

    result = {}
    for city_name, changes in per_city_changes.items():
        avg_change = statistics.mean(changes)
        if avg_change > 1:
            direction = "صعودی"
        elif avg_change < -1:
            direction = "نزولی"
        else:
            direction = "ثابت"

        result[city_name] = {
            "avg_pct_change": avg_change,
            "direction": direction,
            "n_models": len(changes),
        }
    return result


# ---------------------------------------------------------
# چاپ گزارش خوانا در ترمینال
# ---------------------------------------------------------

def format_toman(value):
    return f"{value:,.0f} تومان"


def print_full_report(db_path=DB_PATH):
    conn = db.get_connection(db_path)
    listings = _fetch_all_listings(conn)
    conn.close()

    if not listings:
        print("هیچ داده‌ای در دیتابیس نیست. اول run_scrape.py را اجرا کن.")
        return

    benchmark_cities = {l['city_name'] for l in listings if l['is_benchmark']}

    runs = db.list_runs(db_path)
    latest_run_id = runs[-1]['id'] if runs else None

    print("=" * 60)
    print(f"تعداد کل runها: {len(runs)} | آخرین run: {runs[-1]['run_at'] if runs else '-'}")
    print("=" * 60)

    # --- بخش ۱: میانگین آخرین run ---
    avg_latest = average_price_by_city_per_model(listings, latest_run_id=latest_run_id)
    ranking = cheapest_and_priciest_city_per_model(avg_latest)

    print("\n📊 ارزون‌ترین/گرون‌ترین شهر برای هر مدل (بر اساس آخرین run):\n")
    for model_name, info in ranking.items():
        cheap = info['cheapest']
        pricey = info['priciest']
        bench = info.get('benchmark')

        print(f"▪ {model_name}")
        print(f"   ارزون‌ترین: {cheap['city']} — {format_toman(cheap['avg'])} (n={cheap['count']})")
        print(f"   گرون‌ترین : {pricey['city']} — {format_toman(pricey['avg'])} (n={pricey['count']})")
        if bench:
            print(f"   [مرجع] کل ایران — {format_toman(bench['avg'])} (n={bench['count']})")
        print()

    # --- بخش ۲: ۱۰ گرون‌ترین/ارزون‌ترین آگهی هر مدل ---
    top_n = top_n_listings_per_model(listings, n=10)

    print("\n💰 ۱۰ آگهی گرون‌ترین و ارزون‌ترین هر مدل:\n")
    for model_name, data in top_n.items():
        print(f"▪ {model_name}")
        print("   گرون‌ترین‌ها:")
        for item in data['most_expensive']:
            print(f"      {format_toman(item['price_toman'])} | {item['city_name']} | {item['title']}")
        print("   ارزون‌ترین‌ها:")
        for item in data['cheapest']:
            print(f"      {format_toman(item['price_toman'])} | {item['city_name']} | {item['title']}")
        print()

    # --- بخش ۳: روند صعودی/نزولی ---
    trend_data = trend_per_city_per_model(listings)
    overall = overall_city_trend(trend_data, exclude_benchmark_cities=benchmark_cities)

    print("\n📈 روند کلی هر شهر (میانگین درصد تغییر روی همه‌ی مدل‌ها):\n")
    if not overall:
        print("   هنوز بیش از یک run ثبت نشده، پس روند قابل‌محاسبه نیست.")
        print("   چند روز دیگه دوباره run_scrape.py رو اجرا کن تا روند به‌دست بیاد.")
    else:
        for city_name, info in sorted(overall.items(), key=lambda x: x[1]['avg_pct_change'], reverse=True):
            arrow = "🔺" if info['direction'] == "صعودی" else ("🔻" if info['direction'] == "نزولی" else "➖")
            print(f"   {arrow} {city_name}: {info['avg_pct_change']:+.1f}% ({info['direction']}) — بر اساس {info['n_models']} مدل")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    print_full_report()
