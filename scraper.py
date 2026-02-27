import requests
import json
import fake_useragent

url = 'https://api.divar.ir/v8/postlist/w/search'
headers = {'User-Agent': fake_useragent.UserAgent().random}

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

print(url)
