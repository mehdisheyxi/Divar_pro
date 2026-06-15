from scraper import *
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
print('WELCOME')
iphone_models = {

    '1': 'iphone 17 pro max',
    '2': 'iphone 17 pro',
    '3': 'iphone 17',

    '4': 'iphone 16 pro max',
    '5': 'iphone 16 pro',
    '6': 'iphone 16',

    '7': 'iphone 15 pro max',
    '8': 'iphone 15 pro',
    '9': 'iphone 15',

    '10': 'iphone 14 pro max',
    '11': 'iphone 14 pro',
    '12': 'iphone 14',

    '13': 'iphone 13 pro max',
    '14': 'iphone 13 pro',
    '15': 'iphone 13',

    '16': 'iphone 12 pro max',
    '17': 'iphone 12 pro',
    '18': 'iphone 12',

    '19': 'iphone 11 pro max',
    '20': 'iphone 11 pro',
    '21': 'iphone 11',

    '22': 'iphone xs max',
    '23': 'iphone xs',
    '24': 'iphone xr',

    '25': 'iphone x',

    '26': 'iphone 8 plus',
    '27': 'iphone 8',

    '28': 'iphone 7 plus',
    '29': 'iphone 7',

    '30': 'iphone 6s plus',
    '31': 'iphone 6s',

    '32': 'iphone 6 plus',
    '33': 'iphone 6',

    '34': 'iphone 5s',
    '35': 'iphone 5',
}
while True:
    os.system('cls')
    number = input('''
        1_Get mobile home page
        2_Get home page
        3_Get iphone home page
        4_Get iphone with FILTER
    ''')
    if number == '1':
        posts = get_mobile_posts()
        for post in posts:
            print('-' * 50)
            print(f"title:{post['title']}")
            print(f"price:{post['price']}")
        input('Enter any key to exit...')
    elif number == '2':
        posts = get_home_posts()
        for post in posts:
            print('-' * 50)
            print(f"title:{post['title']}")
            print(f"price:{post['price']}")
        input('Enter any key to exit...')
    elif number == '3':
        posts = get_iphone_posts()
        for post in posts:
            print('-' * 50)
            print(f"title:{post['title']}")
            print(f"price:{post['price']}")
        input('Enter any key to exit...')
    elif number == '4':
        print('''
            1_apple iphone 17 pro max
            2_apple iphone 17 pro
            3_apple iphone 17

            4_apple iphone 16 pro max
            5_apple iphone 16 pro
            6_apple iphone 16

            7_apple iphone 15 pro max
            8_apple iphone 15 pro
            9_apple iphone 15

            10_apple iphone 14 pro max
            11_apple iphone 14 pro
            12_apple iphone 14

            13_apple iphone 13 pro max
            14_apple iphone 13 pro
            15_apple iphone 13

            16_apple iphone 12 pro max
            17_apple iphone 12 pro
            18_apple iphone 12

            19_apple iphone 11 pro max
            20_apple iphone 11 pro
            21_apple iphone 11

            22_apple iphone xs max
            23_apple iphone xs
            24_apple iphone xr

            25_apple iphone x

            26_apple iphone 8 plus
            27_apple iphone 8

            28_apple iphone 7 plus
            29_apple iphone 7

            30_apple iphone 6s plus
            31_apple iphone 6s

            32_apple iphone 6 plus
            33_apple iphone 6

            34_apple iphone 5s
            35_apple iphone 5
            ''')
        a = input('Enter number:::')
        model = iphone_models.get(a)
        posts = get_iphone_coustoms_posts(model)
        for post in posts:
            print('-' * 50)
            print(f"title:{post['title']}")
            print(f"price:{post['price']}")
        input('Enter any key to exit...')
