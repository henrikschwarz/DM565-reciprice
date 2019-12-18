import json
from json import JSONDecodeError

import requests
from time import sleep

BASE_URL = 'https://api.sallinggroup.com/v1-beta/'
PRODUCT_SUGGESTIONS = 'product-suggestions/relevant-products?query=%s'


def query_product_suggestions(query):
    headers = {"Authorization": "Bearer eb20ca15-7deb-4752-be07-bcb1abeb467a"}
    response = requests.get((BASE_URL + PRODUCT_SUGGESTIONS) % query, data=None, headers=headers)
    sleep(int(float(response.headers['Retry-After'])))
    try:
        js = response.json()
    except JSONDecodeError as e:
        js = None
        print(e)
        print(query)

    return js


def pretty_print(data):
    print(json.dumps(data, indent=4, ensure_ascii=False))
