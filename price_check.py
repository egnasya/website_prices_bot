import re
from urllib.parse import urlparse
import aiosqlite
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from domains_selectors import DOMAIN_SELECTOR, DOMAIN_SELECTOR_ADD, DOMAIN_SELECTOR_SOLD_OUT
import manipulation_db


async def check_and_update_prices():
    notifications = {}
    async with aiosqlite.connect('users_products.db') as conn:
        cursor = await conn.cursor()
        await cursor.execute("SELECT user_id, URL, product_name, current_price, product_availability FROM products_users")
        products = await cursor.fetchall()

        for user_id, url, product_name, old_price, old_availability in products:
            domain_url = urlparse(url).netloc
            new_price, availability = await get_price(url, domain_url, old_price)
            notification_message = None

            if availability != old_availability or (new_price and int(new_price) != int(old_price)):
                await manipulation_db.add_or_update_product(user_id, url, product_name, new_price, availability)

                if availability == 0:
                    notification_message = (f'Вашего товара {product_name} больше нет в наличии. Можете отписаться от '
                                            f'отслеживания или подождать наличия (я уведомлю об этом).{url}')
                elif availability == 1 and new_price:
                    if int(new_price) == int(old_price):
                        notification_message = f'Ваш товар {product_name} снова в наличии! Цена не изменилась.{url}'
                    else:
                        diff = int(old_price) - int(new_price)
                        notification_message = (f'Ваш товар {product_name} снова в наличии и цена изменилась!\n'
                                                f'Новая цена: {new_price} ({diff}).\n{url}')
                        print(int(old_price), '->', int(new_price))
                elif new_price and int(new_price) != int(old_price):
                    diff = int(old_price) - int(new_price)
                    notification_message = (f'Цена на ваш товар {product_name} изменилась!\nНовая цена: {new_price}'
                                            f' ({diff}).\n{url}')
                    print(int(old_price), '->', int(new_price))

                if notification_message:
                    notifications[user_id] = notification_message

    return notifications


async def get_price(site_url, key, old_price):
    global driver, price, name_product
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.implicitly_wait(3)
        driver.get(site_url)
        if key in DOMAIN_SELECTOR_SOLD_OUT and driver.find_elements(By.CSS_SELECTOR, DOMAIN_SELECTOR_SOLD_OUT[key]):
            return old_price, 0
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
                    return None, -1
            if price:
                price = re.sub('[\u00A0|\u2009]', '', price)
                price = re.sub('[A-Za-zА-Яа-я:]+', '', price)
                price = re.sub('₽.*₽', '', price).strip()
                price = re.sub('₽[0-9]+₽*', '', price).strip()
                if price.endswith('₽'):
                    price = price[:-1]
                clean_price = price.replace(' ', '')
                return clean_price, 1
            else:
                return None, -1
    except Exception as e:
        print(f'Произошла непредвиденная ошибка: {e}')
        return None, -1
    finally:
        if driver:
            driver.quit()
