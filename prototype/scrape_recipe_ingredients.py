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

def get_ingredient_ranking(recipe_id=0, no_recipes=10):
    rege = re.compile('.*(\(|-|/|:).*', re.IGNORECASE)
    all_ingredients = []
    for i in range(no_recipes):
        soup = load_soup(recipe_id+i)
        ingredient_list = get_ingredients(soup)
        for l in ingredient_list:
            ingredient = l[2]
            if rege.search(l[2]) == None:
                all_ingredients.append(l[2] )

    check_list = []
    ss = []
    for item in all_ingredients:
        if item not in check_list: 
            ss.append([item, all_ingredients.count(item)])
            check_list.append(item)

    ss.sort(key = lambda x:x[1])
    ss.reverse()
    for i in ss:
        print(i)

get_ingredient_ranking()
