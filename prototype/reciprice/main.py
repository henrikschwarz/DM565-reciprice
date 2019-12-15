from flask import Blueprint, render_template

from .extentions import mongo

main = Blueprint("main", __name__)


@main.route('/')
def index():
    user_collection = mongo.db.users
    user_collection.insert({'name': 'Lucas'})
    return '<h1>Added Lucas!</h1>'
