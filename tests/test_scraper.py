import asyncio
import unittest
import sys
from unittest.mock import patch, AsyncMock

sys.path.append('/Users/anastasiaegorova/coding/website_prices_bot/')
from scraper import website_recognition, get_price


class TestWebsiteRecognition(unittest.TestCase):
    def test_website_recognition_valid_url(self):
        async def run_test():
            url = 'https://www.wildberries.ru/catalog/74756699/detail.aspx?targetUrl=MS&size=126108296'
            user_id = '336718279'

            result = await website_recognition(url, user_id)

            print(result)
            self.assertIn('Теперь вы отслеживаете товар', result)

        asyncio.run(run_test())

    @patch('scraper.get_price', new_callable=AsyncMock)
    def test_website_recognition_no_response_url(self, mock_get_price):
        async def run_test():
            invalid_url = 'https://market.yandex.ru/cc/oRhKILeойой'
            user_id = '336718279'

            mock_get_price.return_value = ('', '', '')

            result = await website_recognition(invalid_url, user_id)

            print(result)
            self.assertIn('Произошла ошибка при загрузке страницы', result)

        asyncio.run(run_test())

    @patch('scraper.get_price', new_callable=AsyncMock)
    def test_website_recognition_invalid_site(self, mock_get_price):
        async def run_test():
            invalid_url = 'market.yandex.ru/cc/oRhKILe'
            user_id = '336718279'

            mock_get_price.return_value = ('', '', '')

            result = await website_recognition(invalid_url, user_id)

            print(result)
            self.assertIn('Кажется, это не ссылка или она некорректна', result)

        asyncio.run(run_test())

    @patch('scraper.get_price', new_callable=AsyncMock)
    def test_website_recognition_no_support_site(self, mock_get_price):
        async def run_test():
            invalid_url = 'https://megamarket.ru/?admitad_uid=9b2ee0c4a4d149cc970e3897a8321b5a&utm_campaign=42896&utm_content=closer&utm_medium=cpa&utm_source=admitad&utm_term=34019'
            user_id = '336718279'

            mock_get_price.return_value = ('', '', '')

            result = await website_recognition(invalid_url, user_id)

            print(result)
            self.assertIn('Я пока не могу отслеживать цену с этого сайта', result)

        asyncio.run(run_test())

    def test_get_price_valid_site(self):
        async def run_test():
            site_url = 'https://www.mvideo.ru/products/televizor-hisense-100u7kq-400238500'
            key = 'www.mvideo.ru'
            user_id = '336718279'

            expected_name = 'Телевизор Hisense 100U7KQ'
            expected_price = '499999'
            expected_url = site_url

            name_product, price, url = await get_price(site_url, key, user_id)

            print(name_product, price)
            self.assertEqual(name_product, expected_name)
            self.assertEqual(price, expected_price)
            self.assertEqual(url, expected_url)

        asyncio.run(run_test())


if __name__ == '__main__':
    unittest.main()
