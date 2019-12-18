# Run Instructions:
### First time:
Initialize virtual environment\
Activate virtual environment\
Install requirements.txt on virtual environment\
Run `python setup-env.py` and input mongodb login\
### Every time:
Run flask with `flask run`


# Data Storage
### Ingredient
Each ingredient should have history of prices we have observed\
The estimated price should be gathered from the average, cheapest, or latest of observed prices\
Tags such as alias, when we want to redirect to another ingredient\
List of ingredients that are "free" such as water\
List of ingredients that the user most likely has already such as salt\

### Recipe
Each recipe should have a list of ingredient and an amount, preferably in litres or grams.\
Should have a multiline string on how to prepare the recipe\
Source: Which user submitted it, or a link to the original dk-kogebogen link\