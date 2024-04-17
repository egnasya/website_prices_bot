import re
from urllib.parse import urlparse
from selenium.common import NoSuchWindowException, TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from domains_selectors import DOMAIN_SELECTOR, DOMAIN_SELECTOR_ADD
from selenium import webdriver


async def website_recognition(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// или https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # домен...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...или ip
        r'(?::\d+)?'  # необязательный порт
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    if not regex.match(url):
        return 'Кажется, это не ссылка :('
    else:
        domain_url = urlparse(url).netloc
        if domain_url in DOMAIN_SELECTOR:
            result = await get_price(url, domain_url)
            return result if result is not None else 'Не удалось получить данные по данному URL.'
        else:
            return 'Я пока не могу отслеживать цену с этого сайта :('


async def get_price(site_url, key):
    global driver, price, name_product

    try:
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
            clean_price = re.sub('₽.*₽', '', price).strip()
            # save_in_db(name_product, clean_price, url_product)
            print(f'Товар {name_product} с ценой {clean_price} и ссылкой {site_url} сохранен в базу данных.')
            return f'Теперь вы отслеживаете товар: {name_product}\nЕго начальная цена: {price}\nСсылка: {site_url}'
        else:
            return 'Что-то пошло не так, попробуйте еще раз отправить ссылку.'

    finally:
        driver.quit()
