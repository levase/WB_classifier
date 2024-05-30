import json
import os
import requests
import time
import logging


current_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(current_dir, '../log/parse_product_id.log')

logger = logging.getLogger('parse_product_id')
logger.setLevel(logging.DEBUG)
formatter_setup = {
    'fmt': '%(asctime)s - %(levelname)s - %(name)s - (%(filename)s.%(funcName)s(%(lineno)d)) - %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S'
    }
formatter = logging.Formatter(formatter_setup['fmt'], formatter_setup['datefmt'])
handler = logging.FileHandler(log_path, mode='w+', encoding='utf-8')
handler.setFormatter(formatter)
logger.addHandler(handler)


def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except Exception as e:
        logger.error(e)


def save_to_json(data, output_json_path):
    try:
        with open(output_json_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(e)


def get_response(url):
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'ru,en;q=0.9',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "YaBrowser";v="24.4", "Yowser";v="2.5"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 YaBrowser/24.4.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url=url, headers=headers)
        return response
    except requests.exceptions as e:
        logger.error(e)


def get_product_ids(category):
    result = []

    category_name_level_0 = category.get('category_name_level_0', None)
    category_name_level_1 = category.get('category_name_level_1', None)
    category_name_level_2 = category.get('category_name_level_2', None)
    category_name_level_3 = category.get('category_name_level_3', None)
    category_name_level_4 = category.get('category_name_level_4', None)
    category_shard = category.get('category_shard')
    category_query = category.get('category_query')
    category_url = category.get('category_url')
    
    product_ids = []
    for page_num in range(1, 3): # берем только первые 2 страницы каждой категории. Максимум можно взять только 100 страниц.
        print(f"\r{category_name_level_0}---{category_name_level_1}---{category_name_level_2}---{category_name_level_3}---{category_name_level_4}---{page_num}", end='\r')
        url = f'https://catalog.wb.ru/catalog/{category_shard}/v2/catalog?appType=1&{category_query}&curr=rub&dest=12358271&page={page_num}&sort=popular&spp=30&uclusters=1'
    
        response = get_response(url)

        if response.status_code != 200 or (response.status_code == 200 and response.text == ''):
            attempts = 1
            while attempts < 5:
                response = get_response(url)
                if response.status_code == 200 and response.text != '':
                    break
                attempts += 1
                time.sleep(1)
        
        if response.status_code == 200 and response.text != '':
            products_list = response.json().get('data', None).get('products', None)

            for product in products_list:
                product_id = product.get('id', None)
                product_ids.append(product_id)

    product_dict = {
        'category_name_level_0': category_name_level_0,
        'category_name_level_1': category_name_level_1,
        'category_name_level_2': category_name_level_2,
        'category_name_level_3': category_name_level_3,
        'category_name_level_4': category_name_level_4,
        'category_shard': category_shard, 
        'category_query': category_query,
        'category_url': category_url,
        'product_ids': product_ids
    }
    result.append(product_dict)
    print(f"\nКоличество ID товаров - {len(product_ids)}")    
    return result


def get_category(categories_list):
    seen_category = []
    for category in categories_list:
        category_name = category.get('category_name_level_0')
        seen_category.append(category_name)
    seen_category = set(seen_category)
    return sorted(list(seen_category))


def update_data(output_json_path, categories_list, parse_category):
    count = sum(1 for x in categories_list if x.get('category_name_level_0') == parse_category)
    index = 0
    for category in categories_list:
        if category.get('category_name_level_0', None) == parse_category:
            print(f"\n{index + 1} of {count}")
            product_ids = get_product_ids(category)
            index += 1

            if not os.path.isfile(output_json_path):
                save_to_json(product_ids, output_json_path)
            else:
                data = load_json(output_json_path)
                data += product_ids
                save_to_json(data, output_json_path)


def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_json_path = os.path.join(current_dir, '../output/parsed_category.json')
    output_json_path = os.path.join(current_dir, '../output/parsed_category_with_product_ids.json')
    
    categories_list = load_json(input_json_path)
    parse_category = get_category(categories_list)
    
    for category in parse_category:
        update_data(output_json_path, categories_list, category)


if __name__ == "__main__":
    logger.info('START')
    main()
    logger.info('FINISH')
