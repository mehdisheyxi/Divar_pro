import requests
import json
import fake_useragent
import os
import scraper
import sys
from scraper import *

import sys
sys.stdout.reconfigure(encoding='utf-8')

data = get_mobile()
print(f"status code = {data['status']}")
for widget in data['data'].get('list_widgets', []):
    if widget.get('widget_type') == 'POST_ROW':
        title = widget['data']['title']
        price = widget['data']['middle_description_text']
        print(f'title = {title}')
        print(f'price = {price}')
        print('-' * 10)

print('-*-*' * 50)
print('-*-*' * 50)
print('-*-*' * 50)

data2 = get_homepage()
print(f"status code = {data2['status']}")
for widget in data2['data'].get('list_widgets', []):
    if widget.get('widget_type') == 'POST_ROW':
        title = widget['data'].get('title')
        print(f'title = {title}')
        price = widget['data'].get('middle_description_text')
        if price:
            print(f'price = {price}')

        print('-' * 10)
