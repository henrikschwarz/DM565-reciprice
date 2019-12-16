from bs4 import BeautifulSoup
import time
import re
import urllib.request
import multiprocessing
from concurrent.futures import ThreadPoolExecutor,as_completed
from concurrent.futures import Future
from pymongo import MongoClient

MONGO_URI = 'mongodb://peteradmin:Pepsi1609@pratgen.dk/innovation?authSource=admin'
client = MongoClient(MONGO_URI)

rege = re.compile('.*(\(|-|/|:|\.).*')


def clean_soup(mess):
    return mess.get_text().strip().lower()

def create_urls(recipe_id, no_recipes):
    ingredient_base_url = 'https://www.dk-kogebogen.dk/opskrifter/udskrift/u-kommentar-u-beregn-u-billede.php?id=%s'
    urls = [] 
    for i in range(no_recipes):
        urls.append(ingredient_base_url % str(int(recipe_id)+i))

    return urls

"""
get receipe at url
"""
def get_recipe(url):
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')
    recipetable = soup.findAll('td', {'width': 300})[4]  # find the table containing the recipe
    for head in recipetable.findAll('table'):
        head.extract()
    recipe = clean_soup(recipetable)
    return recipe

"""
gets all ingredients of a recipe including amounts and units
"""
def get_all_ingredients(url):
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')
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
    return ingredients

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
        ingredient = row.findAll('td')[2] #the datafield containing the ingredients is the third field
        for span in ingredient.findAll('span'):
            span.extract()
        i_t = clean_soup(ingredient)

        if len(i_t) > 0:
            if rege.search(i_t) == None:
                ingredients.append(i_t)
            
    return ingredients

"""
take a recipe_id, the number of recipes, and a the name of a function to execute on the urls created
returns a list of results provided by the function given
"""
def execute_get_in_parallel(recipe_id, no_recipes, function):
    urls = create_urls(recipe_id,no_recipes)

    results = []
    thread_count = multiprocessing.cpu_count()
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        futures = [ executor.submit(function, url) for url in urls]
        for result in as_completed(futures):
            results.append(result.result())

    return results

def make_ranking(lis):
    flat_list = []
    for x in lis:
        for y in x:
            flat_list.append(y)

    return flat_list 
#39027
insert_list = make_ranking(execute_get_in_parallel(0,39027,get_ingredients))
remove_dict = {}
in_list = []

for item in insert_list:
    if item not in remove_dict:
        in_list.append({'name': item, 'amount':insert_list.count(item)})
        remove_dict.update({item: 'True'})

db = client.innovation
collection = db.ingredient
collection.insert_many(in_list)
