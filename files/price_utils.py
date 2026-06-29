# price_utils.py
# تبدیل متن قیمت دیوار (که معمولاً با ارقام فارسی و جداکننده‌ی هزارگان است)
# به یک عدد صحیح (تومان). اگر قیمت قابل‌تفسیر نباشد (مثل "توافقی"، "رایگان")
# مقدار None برگردانده می‌شود تا در تحلیل نادیده گرفته شود.

PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
ARABIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"
ASCII_DIGITS = "0123456789"

_DIGIT_TRANSLATION = str.maketrans(
    PERSIAN_DIGITS + ARABIC_DIGITS,
    ASCII_DIGITS + ASCII_DIGITS,
)

# کلماتی که یعنی قیمت عددی مشخصی وجود ندارد
NON_NUMERIC_MARKERS = [
    "توافقی",
    "رایگان",
    "نامشخص",
    "تماس بگیرید",
    "مبادله",
]


def parse_price(price_text):
    """
    ورودی نمونه‌ها:
        "۱۲۵٬۰۰۰٬۰۰۰ تومان"  -> 125000000
        "توافقی"             -> None
        None                  -> None

    خروجی: int یا None
    """
    if not price_text:
        return None

    text = str(price_text).strip()

    for marker in NON_NUMERIC_MARKERS:
        if marker in text:
            return None

    # تبدیل ارقام فارسی/عربی به انگلیسی
    text = text.translate(_DIGIT_TRANSLATION)

    # نگه داشتن فقط رقم‌ها (حذف "تومان"، جداکننده‌های هزارگان، فاصله و...)
    digits_only = "".join(ch for ch in text if ch.isdigit())

    if not digits_only:
        return None

    try:
        return int(digits_only)
    except ValueError:
        return None


if __name__ == "__main__":
    # تست سریع
    tests = [
        "۱۲۵٬۰۰۰٬۰۰۰ تومان",
        "125,000,000 تومان",
        "توافقی",
        "رایگان",
        None,
        "",
        "۹۹۰,۰۰۰ تومان",
    ]
    for t in tests:
        print(repr(t), "->", parse_price(t))
