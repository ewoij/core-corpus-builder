import os
import logging
import requests
import math
import tqdm
import re
import json
import time

os.makedirs('logs', exist_ok=True)
logging.basicConfig(level=logging.INFO, handlers=[
    logging.StreamHandler(),
    logging.FileHandler(filename=os.path.join('logs', '_'.join([time.strftime('%Y%m%d-%H%M'), 'download_corpus']) + '.log'))
])

def query_core(query, page, page_size, api_key):
    params = {
        'page' : page,
        'pageSize' : page_size,
        'metadata' : True,
        'fulltext' : True,
        'citations' : False,
        'similar' : False,
        'duplicate' : False,
        'urls' : False,
        'faithfulMetadata' : False,
        'apiKey' : api_key
    }
    query_string = '&'.join(['{}={}'.format(k, str(v)) for k, v in params.items()])
    url = 'http://core.ac.uk/api-v2/articles/search/{}?{}'.format(query, query_string)
    return requests.get(url).json()

def remove_invalid_xml_10_chars(content):
    return re.sub('[^\u0009\r\n\u0020-\uD7FF\uE000-\uFFFD\uD800\uDBFF-\uDC00\uDFFF]', '', content)

def get_article_coreid(article):
    return article['id']

def get_page_article_list(content):
    return content['data']

def save_article(article_id, article, output_dir):
    fulltext = article.pop('fullText')
    fulltext = remove_invalid_xml_10_chars(fulltext)
    article_id_str = str(article_id).zfill(6)
    file = os.path.join(output_dir, '{}.fulltext.txt'.format(article_id_str))
    with open(file, encoding='utf-8', newline='', mode='w') as f:
        f.write(fulltext)
    file = os.path.join(output_dir, '{}.metadatas.json'.format(article_id_str))
    with open(file, encoding='utf-8', mode='w') as f:
        json.dump(article, f)

def save_corpus_info(output_dir, query, total_hits, max_articles):
    info = {
        'query': query,
        'total_hits': total_hits,
        'max_articles': max_articles
    }
    file = os.path.join(output_dir, '_corpus_info.json')
    with open(file, encoding='utf-8', mode='w') as f:
        json.dump(info, f, indent=4)

def download_corpus(query, api_key, output_dir, max_articles = 10000, page_size = 10):
    try:
        print('Querying core...')
        result = query_core(query, 1, page_size, api_key)
        articles_count = result["totalHits"]
        os.makedirs(output_dir, exist_ok=True)
        save_corpus_info(output_dir, query, articles_count, max_articles)
        logging.info('Query: %s', query)
        logging.info('Number of hits: %s', articles_count)
        articles_count = min(max_articles, articles_count)
        logging.info('Number of articles to download: %s', articles_count)
        page_count = math.ceil(articles_count / page_size)
        core_ids = set()
        article_id = 0
        for page_number in tqdm.tqdm(range(1, page_count + 1)):
            if page_number != 1:
                result = query_core(query, page_number, page_size, api_key)
            for article in get_page_article_list(result):
                core_id = get_article_coreid(article)
                if core_id in core_ids:
                    logging.warn("Article with core id '%s' was already downloaded", core_id)
                    continue
                save_article(article_id, article, output_dir)
                core_ids.add(core_id)
                article_id += 1
                if article_id >= max_articles:
                    return
    except:
        logging.exception('Unexpected error occured while downloading the articles.')
