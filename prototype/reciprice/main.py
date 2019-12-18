from flask import Blueprint, render_template, request, flash, redirect, url_for
import re

import pymongo
from flask import Blueprint, render_template
from bson.json_util import dumps
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
        error = False # primitive way yo check for errors
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


@main.route("/recipe/<name>")
def recipe_get(name):
    name_slash_restored = name.replace('%2F', '/')
    return '<h1>found %s!</h1>' % models.get_recipe(name_slash_restored)


@main.route("/recipes/")
def list_recipes():
    recipes = sorted(mongo.db.recipes.distinct('name'))
    return render_template("main/recipes.html", recipes=[(re.sub("\d+$", "", i).strip(), i.replace('/', '%2F')) for i in recipes])


@main.route("/ingredients_json/")
def ingredients_json():
    ingredients = mongo.db.ingredients.find({"name": {"$in": ["h"]}})
    dict_ingredient = dict()
    for item in ingredients:
        dict_ingredient[item["name"]] = item

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

@main.route("/json/ingredients/")
def list_ingredients_json():
    ingredient_dict = dict()
    ingredients = mongo.db.ingredients.find()
    ingredient_dict["ingredients"] = list(ingredients)
    return dumps(ingredient_dict, ensure_ascii=False)


@main.route("/json/ingredients/<name>")
def list_specific_ingredient_json(name):
    ingredient_dict = dict()
    regex = r'%s' % name
    ingredients = mongo.db.ingredients.find({"name": {"$regex": regex}})
    ingredient_dict["ingredients"] = ingredients
    return dumps(ingredient_dict, ensure_ascii=False)

@main.route("/ingredients/<name>")
def get_ingredient(name):
    ingredient = mongo.db.ingredients.find_one_or_404({"name": name})
    #used_in is a list consisting of tuple (reader-friendly_name, url_name) for each recipe that contains the ingredient
    used_in = [(re.sub("\d+$", "", i['name']).strip(), i['name'].replace('/', '%2F')) for i in mongo.db.recipes.find({'ingredient_list':{'$elemMatch':{'$elemMatch':{'$eq':name}}}}).sort('name', pymongo.ASCENDING)]
    return render_template("main/ingredient.html", ingredient=ingredient, used_in=used_in)
