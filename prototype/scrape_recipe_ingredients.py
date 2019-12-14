from bs4 import BeautifulSoup
import urllib.request


def get_recipe_ingredients(recipe_id, persons=4):
    # recipe_base_url = 'https://www.dk-kogebogen.dk/opskrifter/'
    ingredient_base_url = 'https://www.dk-kogebogen.dk/opskrifter/udskrift/indkoebsliste.php?id=%s&personer=%s'
    url = ingredient_base_url % (recipe_id, persons)
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')

    table = soup.find('table', {'cellpadding': 3})
    rows = table.findAll('tr')
    for row in rows:
        amount, unit, ingredient = row.findAll('td')
        ingredient_text = ingredient.get_text().strip()
        if '\t' in ingredient_text:
            index = ingredient_text.index('\t')
            print('Ingredient:')
            print(ingredient_text[0:index])
            if len(amount.get_text()) > 0:
                print('Amount:')
                print(amount.get_text())
            if len(unit.get_text()) > 0:
                print('Unit:')
                print(unit.get_text())
            print('')

    return soup


#get_recipe_ingredients(33005, 4)
