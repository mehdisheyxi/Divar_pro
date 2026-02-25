import requests
import json
import fake_useragent


def get_mobile():
    payload = {
        f"city_ids": ["10"],
        "source_view": "CATEGORY",
        "pagination_data": {
            "@type": "type.googleapis.com/post_list.PaginationData",
            "page": 1,
            "layer_page": {page}
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
