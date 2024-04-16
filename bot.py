import requests
import time
from my_token import TOKEN


API_URL = 'https://api.telegram.org/bot'
API_CATS_URL = 'https://api.thecatapi.com/v1/images/search'
BOT_TOKEN = TOKEN
ERROR_TEXT = 'здесь должна быть картинка с котиком :('
MAX_COUNTER = 100

offset = -2
counter = 0
chat_id : int
cat_response : requests.Response

while counter < MAX_COUNTER:
    print('attempt = ', counter)
    updates = requests.get(f'{API_URL}{BOT_TOKEN}/getUpdates?offset={offset + 1}').json()

    if updates['result']:
        for update in updates['result']:
            offset = update['update_id']
            chat_id = update['message']['from']['id']
            cat_response = requests.get(API_CATS_URL)
            if cat_response.status_code == 200:
                cat_link = cat_response.json()[0]['url']
                requests.get(f'{API_URL}{BOT_TOKEN}/sendPhoto?chat_id={chat_id}&photo={cat_link}').json()
            else:
                response = requests.get(f'{API_URL}{BOT_TOKEN}/sendMessage?chat_id={chat_id}&text={ERROR_TEXT}').json()

    time.sleep(1)
    counter += 1

