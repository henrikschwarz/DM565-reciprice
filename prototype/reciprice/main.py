from flask import Blueprint, render_template, request, flash, redirect, url_for
import re

import pymongo
from flask import Blueprint, render_template
from bson.json_util import dumps, loads
from .extentions import mongo

from . import models
from datetime import datetime, timezone

main = Blueprint("main", __name__)


@main.route('/')
def index():
    return render_template("main/index.html", userlist=models.get_usernames())


@main.route("/login")
def login():
    return render_template("main/login.html")


@main.route("/user/<username>")
def user_profile(username):
    username_capitalized = str(username).capitalize()
    user = models.load_user_or_404(username_capitalized)
    return '<h1>%s</h1>' % user


@main.route("/user/<username>/create")
def create_user(username):
    users = mongo.db.users
    users.insert({'username': username, 'created': datetime.now(timezone.utc)})
    return '<h1>Created %s!</h1>' % str(username)


@main.route("/recipe/create", methods=["GET", "POST"])
def create_recipe():
    if request.method == "POST":
        error = False  # primitive way to check for errors
        data = {}
        if request.form["recipe-name"]:
            data["name"] = request.form["recipe-name"]
        else:
            flash('Ingen opskrift navn')
            error = True

        try:
            if request.form["ingredients"] and request.form["amount"] and request.form["unit"]:
                ingredients = request.form.getlist("ingredients")
                amounts = request.form.getlist('amount')
                units = request.form.getlist('unit')
                ingredients_list = []
                for index in range(len(ingredients)):
                    ingredients_list.append([ingredients[index], amounts[index], units[index]])
                data["ingredient_list"] = ingredients_list
        except KeyError:
            flash('Mangler ingrediens data')
            error = True

        if request.form["procedure"]:
            data["procedure"] = request.form["procedure"]
        else:
            flash('Ingen Fremgangsmåde')
            error = True

        if error:
            print("error")
            return render_template('main/create_recipe.html')

        flash('Success, opskrift er tiløjet!')

        data["source"] = "useradded"
        data["created"] = datetime.utcnow()

        mongo.db.recipes.insert(data)
        name = data['name'].replace('/', '%2F')

        return redirect(url_for('main.recipe_get', name=name))

    return render_template("main/create_recipe.html")


@main.route("/recipes/<name>")
def recipe_get(name):
    name_slash_restored = name.replace('%2F', '/')
    recipe = models.get_recipe(name_slash_restored)
    ingredient = models.get_ingredient(name_slash_restored)
    product_suggestion = ingredient.get_product_list()
    return render_template('main/recipe.html', recipe=recipe, product_suggestion=product_suggestion)


@main.route("/recipes/")
def list_recipes():
    recipes = mongo.db.recipes.distinct('name')
    return render_template("main/recipes.html",
                           recipes=[(re.sub("\d+$", "", i).strip(), i.replace('/', '%2F')) for i in recipes])


@main.route("/ingredients_json/")
def ingredients_json():
    ingredients = mongo.db.ingredients.find({"name": {"$in": ["h"]}})
    dict_ingredient = dict()
    for item in ingredients:
        dict_ingredient[item["name"]] = item.name

    return dict_ingredient


@main.route("/ingredients/")
def list_ingredients():
    ingredients = mongo.db.ingredients.find()
    return render_template('main/ingredients.html', ingredients=ingredients)


@main.route("/ingredients/<name>/create")
def create_ingredient(name):
    ing = models.Ingredient(name, [], [])
    return '<h1>found %s!</h1>' % ing.insert()


#### Json

@main.route('/json/products/<ingredient_name>')
def list_products_json(ingredient_name):
    name_slash_restored = ingredient_name.replace('%2F', '/')
    ingredient = mongo.db.ingredients.find_one({'name': name_slash_restored})
    products = []
    for item in ingredient["product_list"]:
        product = mongo.db.products.find({'ean': item})
        products.append(product)
    data = {'products': products}
    return dumps(data, ensure_ascii=False)


@main.route("/json/recipes/")
def list_recipes_json():
    recipe_dict = {}
    recipes = mongo.db.recipes.find()
    l = []
    for item in recipes:
        l.append(item["name"])
    recipe_dict["recipes"] = l
    return dumps(recipe_dict, ensure_ascii=False)


@main.route("/json/recipes/<name>")
def list_specific_recipe_json(name):
    recipe_dict = {}
    name = str(name).capitalize()
    regex = '.*{0}.*'.format(name)
    recipes = mongo.db.recipes.find({"name": {"$regex": regex, '$options' : 'i'}})
    l = []
    for item in recipes:
        l.append(item["name"])
    recipe_dict["recipes"] = l
    return dumps(recipe_dict, ensure_ascii=False)


@main.route("/json/ingredients/")
def list_ingredients_json():
    ingredient_dict = dict()
    ingredients = mongo.db.ingredients.find()
    l = []
    for item in ingredients:
        l.append(item["name"])
    ingredient_dict["ingredients"] = l
    return dumps(ingredient_dict, ensure_ascii=False)


@main.route("/json/ingredients/<name>")
def list_specific_ingredient_json(name):
    ingredient_dict = dict()
    regex = r'.*%s.*' % name
    ingredients = mongo.db.ingredients.find({"name": {"$regex": regex, '$options' : 'i'}})
    l = []
    for item in ingredients:
        l.append(item["name"])
    ingredient_dict["ingredients"] = l
    return dumps(ingredient_dict, ensure_ascii=False)


@main.route("/ingredients/<name>")
def get_ingredient(name):
    ingredient = mongo.db.ingredients.find_one_or_404({"name": name})
    # used_in is a list consisting of tuple (reader-friendly_name, url_name) for each recipe that contains the ingredient
    used_in = [(re.sub("\d+$", "", i['name']).strip(), i['name'].replace('/', '%2F')) for i in
               mongo.db.recipes.find({'ingredient_list': {'$elemMatch': {'$elemMatch': {'$eq': name}}}})]
    return render_template("main/ingredient.html", ingredient=ingredient, used_in=used_in)
