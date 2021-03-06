from datetime import datetime, timezone

from .extentions import mongo


class User:
    def __init__(self, username, created):
        self.username = username
        self.created = created

    # Returns the dictionary key that identifies this user
    def get_id(self):
        return self.username

    def get_filter(self):
        return {'username': self.username}

    # Replaces the database user date with data from this object.
    # Will create the user, if it does not already exist.
    def replace(self):
        mongo.db.users.replace_one(self.get_filter(), self.__dict__, upsert=True)

    # Changes the username, and optionally updates the database as well
    def set_username(self, username, update_db=True):
        if update_db:
            mongo.db.users.update_one({'username': username})
        self.username = username

    # Changes the creation time, and optionally updates the database as well
    def set_created(self, created, update_db=True):
        if update_db:
            mongo.db.users.update_one(self.get_filter(), {'created': created})
        self.created = created

    def __repr__(self):
        return 'User(%s, %s)' % (self.username, self.created)


# Returns a user object with data populated from the database
def load_user(username):
    user = mongo.db.users.find_one({'username': username})
    return User(user['username'], user['created'])


# Returns a user object or cause 404 error
def load_user_or_404(username):
    user = mongo.db.users.find_one_or_404({'username': username})
    return User(user['username'], user['created'])


# Creates a new user in the database and returns it as an object
# Warning: This will replace any existing user by that name
def create_user(username):
    user = User(username, datetime.now(timezone.utc))
    user.replace()
    return user


# Returns a list of each username in the database
def get_usernames():
    return list(map(str, mongo.db.users.distinct('username')))


# Returns the count of users
def user_count():
    return mongo.db.users.count_documents({})


class Recipe:
    def __init__(self, name, procedure, ingredient_list, source, created):
        self.name = name
        self.procedure = procedure
        self.ingredient_list = ingredient_list  # example of list [[amount, unit, ingredient],[amount, unit, ingredient]]
        self.source = source
        self.created = created

    def insert(self):
        recipes = mongo.db.recipes
        recipes.insert(self.__dict__)

    def __repr__(self):
        split_procedure = self.procedure.split(' ')
        procedure_short = ' '.join(split_procedure[:min(len(split_procedure), 5)])
        ingredients_short = self.ingredient_list[:min(len(self.ingredient_list), 3)]
        ingredients = ', '.join(i[2] for i in ingredients_short)
        return 'Recipe(Name: %s, Procedure: %s..., Ingredients: %s..., Source: %s, Created: %s)' %\
               (self.name, procedure_short, ingredients, self.source, self.created)


def get_recipe(name):
    recipe = mongo.db.recipes.find_one_or_404({'name': name})
    return Recipe(name=recipe['name'], procedure=recipe['procedure'], ingredient_list=recipe['ingredient_list'],
                  source=recipe['source'],
                  created=recipe['created'])


"""
The Ingredient class holds the name of the ingredient, a list of product identifiers, and if it has an alias.
"""
class Ingredient:
    def __init__(self, name, product_list=[], alias=[]):
        self.name = name
        self.alias = alias  # different names that are the same ingredient
        self.product_list = product_list  # link the products we have scraped from bilkas website

    def insert(self, db=mongo.db):
        return db.ingredients.insert(self.__dict__)

    def add_product_to_list(self, ean, db=mongo.db):
        if ean not in self.product_list:
            self.product_list.append(ean)
            db.ingredients.update({'name': self.name}, {'$set': {'product_list': self.product_list}})
        return self.product_list

    def get_product_list(self, db=mongo.db):
        if self.alias:
            eans = get_ingredient(self.alias[0]).product_list
        else:
            eans = self.product_list

        return [(i['ean'], i['name']) for i in mongo.db.products.find({'ean': {'$in': eans}})]

    def get_product_ean_list(self, db=mongo.db):
        if self.alias:
            eans = get_ingredient(self.alias[0]).product_list
        else:
            eans = self.product_list

        return [i['ean'] for i in mongo.db.products.find({'ean': {'$in': eans}})]


def get_ingredient(name, db=mongo.db):
    ingredient = mongo.db.ingredients.find_one({'name': name})
    return Ingredient(name=ingredient['name'], alias=ingredient['alias'], product_list=ingredient['product_list'])


class Product:
    def __init__(self, name, amount, unit, price, price_history, ean=0):
        self.ean = ean
        self.name = name
        self.amount = amount
        self.unit = unit
        self.price = price
        self.price_history = price_history

    # Replaces the database product data with data from this object.
    # Will create the product, if it does not already exist.
    def replace(self, db=mongo.db):
        db.products.replace_one({'ean': self.ean}, self.__dict__, upsert=True)

    def insert(self, db=mongo.db):
        db.products.insert(self.__dict__)

    def add_price_to_history(self, price, db=mongo.db):
        if price != self.price_history[-1]:
            self.price = price
            self.price_history.append(price)
            db.products.update({'ean': self.ean}, {'$set': {'price_history': self.price_history}})
        return self.price_history


def create_or_update_product(ean, title, price, amount=1, unit='stk', db=mongo.db):
    existing = db.products.find_one({'ean': ean})
    if existing is not None:
        product = Product(existing['name'], existing['amount'], existing['unit'], existing['price'], existing['price_history'], existing['ean'])
        product.add_price_to_history(price, db)
    else:
        product = Product(title, amount, unit, price, [price], ean)
        product.insert(db)
    return product
