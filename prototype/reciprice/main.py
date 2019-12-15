from flask import Blueprint, render_template

from .extentions import mongo

from datetime import datetime, timezone

main = Blueprint("main", __name__)


@main.route('/')
def index():
    users = mongo.db.users
    return '<h1>Users in the system: %s</h1>' % str(users.count_documents({}))


@main.route("/user/<username>")
def user_profile(username):
    users = mongo.db.users
    user = users.find_one_or_404({"_id": username})
    return '<h1>%s</h1>' % str(user)


@main.route("/usercreate/<username>")
def user_create(username):
    users = mongo.db.users
    users.insert({'_id': username, 'created': datetime.now(timezone.utc)})
    return '<h1>Created %s!</h1>' % str(username)
