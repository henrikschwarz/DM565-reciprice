from flask import Blueprint, render_template

from .extentions import mongo

from . import models
from datetime import datetime, timezone

main = Blueprint("main", __name__)


@main.route('/')
def index():
    return '<h1>Users in the system: %s<br>Usernames: %s</h1>' % (
        str(models.user_count()), ', '.join(models.get_usernames()))


@main.route("/user/<username>")
def user_profile(username):
    user = models.load_user_or_404(username)
    return '<h1>%s</h1>' % user


@main.route("/usercreate/<username>")
def user_create(username):
    users = mongo.db.users
    users.insert({'_id': username, 'created': datetime.now(timezone.utc)})
    return '<h1>Created %s!</h1>' % str(username)

@main.route("/recipecreate/<name>")
def recipecreate_create(name):
    re = models.Recipe(name, 'prode', ['fdd','fdds'], 'dk-kogebogen.dk', datetime.utcnow())
    re.insert()
    return '<h1>Created %s!</h1>' % 'lol' 

@main.route("/recipeget/<name>")
def recipe_get(name):
    return '<h1>found %s!</h1>' % models.get_recipe(name)

@main.route("/ingredientcreate/<name>")
def ingredient_create(name):
    ing = models.Ingredient(name, [], [])
    return '<h1>found %s!</h1>' % ing.insert()

@main.route("/ingredientget/<name>")
def ingredient_get(name):
    return '<h1>found %s!</h1>' % models.get_ingredient(name).name
