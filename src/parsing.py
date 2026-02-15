import re
import time
import logging
import asyncio
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import os
from typing import List, Dict

logger = logging.getLogger(__name__)
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")

# ===== СЛОВАРИ ДЛЯ НОРМАЛИЗАЦИИ =====
CITY_ALIASES = {
    "все": "all",
    "all": "all",
    "любой": "all",
    "москва": "moskva",
    "санкт-петербург": "sankt-peterburg",
    "спб": "sankt-peterburg",
    "новосибирск": "novosibirsk",
    "екатеринбург": "ekaterinburg",
    "казань": "kazan",
    "нижний новгород": "nizhniy_novgorod",
    "челябинск": "chelyabinsk",
    "самара": "samara",
    "омск": "omsk",
    "ростов-на-дону": "rostov-na-donu",
    "уфа": "ufa",
    "красноярск": "krasnoyarsk",
    "воронеж": "voronezh",
    "пермь": "perm",
    "волгоград": "volgograd",
    "краснодар": "krasnodar",
    "саратов": "saratov",
    "тюмень": "tyumen",
    "тольятти": "tolyatti",
    "ижевск": "izhevsk",
    "барнаул": "barnaul",
    "иркутск": "irkutsk",
    "хабаровск": "khabarovsk",
    "ярославль": "yaroslavl",
    "владивосток": "vladivostok"
}

CATEGORY_ALIASES = {
    "все": "all",
    "любые": "all",
    "ноутбуки": "noutbuki",
    "видеокарты": "videokarty",
    "процессоры": "processory",
    "телефоны": "telefony",
    "велосипеды": "velosipedy",
    "автозапчасти": "avtotovary",
    "мебель": "mebel",
    "одежда": "odezhda_obuv_aksessuary",
    "игры": "igry_pristavki_programmy",
    "инструменты": "instrumenty",
    "электроника": "elektronika",
    "бытовая техника": "bytovaya_tehnika",
    "книги": "knigi_i_zhurnaly",
    "спорт": "sport_i_otdyh",
    "животные": "zhivotnye",
    "недвижимость": "nedvizhimost",
    "работа": "rabota",
    "услуги": "uslugi",
    "транспорт": "transport",
    "для дома": "dlya_doma_i_dachi",
    "хобби": "hobbi_i_otdyh",
    "антиквариат": "kollektsionirovanie",
    "музыка": "muzykalnye_instrumenty"
}

# ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====
def normalize_city_name(city_name: str) -> str:
    """Приводит название города к слаг-формату для URL."""
    city_name = city_name.strip().lower()
    for alias, slug in CITY_ALIASES.items():
        if alias in city_name:
            return slug
    # Если не найдено в алиасах, пробуем сгенерировать слаг
    normalized = re.sub(r'[^\w-]', '', city_name.replace(' ', '_'))
    logger.debug(f"Normalized city '{city_name}' -> '{normalized}'")
    return normalized

def normalize_category_name(category_name: str) -> str:
    """Приводит название категории к слаг-формату для URL."""
    category_name = category_name.strip().lower()
    for alias, slug in CATEGORY_ALIASES.items():
        if alias in category_name:
            return slug
    normalized = re.sub(r'[^\w-]', '', category_name.replace(' ', '_'))
    logger.debug(f"Normalized category '{category_name}' -> '{normalized}'")
    return normalized

def extract_price(price_str: str) -> int:
    """Извлекает числовое значение цены из строки."""
    if not price_str:
        return 0
    digits = re.findall(r'\d+', price_str.replace(' ', ''))
    return int(''.join(digits)) if digits else 0

def setup_driver(browser_type: str = "firefox"):
    """Создаёт headless драйвер Selenium для указанного браузера."""
    try:
        if browser_type == "chrome":
            options = ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument(f"user-agent={USER_AGENT}")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=options
            )
        else:  # firefox
            options = FirefoxOptions()
            options.add_argument("--headless")
            options.set_preference("general.useragent.override", USER_AGENT)
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference("useAutomationExtension", False)

            driver = webdriver.Firefox(
                service=FirefoxService(GeckoDriverManager().install()),
                options=options
            )
        logger.info(f"Driver for {browser_type} initialized")
        return driver
    except Exception as e:
        logger.error(f"Driver initialization failed: {e}")
        return None

# ===== ПАРСИНГ AVITO =====
def parse_avito(driver, keyword: str, max_price: int, city: str, category: str) -> List[Dict]:
    """
    Парсит объявления с Avito по заданным параметрам.
    Возвращает список словарей с данными объявлений.
    """
    try:
        if city == "all":
            base_url = "https://www.avito.ru/all"
        else:
            base_url = f"https://www.avito.ru/{city}"

        if category == "all":
            url = f"{base_url}?q={keyword.replace(' ', '+')}&pmin=1000&pmax={max_price}"
        else:
            url = f"{base_url}/{category}?q={keyword.replace(' ', '+')}&pmin=1000&pmax={max_price}"

        logger.info(f"Parsing Avito: {url}")
        driver.get(url)
        time.sleep(3)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        items = soup.find_all("div", {"data-marker": "item"})
        logger.info(f"Found {len(items)} items on Avito")

        results = []
        for item in items:
            try:
                title_elem = item.find("h3", itemprop="name")
                price_elem = item.find("meta", itemprop="price")
                link_elem = item.find("a", itemprop="url")

                if not all([title_elem, price_elem, link_elem]):
                    continue

                ad_id = item.get("data-item-id", "")
                title = title_elem.text.strip()
                price = price_elem.get("content", "").strip()
                link = "https://www.avito.ru" + link_elem.get("href", "")

                city_display = "Все города" if city == "all" else city
                category_display = "Все категории" if category == "all" else category

                results.append({
                    "id": ad_id,
                    "title": title,
                    "price": f"{price} руб" if price else "Цена не указана",
                    "link": link,
                    "source": "Avito",
                    "city": city_display,
                    "category": category_display
                })
            except Exception as e:
                logger.warning(f"Failed to parse Avito item: {e}")
        return results
    except Exception as e:
        logger.error(f"Avito parsing error for {city}/{category}: {e}")
        return []

# ===== МОНИТОРИНГ ДЛЯ ПОЛЬЗОВАТЕЛЯ =====
async def monitor_user(user_id: int, manager):
    """
    Асинхронная задача мониторинга для конкретного пользователя.
    Запускается в отдельной корутине и выполняется пока active = True.
    """
    # Импортируем здесь, чтобы избежать циклических импортов
    from src.read import save_ad
    from src.handlers.monitor import send_notification, send_batch_summary

    logger.info(f"Starting monitoring for user {user_id}")
    settings = manager.get_settings(user_id)

    # Создаём драйвер для этого пользователя
    driver = setup_driver(settings.browser)
    if not driver:
        logger.error(f"Failed to create driver for user {user_id}")
        return

    # Локальная копия уже просмотренных ID
    seen_ids = manager.seen_ids.copy()

    try:
        while manager.monitoring_active.get(user_id, False):
            logger.info(f"Checking for user {user_id}")
            new_ads = []  # список новых объявлений за эту проверку

            for keyword in settings.keywords:
                logger.debug(f"Keyword: {keyword}")
                for city in settings.cities:
                    logger.debug(f"City: {city}")
                    category = settings.avito_category
                    # Запускаем синхронный парсинг в отдельном потоке
                    ads = await asyncio.to_thread(
                        parse_avito,
                        driver,
                        keyword,
                        settings.max_price,
                        city,
                        category
                    )
                    for ad in ads:
                        if ad["id"] and ad["id"] not in seen_ids:
                            logger.info(f"New ad: {ad['title']}")
                            seen_ids.add(ad["id"])
                            await save_ad(ad)
                            new_ads.append(ad)

            # Отправляем уведомления
            if new_ads:
                if len(new_ads) <= 3:
                    for ad in new_ads:
                        await send_notification(user_id, ad)
                else:
                    await send_batch_summary(user_id, new_ads)

            interval = settings.interval
            logger.info(f"Waiting {interval//60} minutes until next check")
            # Ждём с возможностью досрочного выхода
            for _ in range(interval // 10):
                if not manager.monitoring_active.get(user_id, False):
                    break
                await asyncio.sleep(10)

    except asyncio.CancelledError:
        logger.info(f"Monitoring cancelled for user {user_id}")
    except Exception as e:
        logger.exception(f"Unexpected error in monitor for user {user_id}: {e}")
    finally:
        if driver:
            driver.quit()
            logger.info(f"Driver closed for user {user_id}")
        logger.info(f"Monitoring stopped for user {user_id}")
