from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import json
import os
import multiprocessing as mp
import sqlite3
import logging


current_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.abspath(os.path.join(current_dir, '../log'))

logger = logging.getLogger('parse_description')
logger.setLevel(logging.DEBUG)
formatter_setup = {
    'fmt': '%(asctime)s - %(levelname)s - %(name)s - (%(filename)s.%(funcName)s(%(lineno)d)) - %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S'
    }
formatter = logging.Formatter(formatter_setup['fmt'], formatter_setup['datefmt'])
handler = logging.FileHandler(f"{log_path}/parse_description.log", mode='a+', encoding='utf-8')
handler.setFormatter(formatter)
logger.addHandler(handler)
lock = mp.Lock()


def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except Exception as e:
        logger.error(e)


def create_database(current_dir):
    db_path = os.path.abspath(os.path.join(current_dir, '../output/database.db'))
    try:
        with sqlite3.connect(db_path) as db:
            cursor = db.cursor()
            query = """
            CREATE TABLE IF NOT EXISTS description (
            category_name_level_0 TEXT,
            category_name_level_1 TEXT,
            category_name_level_2 TEXT,
            category_name_level_3 TEXT,
            category_name_level_4 TEXT,
            product_id INTEGER,
            description TEXT
            )
            """
            cursor.execute(query)
    except Exception as e:
        logger.error(e)


def insert_into_db(current_dir, category_name_level_0, category_name_level_1, category_name_level_2, category_name_level_3, category_name_level_4, product_id, description):
    db_path = os.path.abspath(os.path.join(current_dir, '../output/database.db'))
    try:
        with sqlite3.connect(db_path) as db:
            cursor = db.cursor()
            query = """
            INSERT INTO description (
                category_name_level_0,
                category_name_level_1,
                category_name_level_2,
                category_name_level_3,
                category_name_level_4,
                product_id,
                description
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (category_name_level_0, category_name_level_1, category_name_level_2, category_name_level_3, category_name_level_4, product_id, description))
            db.commit()
    except Exception as e:
        logger.error(e)


def click_button(driver, xpath):
    try:
        button = WebDriverWait(driver, timeout=1, poll_frequency=.2).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        button.click()
    except:
        pass


def get_description(driver, xpath):
    try:
        click_button(driver, xpath)
        description_element = WebDriverWait(driver, timeout=1, poll_frequency=.2).until(EC.visibility_of_element_located((By.CLASS_NAME, "option__text")))
        return description_element.text
    except:
        return None


def parse_description(current_dir, parsed_category_with_product_ids):
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-in-process-stack-traces")
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    chrome_options.add_argument("--disable-animations")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--incognito") 
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-crash-reporter")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--log-level=3') # INFO = 0, WARNING = 1, LOG_ERROR = 2, LOG_FATAL = 3.

    with webdriver.Chrome(options=chrome_options) as driver:
        for category_index, element in enumerate(parsed_category_with_product_ids):
            category_name_level_0 = element.get('category_name_level_0', None)
            category_name_level_1 = element.get('category_name_level_1', None)
            category_name_level_2 = element.get('category_name_level_2', None)
            category_name_level_3 = element.get('category_name_level_3', None)
            category_name_level_4 = element.get('category_name_level_4', None)
            products_ids = element.get('product_ids', None)

            print(f"Категория {category_index + 1} из {len(parsed_category_with_product_ids)}")
            print(f"{category_name_level_0} - {category_name_level_1} - {category_name_level_2}")

            if len(products_ids) == 0:
                continue

            for product_index, product_id in enumerate(products_ids):
                print(f"\r{product_index} of {len(products_ids)}", end='\r')
                driver.implicitly_wait(1)
                driver.get(f"https://www.wildberries.ru/catalog/{product_id}/detail.aspx")

                click_button(driver, "//button[contains(text(), 'Да, мне есть 18 лет')]")
                description = get_description(driver, "//button[contains(text(), 'Все характеристики и описание')]")
                insert_into_db(current_dir, category_name_level_0, category_name_level_1,
                                category_name_level_2, category_name_level_3,
                                category_name_level_4, product_id, description)
                
                if not description:
                    with lock:
                        logger.error(f"{category_index + 1} - {category_name_level_0} - {category_name_level_1} - {category_name_level_2} - {category_name_level_3} - {category_name_level_4} - {product_id}")


def split_for_4_parts(parsed_category_with_product_ids):
    split_index1 = len(parsed_category_with_product_ids) // 4
    split_index2 = split_index1 * 2
    split_index3 = split_index1 * 3
    first_part = parsed_category_with_product_ids[:split_index1]
    second_part = parsed_category_with_product_ids[split_index1:split_index2]
    third_part = parsed_category_with_product_ids[split_index2:split_index3]
    fourth_part = parsed_category_with_product_ids[split_index3:]
    return first_part,second_part,third_part,fourth_part


def parse_in_process(current_dir, first_part, second_part, third_part, fourth_part):
    process1 = mp.Process(target=parse_description, args=(current_dir, first_part))
    process2 = mp.Process(target=parse_description, args=(current_dir, second_part))
    process3 = mp.Process(target=parse_description, args=(current_dir, third_part))
    process4 = mp.Process(target=parse_description, args=(current_dir, fourth_part))

    process1.start()
    process2.start()
    process3.start()
    process4.start()

    process1.join()
    process2.join()
    process3.join()
    process4.join()


if __name__ == '__main__':

    with lock:
        logger.info('START')

    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_json_path = os.path.abspath(os.path.join(current_dir, '../output/parsed_category_with_product_ids.json'))

    parsed_category_with_product_ids = load_json(input_json_path)
    first_part, second_part, third_part, fourth_part = split_for_4_parts(parsed_category_with_product_ids)
    create_database(current_dir)
    parse_in_process(current_dir, first_part, second_part, third_part, fourth_part)

    with lock:
        logger.info('FINISH')