### Data Storage
## Ingredient
Each ingredient should have history of prices we have observed
The estimated price should be gathered from the average, cheapest, or latest of observed prices

## Recipe
Each recipe should have a list of ingredient and an amount, preferably in litres or grams.
Should have a multiline string on how to prepare the recipe
Source: Which user submitted it, or a link to the original dk-kogebogen link
List of ingredients that are "free" such as water
List of ingredients that the user most likely has already such as salt

### Todos
Integrate Salling API to get ingredient prices
Integrate eTilbudsAvis API
Create db models
Web Scrape recipes from [dk-kogebogen](https://www.dk-kogebogen.dk/)
Perhaps enter some prices manually to initiate the database with some of the most common ingredient
Web Scrape prices from [coop](https://coop.dk/)
Web Scrape prices from [nemlig](https://www.nemlig.com/)