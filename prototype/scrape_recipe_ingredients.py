from bs4 import BeautifulSoup
import re
import urllib.request


def clean_soup(mess):
    return mess.get_text().strip().lower()


def load_soup(recipe_id, persons=None):
    # recipe_base_url = 'https://www.dk-kogebogen.dk/opskrifter/'
    ingredient_base_url = 'https://www.dk-kogebogen.dk/opskrifter/udskrift/u-kommentar-u-beregn-u-billede.php?id=%s'
    if persons is not None:
        ingredient_base_url += '&personer=%s'
        url = ingredient_base_url % (recipe_id, persons)
    else:
        url = ingredient_base_url % recipe_id
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')

    return soup


def get_recipe(soup):
    recipetable = soup.findAll('td', {'width': 300})[4]  # find the table containing the recipe
    for head in recipetable.findAll('table'):
        head.extract()
    recipe = clean_soup(recipetable)
    return recipe


def get_ingredients(soup):
    table = soup.find('table', {'cellpadding': 3})  # find the table containing ingredients
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

rege = re.compile('.*(\(|-|/|:).*', re.IGNORECASE)
all_ingredients = []
for i in range(10):
    soup = load_soup(0+i,4)
    ingredient_list = get_ingredients(soup)
    for l in ingredient_list:
        ingredient = l[2]
        if rege.search(l[2]) == None:
            all_ingredients.append(l[2] )
dist = {rr:all_ingredients.count(rr) for rr in all_ingredients}

dd = dist.keys()
ss = []
for key in dd:
    ss.append([key,dist[key]])

ss.sort(key = lambda x:x[1])
ss.reverse()
for i in ss:
    print(i)
