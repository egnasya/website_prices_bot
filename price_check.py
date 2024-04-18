import re
from asyncio import to_thread
from urllib.parse import urlparse
import aiosqlite
from domains_selectors import DOMAIN_SELECTOR, DOMAIN_SELECTOR_ADD
from selenium.webdriver.common.by import By
from seleniumwire import webdriver
import manipulation_db


async def check_and_update_prices():
    notifications = {}
    async with aiosqlite.connect('users_products.db') as conn:
        cursor = await conn.cursor()
        await cursor.execute("SELECT user_id, URL, product_name, current_price FROM products_users")
        products = await cursor.fetchall()

    for user_id, url, product_name, old_price in products:
        domain_url = urlparse(url).netloc
        new_price = await get_price(url, domain_url, old_price)
        if new_price and int(new_price) != int(old_price):
            diff = int(old_price) - int(new_price)
            await manipulation_db.add_or_update_product(user_id, url, product_name, new_price)
            notification_user, notification_message = send_notification(user_id, url, product_name, new_price, diff)
            notifications[notification_user] = notification_message
        else:
            print('Цена не изменилась')

    await conn.close()
    return notifications


async def get_price(site_url, key, old_price):
    global driver, price, name_product

    try:
        driver = webdriver.Chrome()
        driver.implicitly_wait(3)
        driver.get(site_url)
    except Exception as e:
        print(f'Произошла непредвиденная ошибка: {e}')
    else:
        price_elements = driver.find_elements(By.CSS_SELECTOR, DOMAIN_SELECTOR[key])
        if price_elements:
            price = price_elements[0].text
        else:
            price_elements = driver.find_elements(By.CSS_SELECTOR, DOMAIN_SELECTOR_ADD[key])
            if price_elements:
                price = price_elements[0].text
            else:
                print('Элемент с css-селекторами из базы данных на странице не найдены.')
                return get_price(site_url, key, old_price)
        if price:
            price = re.sub('[\u00A0|\u2009]', '', price)
            price = re.sub('[A-Za-zА-Яа-я:]+', '', price)
            price = re.sub('₽.*₽', '', price).strip()
            price = re.sub('₽[0-9]+₽*', '', price).strip()
            if price.endswith('₽'):
                price = price[:-1]
            clean_price = price.replace(' ', '')
            return clean_price
        else:
            return get_price(site_url, key, old_price)
    finally:
        driver.quit()


def send_notification(user, url, name_product, price, diff):
    message = f'Цена на ваш товар {name_product} изменилась!\nНовая цена: {price} ({diff})\n{url}'
    return user, message