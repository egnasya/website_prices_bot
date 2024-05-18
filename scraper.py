import re
import asyncio
from urllib.parse import urlparse
import requests
import validators
from selenium.common.exceptions import NoSuchWindowException, TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

from domains_selectors import DOMAIN_SELECTOR, DOMAIN_SELECTOR_ADD
import manipulation_db


async def website_recognition(text, user_id):
    valid = validators.url(text)

    if not valid:
        return 'Кажется, это не ссылка или она некорректна :('
    else:
        try:
            response = requests.get(text)
            if response.status_code != 200:
                return 'Произошла ошибка при загрузке страницы :('

            url = text
            domain_url = urlparse(url).netloc
            if domain_url in DOMAIN_SELECTOR:
                name_product, price, url = await get_price(url, domain_url, user_id)
                return f'Теперь вы отслеживаете товар: {name_product}\nЕго начальная цена: {price}\nСсылка: {url}'
            else:
                return 'Я пока не могу отслеживать цену с этого сайта :('
        except Exception as e:
            return f'Ошибка: {e}'


async def get_price(site_url, key, user_id):
    loop = asyncio.get_running_loop()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-setuid-sandbox")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--remote-debugging-port=9222")
    service = Service(executable_path='/home/nastya/website_prices_bot/chromedriver')

    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(10)  # Увеличиваем время ожидания для headless-режима

        driver.get(site_url)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'h1')))

        try:
            name_product = driver.find_element(By.TAG_NAME, 'h1').text.strip()
        except NoSuchElementException:
            print('Элемент с тегом "h1" не найден на странице.')
            name_product = 'Unknown Product'

        price_elements = await loop.run_in_executor(None, driver.find_elements, By.CSS_SELECTOR,
                                                    DOMAIN_SELECTOR.get(key))
        if not price_elements:
            price_elements = await loop.run_in_executor(None, driver.find_elements, By.CSS_SELECTOR,
                                                        DOMAIN_SELECTOR_ADD.get(key))

        if price_elements:
            price = price_elements[0].text
        else:
            print('Элемент с css-селекторами из базы данных на странице не найдены.')
            price = 'error'

        if price:
            price = re.sub('[\u00A0|\u2009]', '', price)
            price = re.sub('[A-Za-zА-Яа-я:]+', '', price)
            price = re.sub('₽.*₽', '', price).strip()
            price = re.sub('₽[0-9]+₽*', '', price).strip()
            if price.endswith('₽'):
                price = price[:-1]
            clean_price = price.replace(' ', '')
            await manipulation_db.add_or_update_product(user_id, site_url, name_product, clean_price, 1)
            print(f'Товар {name_product} с ценой {clean_price} и ссылкой {site_url} сохранен в базу данных.')
            return name_product, clean_price, site_url
        else:
            return name_product, 'error', site_url
    except Exception as e:
        print(f'Произошла непредвиденная ошибка: {e}')
        return 'Unknown Product', 'error', site_url
    finally:
        if driver:
            driver.quit()
