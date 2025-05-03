import os
import re
import logging
import requests
import time
from requests.adapters import HTTPAdapter
from http import HTTPStatus
from urllib3.util.retry import Retry
from random import randint, uniform
from dotenv import load_dotenv

load_dotenv()

MAX_PROXY_MISMATCH = 10
MAX_RETRIES = 3

def mock_data():
    return {
        "product_id": 123456789,
        "name": "Sample Product",
        "brand": "Sample Brand",
        "price": 1000,
        "discount_price": 800,
        "rating": 4.5,
        "reviews": 150,
    }

class WildberriesParser:
    def __init__(self, use_mock=False):
        self.search_url = os.getenv('WILDBERRIES_SEARCH_URL')
        self.proxies = [p.strip() for p in os.getenv('WILDBERRIES_PROXIES', '').split(',') if p.strip()]
        self.proxy_mismatch = {p: 0 for p in self.proxies}
        self.category_url = os.getenv('WILDBERRIES_CATEGORY_URL')
        self.seller_url = os.getenv('WILDBERRIES_SELLER_URL')
        self.logger = logging.getLogger('__wildberries_parser__')

        self.session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)

        raw_catalog = self.get_catalog_wb()
        self.categories = self.get_categories(raw_catalog) if raw_catalog else {}
        self.use_mock = use_mock

    @staticmethod
    def match_order(order):
        match order:
            case 'По популярности':
                return 'popular'
            case 'Сначала дешевые':
                return 'pricedown'
            case 'Сначала дорогие':
                return 'priceup'
            case 'По рейтингу':
                return 'rate'
            case 'По новинкам':
                return 'newly'
            case _:
                return 'popular'

    @staticmethod
    def get_seller_id(url):
        match = re.search(r'/seller/(\d+)', url)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def random_delay(a=1, b=3):
        time.sleep(uniform(a, b))

    def fetch_data(self, url, proxy=None):
        try:
            if proxy:
                proxies = {"http": proxy}
            else:
                proxies = None
            resp = self.session.get(url, proxies=proxies, timeout=8)
            if resp.status_code == HTTPStatus.OK:
                return resp.json(), resp.status_code
            return None, resp.status_code
        except Exception as e:
            self.logger.error(f'Exception while fetching data: {str(e)}')
            return None, HTTPStatus.INTERNAL_SERVER_ERROR

    def get_catalog_wb(self):
        catalog_list_url = os.getenv('WILDBERRIES_CATALOG_LIST_URL')
        for _ in range(MAX_RETRIES):
            data, _ = self.fetch_data(catalog_list_url)
            if data:
                return data
            WildberriesParser.random_delay()
        self.logger.error(f"Could not get catalog after {MAX_RETRIES} retries")
        return None

    def get_categories(self, catalog_wb):
        result = {}
        def extract(node):
            if not isinstance(node, dict):
                return
            url = node.get("url")
            if url and url not in result:
                result[url] = {
                    'shard': node.get('shard', ''),
                    'cat': node.get('cat', ''),
                    'query': node.get('query', '')
                }
            for child in node.get("childs", []):
                extract(child)
        if isinstance(catalog_wb, dict):
            extract(catalog_wb)
        elif isinstance(catalog_wb, list):
            for node in catalog_wb:
                extract(node)
        return result

    def parse_response(self, response):
        result = []
        try:
            products = response['data']['products']
        except (TypeError, KeyError):
            self.logger.warning("Bad structure in response")
            return result
        for product in products:
            product_info = {
                'brand': product.get('brand', ''),
                'product_id': product.get('id', ''),
                'name': product.get('name', ''),
                'price': product.get('price', {}).get('product', ''),
                'discount_price': product.get('price', {}).get('wallet', ''),
                'rating': product.get('reviewRating', ''),
                'reviews': product.get('feedbacks', ''),
            }
            result.append(product_info)
        return result

    def scrap_page(self, url):
        # фильтрация невалидных прокси (с большим числом ошибок)
        available_proxies = [p for p in self.proxies if self.proxy_mismatch.get(p, 0) < MAX_PROXY_MISMATCH]
        proxy = None
        if available_proxies:
            proxy = available_proxies[randint(0, len(available_proxies) - 1)]
        else:
            self.logger.warning('No proxies available or all are over mismatch limit, fetching without proxy.')
        result, status = self.fetch_data(url, proxy)
        if status == HTTPStatus.OK:
            return self.parse_response(result)
        elif status in (HTTPStatus.TOO_MANY_REQUESTS, HTTPStatus.FORBIDDEN):
            if proxy:
                self.proxy_mismatch[proxy] = self.proxy_mismatch.get(proxy, 0) + 1
        return None

    def process_pages(self, num, base_url, url_values):
        result = []
        page_size = 100
        total_pages = (num + page_size - 1) // page_size
        for page in range(total_pages):
            url_values['page'] = page
            url = base_url.format(**url_values)
            retries = 0
            data = None
            while retries < MAX_RETRIES and data is None:
                if self.use_mock:
                    data = [mock_data() for _ in range(min(page_size, num - page * page_size))]
                else:
                    data = self.scrap_page(url)
                    WildberriesParser.random_delay()
                retries += 1
            if data:
                result.extend(data)
            WildberriesParser.random_delay()
            if len(result) >= num:
                break
        return result[:num]

    def search(self, text, num, order):
        query_order = self.match_order(order)
        url_values = {
            'query': text,
            'sort': query_order,
        }
        data = self.process_pages(num, self.search_url, url_values)
        return {
            'filename': f'wildberries search {text}',
            'data': data,
        }

    def category(self, link, num, order):
        query_order = self.match_order(order)
        if link not in self.categories:
            self.logger.warning(f'Incorrect category url: {link}')
            return None
        url_values = {
            'query': self.categories[link].get('query', ''),
            'cat': self.categories[link].get('cat', ''),
            'sort': query_order,
        }
        data = self.process_pages(num, self.category_url, url_values)
        return {
            'filename': f'wildberries category {link}',
            'data': data
        }

    def seller(self, link, num, order):
        query_order = self.match_order(order)
        seller_id = self.get_seller_id(link)
        if seller_id is None:
            self.logger.warning(f'Incorrect seller url: {link}')
            return None
        url_values = {
            'sort': query_order,
            'supplier': seller_id,
        }
        data = self.process_pages(num, self.seller_url, url_values)
        return {
            'filename': f'wildberries seller {link}',
            'data': data
        }
