import re
from urllib.parse import urlparse
from selenium.common import WebDriverException, NoSuchWindowException, TimeoutException, StaleElementReferenceException, \
    NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from domains_selectors import DOMAIN_SELECTOR, DOMAIN_SELECTOR_ADD
from selenium import webdriver
from test import TEST


def website_recognition(url):
    domain_url = urlparse(url).netloc
    if domain_url in DOMAIN_SELECTOR:
        get_price(url, domain_url)
        return domain_url
    else:
        return 'Я пока не могу отслеживать цену с этого сайта :('


def get_price(site_url, key):
    global driver, price, name_product

    try:
        # options = webdriver.ChromeOptions()
        driver = webdriver.Chrome()
        driver.implicitly_wait(10)
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
            print(name_product)
        except NoSuchElementException:
            print('Элемент с тегом "h1" не найден на странице.')
        except Exception as e:
            print(f'Произошла непредвиденная ошибка: {e}')

        price_elements = driver.find_elements(By.CSS_SELECTOR, DOMAIN_SELECTOR[key])
        if price_elements:
            price = price_elements[0].text
        else:
            price_elements = driver.find_elements(By.CSS_SELECTOR, DOMAIN_SELECTOR_ADD[key])
            if price_elements:
                price = price_elements[0].text
            else:
                print('Элемент с css-селекторами из базы данных на странице не найдены.')

        price = re.sub('[\u00A0|\u2009]', '', price)
        price = re.sub('[A-Za-zА-Яа-я:]+', '', price)
        clean_price = re.sub('₽.*₽', '', price).strip()
        # save_in_db(name_product, clean_price, url_product)
        message(name_product, price, site_url)
        print(f'Товар {name_product} с ценой {clean_price} и ссылкой {site_url} сохранен в базу данных.')

    finally:
        driver.quit()


def message(name, price, url):
    return f'Теперь вы отслеживаете товар: {name}\nЕго начальная цена: {price}\nСсылка: {url}'


for url in TEST:
    website_recognition(url)