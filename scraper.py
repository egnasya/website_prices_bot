from urllib.parse import urlparse
from selenium.common import WebDriverException, NoSuchWindowException, TimeoutException, StaleElementReferenceException, \
    NoSuchElementException
from selenium.webdriver.common.by import By

from domains_selectors import DOMAIN_SELECTOR, DOMAIN_SELECTOR_ADD
from selenium import webdriver


def website_recognition(url):
    domain_url = urlparse(url).netloc
    if domain_url in DOMAIN_SELECTOR:
        get_price(url, domain_url)
        return domain_url
    else:
        return 'Я пока не могу отслеживать цену с этого сайта :('


def get_price(site_url, key):
    global driver

    try:
        # options = webdriver.ChromeOptions()
        driver = webdriver.Chrome()
        driver.implicitly_wait(15)
        driver.get(site_url)
    except TimeoutException:
        print('Время ожидания операции истекло.')
    except NoSuchWindowException:
        print('Окно браузера не найдено.')
    except Exception as e:
        print(f'Произошла непредвиденная ошибка: {e}')

    else:
        print('пока все кул')
        name_product = None
        price = None

        try:
            name_product = driver.find_element(By.TAG_NAME, 'h1')
            print(name_product.text)
        except NoSuchElementException:
            print('Элемент с тегом "h1" не найден на странице.')
        except Exception as e:
            print(f'Произошла непредвиденная ошибка: {e}')

    finally:
        driver.quit()

    return 0


get_price('https://www.wildberries.ru/catalog/181047832/detail.aspx?targetUrl=MS&size=29908097', 'www.wildberries.ru')