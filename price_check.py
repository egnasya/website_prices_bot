import asyncio
import re
from urllib.parse import urlparse
import aiosqlite
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire import webdriver
from selenium.webdriver.support import expected_conditions as EC
from xvfbwrapper import Xvfb

from domains_selectors import DOMAIN_SELECTOR, DOMAIN_SELECTOR_ADD, DOMAIN_SELECTOR_SOLD_OUT
import manipulation_db


vdisplay = Xvfb()
vdisplay.start()


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

                if availability == 0 and availability != old_availability:
                    notification_message = (f'Вашего товара {product_name} больше нет в наличии. Можете отписаться от '
                                            f'отслеживания или подождать наличия (я уведомлю об этом).\n{url}')
                elif availability == 1 and availability != old_availability and new_price:
                    if int(new_price) == int(old_price):
                        notification_message = f'Ваш товар {product_name} снова в наличии! Цена не изменилась.\n{url}'
                    else:
                        diff = int(new_price) - int(old_price)
                        notification_message = (f'Ваш товар {product_name} снова в наличии и цена изменилась!\n'
                                                f'Новая цена: {new_price} ({diff}).\n{url}')
                elif new_price and int(new_price) != int(old_price):
                    diff = int(new_price) - int(old_price)
                    notification_message = (f'Цена на ваш товар {product_name} изменилась!\nНовая цена: {new_price}'
                                            f' ({diff}).\n{url}')

                if notification_message:
                    if user_id not in notifications:
                        notifications[user_id] = []
                    notifications[user_id].append(notification_message)

    return notifications


async def get_price(site_url, key, old_price):
    loop = asyncio.get_running_loop()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-setuid-sandbox")
    chrome_options.add_argument('--remote-debugging-pipe')
    chrome_options.add_argument("--headless")
    #chrome_options.add_argument("user-agent='Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 YaBrowser/20.12.1.178 Yowser/2.5 Safari/537.36'")
    service = Service(executable_path='/home/nastya/website_prices_bot/chromedriver')
    with webdriver.Chrome(executable_path=service, options=chrome_options) as driver:
        driver.implicitly_wait(3)

        try:
            await loop.run_in_executor(None, driver.get, site_url)

            sold_out_selector = DOMAIN_SELECTOR_SOLD_OUT.get(key)
            if sold_out_selector:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, sold_out_selector)))
                sold_out_elements = await loop.run_in_executor(None, driver.find_elements, By.CSS_SELECTOR, sold_out_selector)
                if sold_out_elements:
                    return old_price, 0

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, DOMAIN_SELECTOR[key])))
            price_elements = await loop.run_in_executor(None, driver.find_elements, By.CSS_SELECTOR, DOMAIN_SELECTOR.get(key))
            if not price_elements:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, DOMAIN_SELECTOR_ADD[key])))
                price_elements = await loop.run_in_executor(None, driver.find_elements, By.CSS_SELECTOR, DOMAIN_SELECTOR_ADD.get(key))

            if price_elements:
                price = price_elements[0].text
            else:
                print('Элемент с css-селекторами из базы данных на странице не найдены.')
                return old_price, 1

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
                return old_price, 1
        except Exception as e:
            print(f'Произошла непредвиденная ошибка: {e}')
            return old_price, 1

        finally:
            driver.quit()
            vdisplay.stop()
