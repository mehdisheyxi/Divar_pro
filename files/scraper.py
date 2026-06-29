# scraper.py
# نسخه‌ی گسترش‌یافته: توابع قبلی دست‌نخورده باقی مانده‌اند
# (برای سازگاری با Master.py و main.py)، و در پایین فایل
# تابع جدید پارامتری برای اسکرپ چندشهره/چندمدله اضافه شده است.

import time
import requests
import json
import fake_useragent

url = 'https://api.divar.ir/v8/postlist/w/search'


def _get_headers():
    """هر بار یک User-Agent تازه می‌سازد (به‌جای ثابت ماندن در کل اجرای برنامه)."""
    return {'User-Agent': fake_useragent.UserAgent().random}


headers = _get_headers()  # برای سازگاری با کد قبلی که از متغیر سراسری headers استفاده می‌کرد


def get_mobile():
    payload = {
        f"city_ids": ["10"],
        "source_view": "CATEGORY",
        "pagination_data": {
            "@type": "type.googleapis.com/post_list.PaginationData",
            "page": 1,
            "layer_page": 1,
        },
        "disable_recommendation": False,
        "map_state": {
            "camera_info": {
                "bbox": {}
            }
        },
        "search_data": {
            "form_data": {
                "data": {
                    "category": {
                        "str": {
                            "value": "mobile-phones"
                        }
                    }
                }
            },
            "server_payload": {
                "@type": "type.googleapis.com/widgets.SearchData.ServerPayload",
                "additional_form_data": {
                    "data": {
                        "sort": {
                            "str": {
                                "value": "sort_date"
                            }
                        }
                    }
                }
            }
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    return {
        'data': response.json(),
        'status': response.status_code,
    }


def get_homepage():
    payload2 = {
        "city_ids": ["10"],
        "disable_recommendation": False,
        "map_state": {
            "camera_info": {
                "bbox": {}
            },
            "page_state": "DEFAULT"
        },
        "search_data": {
            "form_data": {
                "data": {
                    "category": {
                        "str": {
                            "value": "ROOT"
                        }
                    }
                }
            }
        }
    }
    response = requests.post(url, headers=headers, json=payload2)
    return {
        'data': response.json(),
        'status': response.status_code,
    }


def get_iphone():
    payload = {
        "city_ids": ["10"],
        "search_data": {
            "form_data": {
                "data": {
                    "category": {
                        "str": {
                            "value": "mobile-phones"
                        }
                    },
                    "brand_model": {
                        "repeated_string": {
                            "value": ["apple"]
                        }
                    }
                }
            }
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    return {
        'data': response.json(),
        'status': response.status_code,
    }


def get_iphone_coustoms(model):
    payload = {
        "city_ids": ["10"],
        "source_view": "FILTER",
        "pagination_data": {
            "@type": "type.googleapis.com/post_list.PaginationData",
            "page": 1,
            "layer_page": 1,
        },
        "disable_recommendation": False,
        "map_state": {
            "camera_info": {
                "bbox": {}
            }
        },
        "search_data": {
            "form_data": {
                "data": {
                    "category": {
                        "str": {
                            "value": "mobile-phones"
                        }
                    },
                    "brand_model": {
                        "repeated_string": {
                            "value": [f"apple {model}"]
                        }
                    }
                }
            },
            "server_payload": {
                "@type": "type.googleapis.com/widgets.SearchData.ServerPayload",
                "additional_form_data": {
                    "data": {
                        "sort": {
                            "str": {
                                "value": "recommended"
                            }
                        }
                    }
                }
            }
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    return {
        'data': response.json(),
        'status': response.status_code,
    }


def get_mobile_posts():
    data = get_mobile()
    posts = []
    for widget in data['data'].get('list_widgets', []):
        if widget.get('widget_type') == 'POST_ROW':
            title = widget['data'].get('title')
            price = widget['data'].get('middle_description_text')
            posts.append({"title": title, "price": price})
    return posts


def get_home_posts():
    data = get_homepage()
    posts = []
    for widget in data['data'].get('list_widgets', []):
        if widget.get('widget_type') == 'POST_ROW':
            title = widget['data'].get('title')
            price = widget['data'].get('middle_description_text')
            posts.append({"title": title, "price": price if price else 'NONE'})
    return posts


def get_iphone_posts():
    data = get_iphone()
    posts = []
    for widget in data['data'].get('list_widgets', []):
        if widget.get('widget_type') == 'POST_ROW':
            title = widget['data'].get('title')
            price = widget['data'].get('middle_description_text')
            posts.append({"title": title, "price": price})
    return posts


def get_iphone_coustoms_posts(model):
    data = get_iphone_coustoms(model)
    print(data['status'])
    posts = []
    for widget in data['data'].get('list_widgets', []):
        if widget.get('widget_type') == 'POST_ROW':
            title = widget['data'].get('title')
            price = widget['data'].get('middle_description_text')
            posts.append({"title": title, "price": price})
    return posts


# =============================================================
# توابع جدید: پارامتری بر اساس شهر + پشتیبانی از چند صفحه
# (برای پروژه‌ی مقایسه‌ی قیمت بین‌شهری)
# =============================================================

def get_iphone_city_page(model, city_id, page=1):
    """
    یک درخواست برای یک مدل آیفون مشخص، در یک شهر مشخص، یک صفحه‌ی مشخص.
    model: رشته‌ی مدل، مثل 'iphone 15 pro'
    city_id: شناسه‌ی شهر دیوار (int یا str)
    """
    payload = {
        "city_ids": [str(city_id)],
        "source_view": "FILTER",
        "pagination_data": {
            "@type": "type.googleapis.com/post_list.PaginationData",
            "page": page,
            "layer_page": page,
        },
        "disable_recommendation": False,
        "map_state": {
            "camera_info": {
                "bbox": {}
            }
        },
        "search_data": {
            "form_data": {
                "data": {
                    "category": {
                        "str": {
                            "value": "mobile-phones"
                        }
                    },
                    "brand_model": {
                        "repeated_string": {
                            "value": [f"apple {model}"]
                        }
                    }
                }
            },
            "server_payload": {
                "@type": "type.googleapis.com/widgets.SearchData.ServerPayload",
                "additional_form_data": {
                    "data": {
                        "sort": {
                            "str": {
                                "value": "recommended"
                            }
                        }
                    }
                }
            }
        }
    }
    response = requests.post(url, headers=_get_headers(), json=payload)
    return {
        'data': response.json(),
        'status': response.status_code,
    }


def get_iphone_city_posts(model, city_id, max_pages=1, delay_seconds=1.0):
    """
    آگهی‌های یک مدل آیفون در یک شهر مشخص را برمی‌گرداند، با امکان گرفتن
    چند صفحه برای نمونه‌ی بزرگ‌تر (برای میانگین دقیق‌تر).

    خروجی: لیستی از دیکشنری {'title': ..., 'price_raw': ...}
    """
    posts = []
    for page in range(1, max_pages + 1):
        try:
            result = get_iphone_city_page(model, city_id, page=page)
        except requests.RequestException as exc:
            print(f"  [خطا در درخواست] model={model} city={city_id} page={page}: {exc}")
            break

        if result['status'] != 200:
            print(f"  [status={result['status']}] model={model} city={city_id} page={page}")
            break

        widgets = result['data'].get('list_widgets', [])
        page_posts = [
            {
                'title': w['data'].get('title'),
                'price_raw': w['data'].get('middle_description_text'),
            }
            for w in widgets
            if w.get('widget_type') == 'POST_ROW'
        ]

        if not page_posts:
            # دیگه آگهی‌ای برای صفحه‌ی بعد نیست
            break

        posts.extend(page_posts)

        if page < max_pages:
            time.sleep(delay_seconds)

    return posts
