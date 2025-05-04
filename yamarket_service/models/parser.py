import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.support.ui import WebDriverWait
from shutil import which
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import re
import time
import logging

load_dotenv()

PROXY = os.getenv("YAMARKET_PROXY")

chromium_path = which("chromium") or which("chromium-browser")
if chromium_path is None:
    raise RuntimeError("Chromium не найден!")

class YamarketParser:
    def __init__(self, verbose=False):
        self.logger = logging.getLogger('__yamarket_parser__')
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
                return ''
            case 'Сначала дешевые':
                return 'aprice'
            case 'Сначала дорогие':
                return 'dprice'
            case 'По рейтингу':
                return 'rating'
            case _:
                return ''

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
        elements = self.driver.find_elements(By.CSS_SELECTOR, 'a[href^="/product--"]')
        for elem in elements:
            href = elem.get_attribute("href")
            if href:
                if href.startswith("/"):
                    href = "https://market.yandex.ru" + href
                links.add(href)
        if fetch_only:
            return list(links)
        self.logger.info(f"[+] Ссылки на товары с Яндекс.Маркета собраны: {len(links)}")
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
            product_id = None
            for span in soup.find_all("span"):
                text = span.get_text(strip=True)
                if text.isdigit() and 7 <= len(text) <= 12:
                    product_id = text
                    break

            # Name
            try:
                product_name = soup.find("h1").get_text(strip=True)
            except Exception:
                product_name = ''
            
            # Brand
            brand = None
            for span in soup.find_all("span"):
                txt = span.get_text(strip=True)
                if txt.isalpha() and txt[0].isupper() and 2 < len(txt) < 30:
                    brand = txt
                    break
            
            # Price
            meta_price_tag = soup.find("meta", itemprop="price")
            price = meta_price_tag["content"] if meta_price_tag else None

            # Price yandex pay
            discount_price = None
            for div in soup.find_all("div"):
                # В div ищем "Цена с картой Яндекс Пэй:" и рядом сумму
                if div.get_text().find("Яндекс Пэй") != -1:
                    match = re.search(r"Цена с картой Яндекс Пэй[^:]*:\s*([0-9\s\u2009]+)", div.get_text())
                    if match:
                        discount_price = match.group(1).replace('\u2009', '').replace(' ', '')
                        break

            # Rating & reviews
            rating = None
            reviews = None
            for a in soup.find_all("a", href=True):
                if "/reviews" in a["href"]:
                    spans = a.find_all("span")
                    if spans:
                        rating = spans[0].get_text(strip=True)
                    if len(spans) > 2:
                        rev_text = spans[-1].get_text()
                        m = re.search(r"\d+", rev_text)
                        if m:
                            reviews = m.group()
                    break

            info = {
                'brand': brand,
                'product_id': product_id,
                'name': product_name,
                'price': price,
                'discount_price': discount_price,
                'rating': rating,
                'reviews': reviews,
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
        self.driver.get('https://market.yandex.ru/')
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
        search_url = f"{self.driver.current_url}&how={sorting}"
        self.driver.get(search_url)
        time.sleep(2)

        data = self.process_search_results(num)
        self.driver.quit()

        return {
            'filename': f'yandex market search {query}',
            'data': data
        }

    def category(self, link, num, order):
        self.logger.info(f"Старт поиска: '{link}', {num} товаров, сортировка: {order}")
        self.driver.get(link)
        time.sleep(2)

        sorting = self.match_order(order)
        search_url = f"{self.driver.current_url}&how={sorting}"
        self.driver.get(search_url)
        time.sleep(2)

        data = self.process_search_results(num)
        self.driver.quit()

        return {
            'filename': f'yandex market category {link}',
            'data': data
        }


    def seller(self, link, num, order):
        self.logger.info(f"Старт поиска: '{link}', {num} товаров, сортировка: {order}")
        self.driver.get(link)
        time.sleep(2)

        sorting = self.match_order(order)
        search_url = f"{self.driver.current_url}&how={sorting}"
        self.driver.get(search_url)
        time.sleep(2)

        data = self.process_search_results(num)
        self.driver.quit()

        return {
            'filename': f'yandex market seller {link}',
            'data': data
        }
