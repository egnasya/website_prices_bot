from urllib.parse import urlparse
from domains_selectors import DOMAIN_SELECTOR, DOMAIN_SELECTOR_ADD


def website_recognition(url):
    domain_url = urlparse(url).netloc
    if domain_url in DOMAIN_SELECTOR:
        get_price(url, domain_url)
        return domain_url
    else:
        return 'Я пока не могу отслеживать цену с этого сайта :('


def get_price(site_url, key):
    # тут будет скрапер
    return 0