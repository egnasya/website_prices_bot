import re
from urllib.parse import urlparse
import requests
import validators
from selenium.common import NoSuchWindowException, TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

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
                return 'Произошла ошибка при загрузке страницы   :('

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
    global driver, price, name_product

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
<<<<<<< HEAD

=======
>>>>>>> e2a164cd7d6ea461f958ba77ba3bf8e9ab2b4dc0
        driver.implicitly_wait(3)
        driver.get(site_url)
    except TimeoutException:
        print('Время ожидания операции истекло.')
    except NoSuchWindowException:
        print('Окно браузера не найдено.')
    except Exception as e:
        print(f'Произошла непредвиденная ошибка: {e}')
    else:
        try:
            name_product = driver.find_element(By.TAG_NAME, 'h1').text.strip()
        except NoSuchElementException:
            print('Элемент с тегом "h1" не найден на странице.')
        except Exception as e:
            print(f'Произошла непредвиденная ошибка: {e}')

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
            price = re.sub('₽[0-9]+₽*', '', price).strip()
            if price.endswith('₽'):
                price = price[:-1]
            clean_price = price.replace(' ', '')
            await manipulation_db.add_or_update_product(user_id, site_url, name_product, clean_price, 1)
            print(f'Товар {name_product} с ценой {clean_price} и ссылкой {site_url} сохранен в базу данных.')
            return name_product, clean_price, site_url
        else:
            return name_product, 'error', site_url

    finally:
        driver.quit()
