from flask import (Blueprint, render_template, request, session, url_for)
import functools

main = Blueprint("main", __name__, url_prefix="")

@main.route("/")
def index():
    return render_template("main/index.html")
