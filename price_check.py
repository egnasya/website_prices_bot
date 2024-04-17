import re
import sqlite3
from urllib.parse import urlparse
from domains_selectors import DOMAIN_SELECTOR, DOMAIN_SELECTOR_ADD
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from seleniumwire import webdriver
import manipulation_db
import scraper


def check_and_update_prices():
    conn = sqlite3.connect('users_products.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, URL, product_name, current_price FROM products_users")
    products = cursor.fetchall()

    for user_id, url, product_name, old_price in products:
        domain_url = urlparse(url).netloc
        new_price = scraper.website_recognition(url, domain_url)
        if new_price and new_price != old_price:
            diff = old_price - new_price
            manipulation_db.add_or_update_product(user_id, url, product_name, new_price)
            send_notification(user_id, url, product_name, new_price, diff)

    conn.close()

def get_price(site_url, key):
    global driver, price, name_product

    try:
        driver = webdriver.Chrome()
        driver.implicitly_wait(15)
        driver.get(site_url)
    except Exception as e:
        print(f'Произошла непредвиденная ошибка: {e}')
    else:
        last_price = price
        price = None
        price_elements = driver.find_elements(By.CSS_SELECTOR, DOMAIN_SELECTOR[key])
        if price_elements:
            price = price_elements[0].text
        else:
            price_elements = driver.find_elements(By.CSS_SELECTOR, DOMAIN_SELECTOR_ADD[key])
            if price_elements:
                price = price_elements[0].text
            else:
                print('Элемент с css-селекторами из базы данных на странице не найдены.')
        if price:
            price = re.sub('[\u00A0|\u2009]', '', price)
            price = re.sub('[A-Za-zА-Яа-я:]+', '', price)
            clean_price = re.sub('₽.*₽', '', price).strip()
            return clean_price
        else:
            return last_price

    finally:
        driver.quit()


def send_notification(user, url, name_product, price, diff):
    return f'Цена на ваш товар {name_product} изменилась!\nНовая цена: {price} ({diff})\n{url}'
