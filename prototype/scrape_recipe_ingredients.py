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
        if len(ingredient_text) > 0:
            print('Ingredient:')
            print(ingredient_text)
        amount_text = amount.get_text().strip()
        if len(amount_text) > 0:
            print('Amount:')
            print(amount_text)
        unit_text = unit.get_text().strip()
        if len(unit_text) > 0 and (chr(160) != unit_text): #exclude non-breaking space
            print( 'Unit:')
            print(unit_text )
        print('')

    return soup

for i in range(5):
    get_recipe_ingredients(i+33000, 4)
