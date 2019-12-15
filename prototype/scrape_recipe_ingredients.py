from bs4 import BeautifulSoup
import urllib.request


def clean_soup(mess):
    return mess.get_text().strip().lower()


def get_recipe_ingredients(recipe_id, persons=4):
    # recipe_base_url = 'https://www.dk-kogebogen.dk/opskrifter/'
    ingredient_base_url = 'https://www.dk-kogebogen.dk/opskrifter/udskrift/indkoebsliste.php?id=%s&personer=%s'
    url = ingredient_base_url % (recipe_id, persons)
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')

    table = soup.find('table', {'cellpadding': 3})
    rows = table.findAll('tr')

    ingredients = []

    for row in rows:
        amount, unit, ingredient = row.findAll('td')
        for span in ingredient.findAll('span'):
            span.extract()

        # ingredients.append({'amount': amount.get_text(), 'unit': unit.get_text(), 'ingredient': ingredient.get_text()})
        a_t, u_t, i_t = clean_soup(amount), clean_soup(unit), clean_soup(ingredient)

        if len(a_t) + len(u_t) + len(i_t) > 0:
            ingredients.append([a_t, u_t, i_t])

    return ingredients


print(get_recipe_ingredients(33005, 4))
