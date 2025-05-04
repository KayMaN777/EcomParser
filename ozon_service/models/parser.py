import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.support.ui import WebDriverWait
from shutil import which
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import time
import logging

load_dotenv()

PROXY = os.getenv("OZON_PROXY")

chromium_path = which("chromium") or which("chromium-browser")
if chromium_path is None:
    raise RuntimeError("Chromium не найден!")

class OzonParser:
    def __init__(self, verbose=False):
        self.logger = logging.getLogger('__ozon_parser__')
        self.logger.setLevel(logging.DEBUG if verbose else logging.INFO)
        options = uc.ChromeOptions()
        options.add_argument('--disable-gpu')
        options.add_argument("--no-sandbox")
        options.add_argument("--headless=new")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

        if PROXY:
            self.logger.info(f"Используем прокси: {PROXY}")
            options.add_argument(f'--proxy-server={PROXY}')
        else:
            self.logger.warning("Прокси не задан")

        self.driver = uc.Chrome(
            options=options,
            browser_executable_path=chromium_path
        )
        self.driver.implicitly_wait(2)

    @staticmethod
    def match_order(order):
        match order:
            case 'По популярности':
                return 'score'
            case 'Сначала дешевые':
                return 'price'
            case 'Сначала дорогие':
                return 'price_desc'
            case 'По рейтингу':
                return 'rating'
            case 'По новинкам':
                return 'new'
            case _:
                return 'score'

    def wait_products(self, min_count, max_scrolls=20):
        scroll_pause_time = 1.2
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        for _ in range(max_scrolls):
            products = self.collect_product_links(fetch_only=True)
            if len(products) >= min_count:
                break
            
            self.logger.debug(f"Товаров найдено: {len(products)}. Скроллим дальше...")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def collect_product_links(self, fetch_only=False):
        links = set()
        elements = self.driver.find_elements(By.CSS_SELECTOR, 'a[href^="/product/"]')
        for elem in elements:
            href = elem.get_attribute("href")
            if href:
                links.add(href)
        if fetch_only:
            return list(links)
        self.logger.info(f"[+] Ссылки на товары собраны: {len(links)}")
        return list(links)
    
    def open_new_tab(self, url):
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.driver.get(url)
        time.sleep(2)

    def extract_product_info(self, product_url):
        try:
            self.open_new_tab(product_url)
            
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')
            
            # Product ID
            try:
                product_id = self.driver.find_element(
                    By.XPATH, '//div[contains(text(), "Артикул: ")]'
                ).text.split('Артикул: ')[1]
            except Exception:
                product_id = None

            # Name
            try:
                product_name = soup.find('div', attrs={"data-widget": 'webProductHeading'}).find('h1').get_text(strip=True)
            except Exception:
                product_name = ''
            
            # Rating & reviews
            try:
                stat = soup.find('div', attrs={"data-widget": 'webSingleProductScore'}).text.strip()
                if " • " in stat:
                    product_stars, product_reviews = map(str.strip, stat.split(' • '))
                else:
                    product_stars, product_reviews = stat, None
            except Exception:
                product_stars = product_reviews = None

            # Prices
            try:
                price_block = soup.find('div', attrs={"data-widget": "webPrice"})
                spans = price_block.find_all('span')
                if len(spans) > 1:
                    discount_price = spans[0].text.strip()
                    ozon_card_price = spans[1].text.strip()
                else:
                    discount_price = ozon_card_price = None
            except Exception:
                discount_price = ozon_card_price = None

            # Brand
            try:
                brand_elem = soup.find('span', string="Бренд")
                if brand_elem:
                    brand = brand_elem.find_parent().find('span').text.strip()
                else:
                    brand = "No brand"
            except Exception:
                brand = "No brand"

            info = {
                'brand': brand,
                'product_id': product_id,
                'name': product_name,
                'price': discount_price,
                'discount_price': ozon_card_price,
                'rating': product_stars,
                'reviews': product_reviews,
                'url': product_url
            }
            return info
        except Exception as ex:
            self.logger.error(f"Ошибка при парсинге товара {product_url}: {ex}")
            return None
        finally:
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])

    def process_search_results(self, desired_count):
        self.wait_products(desired_count)
        links = self.collect_product_links()
        links = links[:desired_count]
        result = []
        for link in links:
            data = self.extract_product_info(link)
            if data:
                result.append(data)
            time.sleep(1.5)
        return result

    def search(self, query, num, order):
        self.logger.info(f"Старт поиска: '{query}', {num} товаров, сортировка: {order}")
        self.driver.get('https://www.ozon.ru/')
        time.sleep(2)

        try:
            find_input = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.NAME, 'text'))
            )
        except Exception as e:
            self.logger.error(f"[!] Не найдено поле поиска! {e}")
            self.driver.save_screenshot("find_input_fail.png")
            self.driver.quit()
            return None

        find_input.clear()
        find_input.send_keys(query)
        find_input.send_keys(Keys.ENTER)
        time.sleep(2)

        sorting = self.match_order(order)
        search_url = f"{self.driver.current_url}&sorting={sorting}"
        self.driver.get(search_url)
        time.sleep(2)

        data = self.process_search_results(num)
        self.driver.quit()

        return {
            'filename': f'ozon search {query}',
            'data': data
        }

    def category(self, link, num, order):
        self.logger.info(f"Старт поиска: '{link}', {num} товаров, сортировка: {order}")
        self.driver.get(link)
        time.sleep(2)

        sorting = self.match_order(order)
        search_url = f"{self.driver.current_url}&sorting={sorting}"
        self.driver.get(search_url)
        time.sleep(2)

        data = self.process_search_results(num)
        self.driver.quit()

        return {
            'filename': f'ozon category {link}',
            'data': data
        }

    def seller(self, link, num, order):
        self.logger.info(f"Старт поиска: '{link}', {num} товаров, сортировка: {order}")
        self.driver.get(link)
        time.sleep(2)

        sorting = self.match_order(order)
        search_url = f"{self.driver.current_url}&sorting={sorting}"
        self.driver.get(search_url)
        time.sleep(2)

        data = self.process_search_results(num)
        self.driver.quit()

        return {
            'filename': f'ozon seller {link}',
            'data': data
        }
