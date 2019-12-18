import concurrent

from bs4 import BeautifulSoup
import re
import time
import urllib.request
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed, ALL_COMPLETED
from pymongo import MongoClient
from mongoenv import MONGO_URI
from reciprice.models import *

client = MongoClient(MONGO_URI)

rege = re.compile('.*(\(|-|/|:|\.).*')


def clean_soup(mess):
    return mess.get_text().strip().lower()


def create_urls(recipe_id, no_recipes):
    ingredient_base_url = 'https://www.dk-kogebogen.dk/opskrifter/udskrift/u-kommentar-u-beregn-u-billede.php?id=%s'
    urls = []
    for i in range(no_recipes):
        urls.append(ingredient_base_url % str(int(recipe_id) + i))
    return urls


"""
get recipe at url
gets all ingredients of a recipe including amounts and units
"""


def get_recipe_url(url):
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')
    recipetable = soup.findAll('td', {'width': 300})[4]  # find the table containing the recipe
    for head in recipetable.findAll('table'):
        head.extract()
    recipe = clean_soup(recipetable)

    table = soup.find('table', {'cellpadding': 3})  # find the table containing ingredients
    rows = table.findAll('tr')
    ingredients = []
    for row in rows:
        amount, unit, ingredient = row.findAll('td')
        for span in ingredient.findAll('span'):
            span.extract()
        a_t, u_t, i_t = clean_soup(amount), clean_soup(unit), clean_soup(ingredient)

        if len(a_t) + len(u_t) + len(i_t) > 0:
            ingredients.append([a_t, u_t, i_t])

    return recipe


"""
returns the ingredients of one recipe at url, this does not include amounts and units
returns a list of ingredients
"""


def get_ingredients(url):
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')

    table = soup.find('table', {'cellpadding': 3})  # find the table containing ingredients
    rows = table.findAll('tr')
    ingredients = []
    for row in rows:
        ingredient = row.findAll('td')[2]  # the datafield containing the ingredients is the third field
        for span in ingredient.findAll('span'):
            span.extract()
        i_t = clean_soup(ingredient)

        if len(i_t) > 0 and rege.search(i_t) == None:
            ingredients.append(i_t)
    return ingredients


"""
take a recipe_id, the number of recipes, and a the name of a function to execute on the urls created
returns a list of results provided by the function given
"""


def execute_get_in_parallel(recipe_id, no_recipes, function):
    urls = create_urls(recipe_id, no_recipes)

    results = []
    thread_count = multiprocessing.cpu_count()
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        futures = [executor.submit(function, url) for url in urls]
        for result in as_completed(futures):
            results.append(result.result())

    return results


def make_ranking(lis):
    flat_list = []
    for x in lis:
        for y in x:
            flat_list.append(y)

    return flat_list


# 39027

def insert_ingredient_frequency():
    insert_list = make_ranking(execute_get_in_parallel(0, 10, get_ingredients))
    remove_dict = {}
    in_list = []

    for item in insert_list:
        if item not in remove_dict:
            in_list.append({'name': item, 'amount': insert_list.count(item)})
            remove_dict.update({item: 'True'})

    db = client.innovation
    collection = db.ingredient_frequency
    collection.insert_many(in_list)


def populate_ingredient_whitelist():
    db = client.innovation
    collection = db.ingredient_frequency
    ingredient_collection = db.ingredients

    lis = [100000, 10]
    for i in range(len(lis) - 1):
        for item in collection.find({"amount": {"$lt": lis[i], "$gt": lis[i + 1]}}).sort('amount', -1):
            if ingredient_collection.count_documents({'name': item['name']}) == 0:
                ing = Ingredient(item['name'], [], [])
                ingredient_collection.insert_one(ing.__dict__)
                reg = '(.* {0}$|^{0}.*)'.format(item['name'])
                for related_item in collection.find({'name': {'$regex': reg}, 'amount': {"$gt": lis[i + 1]}}).sort(
                        'amount', -1):
                    if related_item['name'] != item['name']:
                        related_ing = Ingredient(related_item['name'], [], [item['name']])

                        ingredient_collection.replace_one({'name': related_item['name']}, related_ing.__dict__,
                                                          upsert=True)

def is_whitelisted(ingredient):
    return client.innovation.ingredients.find_one({'name': ingredient})


def get_recipe_object(recipe_id):
    url = 'https://www.dk-kogebogen.dk/opskrifter/udskrift/u-kommentar-u-beregn-u-billede.php?id=' + str(recipe_id)
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')
    name = soup.find('h1').get_text()
    recipetable = soup.findAll('td', {'width': 300})[4]  # find the table containing the recipe
    for head in recipetable.findAll('table'):
        head.extract()
    procedure = clean_soup(recipetable)

    table = soup.find('table', {'cellpadding': 3})  # find the table containing ingredients
    rows = table.findAll('tr')
    ingredients = []
    for row in rows:
        amount, unit, ingredient = row.findAll('td')
        for span in ingredient.findAll('span'):
            span.extract()
        a_t, u_t, i_t = clean_soup(amount), clean_soup(unit), clean_soup(ingredient)

        if rege.search(i_t) is not None:
            return None

        if not is_whitelisted(i_t):
            return None

        if len(a_t) + len(u_t) + len(i_t) > 0:
            ingredients.append([a_t, u_t, i_t])

    recipe = Recipe(name, procedure, ingredients, 'dk-kogebogen-' + str(recipe_id), datetime.utcnow())
    return recipe


def scrape_recipes(start=0, end=39027):
    print('Scraping recipes from dk-kogebogen in interval', start, 'to', end)
    print('Datebase has', client.innovation.recipes.count_documents({}), 'recipes before scraping.')
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        futures = [executor.submit(get_recipe_object, i) for i in range(start, end + 1)]

        for result in as_completed(futures):
            recipe = result.result()
            if recipe is not None:
                client.innovation.recipes.replace_one({'source': recipe.source}, result.result().__dict__, upsert=True)

        concurrent.futures.wait(futures, timeout=None, return_when=ALL_COMPLETED)
    end_time = time.time()
    print('Scraping took', end_time-start_time, 'seconds.')
    print('Database now has', client.innovation.recipes.count_documents({}), 'recipes.')

#scrape_recipes(start=0)
