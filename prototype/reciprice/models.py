from datetime import datetime, timezone

from .extentions import mongo

class User:
    def __init__(self, username, created):
        self._id = username
        self.created = created

    # Returns the dictionary key that identifies this user
    def get_id(self):
        return {'_id': self.username}

    # Returns the dictionary representation of this user
    def get_dict(self):
        return self.__dict__ 

    # Replaces the database user date with data from this object.
    # Will create the user, if it does not already exist.
    def replace(self):
        mongo.db.users.replace_one(self.get_id(), self.get_dict(), upsert=True)

    # Changes the username, and optionally updates the database as well
    def set_username(self, username, update_db=True):
        if update_db:
            mongo.db.users.update_one(self.get_id(), {'_id': username})
        self.username = username

    # Changes the creation time, and optionally updates the database as well
    def set_created(self, created, update_db=True):
        if update_db:
            mongo.db.users.update_one(self.get_id(), {'created': created})
        self.created = created

# Returns a user object with data populated from the database
def load_user(username):
    users = mongo.db.users
    def __repr__(self):
        return 'User(%s, %s)' % (self.username, self.created)


# Returns a user object with data populated from the database
def load_user(username):
    user = mongo.db.users.find_one({'_id': username})
    return User(user['_id'], user['created'])


# Returns a user object or cause 404 error
def load_user_or_404(username):
    user = mongo.db.users.find_one_or_404({'_id': username})
    return User(user['_id'], user['created'])


# Creates a new user in the database and returns it as an object
# Warning: This will replace any existing user by that name
def create_user(username):
    user = User(username, datetime.now(timezone.utc))
    user.replace()
    return user

class Recipe:
    def __init__(self, name, procedure, ingredient_list, source, created):
        self._id = name
        self.procedure = procedure
        self.ingredient_list = ingredient_list
        self.source = source
        self.created = created

    def insert(self):
        recipes = mongo.db.recipes
        recipes.insert(self.__dict__)

def get_recipe(name):
    recipes = mongo.db.recipes
    return recipes.find_one_or_404(name)
    
 

class Ingredient:
    def __init__(self, name, alias, created, price_estimate, price_history):
        self.name = name
        self.alias = alias
        self.created = created
        self.price_estimate = price_estimate
        self.price_history = price_history

    def insert(self):
        ingredients = mongo.db.ingredient
        ingredients.insert(self.__dict__)
        


# Returns a list of each username in the database
def get_usernames():
    return list(map(str, mongo.db.users.distinct('_id')))


# Returns the count of users
def user_count():
    return mongo.db.users.count_documents({})
