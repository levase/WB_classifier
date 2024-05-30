import requests
import json
import os
import pandas as pd
import logging


current_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(current_dir, '../log/parse_category.log')

logger = logging.getLogger('parse_category')
logger.setLevel(logging.DEBUG)
formatter_setup = {
    'fmt': '%(asctime)s - %(levelname)s - %(name)s - (%(filename)s.%(funcName)s(%(lineno)d)) - %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S'
    }
formatter = logging.Formatter(**formatter_setup)
handler = logging.FileHandler(log_path, mode='w+', encoding='utf-8')
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_category():
    url = 'https://static-basket-01.wbbasket.ru/vol0/data/main-menu-ru-ru-v2.json'

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'ru,en;q=0.9',
        'cache-control': 'no-cache',
        'origin': 'https://www.wildberries.ru',
        'pragma': 'no-cache',
        'referer': 'https://www.wildberries.ru/',
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
        return response.json()
    except requests.exceptions as e:
        logger.error(e)


def prepare_items(response):
    result = []
    seen_category_ids = set()  # Для отслеживания уже просмотренных категорий

    for idx in range(len(response)):
        category_id = response[idx].get('id', None)
        category_shard = response[idx].get('shard', None)
        category_query = response[idx].get('query', None)
        category_url = response[idx].get('url', None)
        category_name_level_0 = response[idx].get('name', None)
        category_name_seo_level_0 = response[idx].get('seo', None)
        category_list_level_1 = response[idx].get('childs', [])

        if category_id not in seen_category_ids and len(category_list_level_1) == 0:  # Проверка на уникальность категории
            seen_category_ids.add(category_id)
            category = {
                'category_name_level_0': category_name_seo_level_0 if category_name_seo_level_0 is not None else category_name_level_0,
                'category_query': category_query,
                'category_shard': category_shard,
                'category_url': category_url,
            }
            result.append(category)

        for category_level_1 in category_list_level_1:
            category_id_level_1 = category_level_1.get('id', None)
            category_name_level_1 = category_level_1.get('name', None)
            category_name_seo_level_1 = category_level_1.get('seo', None)
            category_shard_level_1 = category_level_1.get('shard', None)
            category_query_level_1 = category_level_1.get('query', None)
            category_url_level_1 = category_level_1.get('url', None)
            category_list_level_2 = category_level_1.get('childs', None)

            if category_id_level_1 not in seen_category_ids and category_list_level_2 is None:
                seen_category_ids.add(category_id_level_1)
                category_dict = {
                    'category_name_level_0': category_name_level_0,
                    'category_name_level_1': category_name_seo_level_1 if category_name_seo_level_1 is not None else category_name_level_1,
                    'category_shard': category_shard_level_1,
                    'category_query': category_query_level_1,
                    'category_url': category_url_level_1,
                }
                result.append(category_dict)

            if category_id_level_1 not in seen_category_ids and category_list_level_2 is not None:
                seen_category_ids.add(category_id_level_1)

                for category_level_2 in category_list_level_2:
                    category_name_level_2 = category_level_2.get('name', None)
                    category_name_seo_level_2 = category_level_2.get('seo', None)
                    category_shard_level_2 = category_level_2.get('shard', None)
                    category_query_level_2 = category_level_2.get('query', None)
                    category_url_level_2 = category_level_2.get('url', None)
                    category_list_level_3 = category_level_2.get('childs', None)

                    if category_list_level_3 is None:
                        category_dict = {
                            'category_name_level_0': category_name_level_0,
                            'category_name_level_1': category_name_seo_level_1 if category_name_seo_level_1 is not None else category_name_level_1,
                            'category_name_level_2': category_name_seo_level_2 if category_name_seo_level_2 is not None else category_name_level_2,
                            'category_shard': category_shard_level_2,
                            'category_query': category_query_level_2,
                            'category_url': category_url_level_2,
                        }
                        result.append(category_dict)

                    if category_list_level_3 is not None:
                        
                        for category_level_3 in category_list_level_3:
                            category_name_level_3 = category_level_3.get('name', None)
                            category_name_seo_level_3 = category_level_3.get('seo', None)
                            category_shard_level_3 = category_level_3.get('shard', None)
                            category_query_level_3 = category_level_3.get('query', None)
                            category_url_level_3 = category_level_3.get('url', None)
                            category_list_level_4 = category_level_3.get('childs', None)

                            if category_list_level_4 is None:
                                category_dict = {
                                    'category_name_level_0': category_name_level_0,
                                    'category_name_level_1': category_name_seo_level_1 if category_name_seo_level_1 is not None else category_name_level_1,
                                    'category_name_level_2': category_name_seo_level_2 if category_name_seo_level_2 is not None else category_name_level_2,
                                    'category_name_level_3': category_name_seo_level_3 if category_name_seo_level_3 is not None else category_name_level_3,
                                    'category_shard': category_shard_level_3,
                                    'category_query': category_query_level_3,
                                    'category_url': category_url_level_3,
                                }
                                result.append(category_dict)

                            if category_list_level_4 is not None:
                                for category_level_4 in category_list_level_4:
                                    category_name_level_4 = category_level_4.get('name', None)
                                    category_name_seo_level_4 = category_level_4.get('seo', None)
                                    category_shard_level_4 = category_level_4.get('shard', None)
                                    category_query_level_4 = category_level_4.get('query', None)
                                    category_url_level_4 = category_level_4.get('url', None)
                                    category_list_level_5 = category_level_4.get('childs', None)
                                    category_dict = {
                                        'category_name_level_0': category_name_level_0,
                                        'category_name_level_1': category_name_seo_level_1 if category_name_seo_level_1 is not None else category_name_level_1,
                                        'category_name_level_2': category_name_seo_level_2 if category_name_seo_level_2 is not None else category_name_level_2,
                                        'category_name_level_3': category_name_seo_level_3 if category_name_seo_level_3 is not None else category_name_level_3,
                                        'category_name_level_4': category_name_seo_level_4 if category_name_seo_level_4 is not None else category_name_level_4,
                                        'category_shard': category_shard_level_4,
                                        'category_query': category_query_level_4,
                                        'category_url': category_url_level_4,
                                        'category_list_level_5': category_list_level_5
                                    }
                                    result.append(category_dict)
    return result


def save_to_json(parsed_category, output_json_path):
    try:
        with open(output_json_path, 'w', encoding='utf-8') as file:
            json.dump(parsed_category, file, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(e)


def save_to_xlsx(parsed_category, output_xlsx_path):
    columns=[
        'category_name_level_0', 'category_name_level_1', 'category_name_level_2',
        'category_name_level_3', 'category_name_level_4', 'category_shard',
        'category_query', 'category_url', 'category_list_level_5'
    ]
    dataframe = pd.DataFrame(parsed_category, columns=columns)

    try:
        with pd.ExcelWriter(output_xlsx_path) as writer:
            dataframe.to_excel(writer, index=False)
    except Exception as e:
        logger.error(e)


def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_json_path = os.path.join(current_dir, '../output/parsed_category.json')
    output_xlsx_path = os.path.join(current_dir, '../output/parsed_category.xlsx')
    
    response = get_category()
    parsed_category = prepare_items(response)
    
    save_to_json(parsed_category, output_json_path)
    save_to_xlsx(parsed_category, output_xlsx_path)

    


if __name__ == "__main__":
    logger.info('START')
    main()
    logger.info('FINISH')