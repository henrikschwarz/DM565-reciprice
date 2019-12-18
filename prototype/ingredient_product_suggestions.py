from pymongo import MongoClient
from mongoenv import MONGO_URI
from reciprice.models import *
from reciprice.salling import *

db = MongoClient(MONGO_URI).innovation

def update_suggestions(ingredient):
    query_response = query_product_suggestions(ingredient)
    if query_response is None:
        return
    try:
        retry_in = query_response['Retry-After']
        print(retry_in)
        exit()
    except KeyError:
        pass

    try:
        suggestions = query_response['suggestions']
        products = []
        for suggestion in suggestions:
            try:
                products.append(create_or_update_product(suggestion['eans'], suggestion['title'], suggestion['price'], db=db))
            except KeyError:
                pass

        ingredient = get_ingredient(ingredient, db=db)

        for product in products:
            ingredient.add_product_to_list(product.ean, db=db)

    except KeyError:
        print('Key Error')
        print(query_response)


def populate_suggestions():
    ingredients = db.ingredients.find({'alias':{'$size': 0}, 'product_list':{'$size': 0}})
    for ingredient in ingredients:
        update_suggestions(ingredient['name'])

populate_suggestions()
