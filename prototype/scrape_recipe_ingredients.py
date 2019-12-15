from bs4 import BeautifulSoup
import re
import urllib.request


def clean_soup(mess):
    return mess.get_text().strip().lower()

def get_recipe_ingredients(recipe_id, persons=4):
    # recipe_base_url = 'https://www.dk-kogebogen.dk/opskrifter/'
    ingredient_base_url = 'https://www.dk-kogebogen.dk/opskrifter/udskrift/u-kommentar-u-beregn-u-billede.php?id=%s&personer=%s'
    url = ingredient_base_url % (recipe_id, persons)
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')

    return [get_ingredients(soup), get_recipe(soup)]
        

def get_recipe(soup):
    recipetable = soup.findAll('td', {'width': 300})[4] #find the table containing the recipe
    for head in recipetable.findAll('table'):
        head.extract()
    recipe = clean_soup(recipetable)
    return recipe

def get_ingredients(soup):
    table = soup.find('table', {'cellpadding': 3}) #find the table containing ingredients
    rows = table.findAll('tr')
    ingredients = []
    for row in rows:
        amount, unit, ingredient = row.findAll('td')
        for span in ingredient.findAll('span'):
            span.extract()
        a_t, u_t, i_t = clean_soup(amount), clean_soup(unit), clean_soup(ingredient)

        if len(a_t) + len(u_t) + len(i_t) > 0:
            ingredients.append([a_t, u_t, i_t])
    return ingredients

print(get_recipe_ingredients(33005, 4))
