from flask_wtf.csrf import CSRFProtect
from flask_pymongo import PyMongo

csrf = CSRFProtect()
mongo = PyMongo()