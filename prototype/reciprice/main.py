from flask import Blueprint, render_template

from . import models

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
    user = models.create_user(username)
    return '<h1>Created %s!</h1>' % user
