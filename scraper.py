import requests
import json
import fake_useragent

url = 'https://api.divar.ir/v8/postlist/w/search'
headers = {'User-Agent': fake_useragent.UserAgent().random}


def get_mobile():
    '''

    :return:
    '''

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


# ----------------------
def get_homepage():
    payload2 = {
        "city_ids": [
            "10"
        ],
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


# ----------------------
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

    posts = []  # لیست خروجی

    for widget in data['data'].get('list_widgets', []):
        if widget.get('widget_type') == 'POST_ROW':
            title = widget['data'].get('title')
            price = widget['data'].get('middle_description_text')

            posts.append({
                "title": title,
                "price": price
            })

    return posts


def get_home_posts():
    data = get_homepage()
    posts = []
    for widget in data['data'].get('list_widgets', []):
        if widget.get('widget_type') == 'POST_ROW':
            title = widget['data'].get('title')
            price = widget['data'].get('middle_description_text')
            if price:
                posts.append({
                    "title": title,
                    "price": price
                })
            else:
                posts.append({
                    "title": title,
                    "price": 'NONE'
                })
    return posts


def get_iphone_posts():
    data = get_iphone()

    posts = []

    for widget in data['data'].get('list_widgets', []):

        if widget.get('widget_type') == 'POST_ROW':
            title = widget['data'].get('title')
            price = widget['data'].get('middle_description_text')

            posts.append({
                "title": title,
                "price": price
            })

    return posts


def get_iphone_coustoms_posts(model):
    data = get_iphone_coustoms(model)
    print(data['status'])

    posts = []

    for widget in data['data'].get('list_widgets', []):

        if widget.get('widget_type') == 'POST_ROW':
            title = widget['data'].get('title')
            price = widget['data'].get('middle_description_text')
            date = widget["data"].get("bottom_description_text")

            if not date:
                red_text = widget["data"].get("red_text", "")

                emoji = {
                    "نردبان شده": "🪜",
                    "پله شده": "⚡",
                    "نردبان شده | فروشگاه": "⭐"
                }

                date = f"{emoji.get(red_text, '')} {red_text}".strip()

            token = (
                widget["data"]
                .get("action", {})
                .get("payload", {})
                .get("token")
            )

            city = (
                widget["data"]
                .get("action", {})
                .get("payload", {})
                .get("web_info", {})
                .get("city_persian")
            )


            posts.append({
                "title": title,
                "price": price,
                "date": date,
                "city": city,
                "token": token,
                "link": f"https://divar.ir/v/{token}"
            })
    return posts


print(url)
