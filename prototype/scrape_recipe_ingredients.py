from bs4 import BeautifulSoup
import re
import urllib.request


def get_recipe_ingredients(recipe_id, persons=4):
    # recipe_base_url = 'https://www.dk-kogebogen.dk/opskrifter/'
    ingredient_base_url = 'https://www.dk-kogebogen.dk/opskrifter/udskrift/u-kommentar-u-beregn-u-billede.php?id=%s&personer=%s'
    url = ingredient_base_url % (recipe_id, persons)
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')

    recipetable = soup.findAll('td', {'width': 300})[4] #find the table containing the recipe

    for head in recipetable.findAll('table'):
        head.extract()
    recipe = recipetable.get_text().strip()

    table = soup.find('table', {'cellpadding': 3}) #find the table containing ingredients
    rows = table.findAll('tr')
    ingredients = []
    for row in rows:
        amount, unit, ingredient = row.findAll('td')
        for span in ingredient.findAll('span'):
            span.extract()
        ingredients.append([amount.get_text().strip(), unit.get_text().strip(), ingredient.get_text().strip()])
    return [recipe, ingredients] 

print(get_recipe_ingredients(33005, 4))
