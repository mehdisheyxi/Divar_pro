import requests
import json
import fake_useragent

url = 'https://api.divar.ir/v8/postlist/w/search'

payload = {
    "city_ids": ["10"],
    "source_view": "CATEGORY",
    "pagination_data": {
        "@type": "type.googleapis.com/post_list.PaginationData",
        "page": 1,
        "layer_page": 1
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
ua = fake_useragent.FakeUserAgent().random
headers = {
    'Content-Type': 'application/json',
    'User-Agent': ua
}
#به صورت اتوماتیک خط پایین اجرا میشه
#payload = json.dumps(payload)
#این جا dict تبدیل به json میشه

response = requests.post(url, headers=headers, json=payload)

print(f"status code: {response.status_code}")


#به صورت اتوماتیک json که گرفتیم رو تبدیل به dict میکنه
#data = json.loads(response.text)
#خط بالا به صورت اتوماتیک اجرا میشه

data = response.json()


for widget in data.get('list_widgets', []):
    if widget.get('widget_type') == 'POST_ROW':
        title = widget['data']['title']
        price = widget['data']['middle_description_text']
        print(f'title = {title}')
        print(f'price = {price}')
        print('-' * 30)
        break


print(ua)
