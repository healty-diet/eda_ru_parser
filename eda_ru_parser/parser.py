""" Parser for eda.ru site. """

from typing import Dict, List, Any, Union, Optional, Generator
from fractions import Fraction
import os
import json
import random
import requests
from bs4 import BeautifulSoup

from .proxy import StepResult, run_with_proxy

EDA_RU_URL = "https://eda.ru/recepty"
# This constant is discovered manually, it may change.
PAGES_AMOUNT = 291

# JSON type
JSONValue = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]
JSONType = Union[Dict[str, JSONValue], List[JSONValue]]

USER_AGENTS = [
    ("Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0"),  # firefox
    (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/57.0.2987.110 "
        "Safari/537.36"
    ),  # chrome
    (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/61.0.3163.79 "
        "Safari/537.36"
    ),  # chrome
    (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/61.0.3163.91 "
        "Safari/537.36"
    ),  # chrome
    (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/62.0.3202.89 "
        "Safari/537.36"
    ),  # chrome
    (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/63.0.3239.108 "
        "Safari/537.36"
    ),  # chrome
]


def random_headers():
    """ Returns random header for request. """
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }


def get_recipes_json(response: requests.Response) -> JSONType:
    """ Function that gets <div id='main-content'>..</div> from the response. """
    soup = BeautifulSoup(response.content)

    return json.loads(soup.find("script", {"type": "application/ld+json"}).text)


def split_ingredient(ingredient_str: str) -> Dict[str, Dict[str, float]]:
    """ Parsed string with ingredient to dict like {'ingr': {'gr.': 100.0}}
    'to taste' is parsed like {'ingr': {'to taste': 1.0}} """

    to_taste_str = "по вкусу"
    if to_taste_str in ingredient_str:
        return {ingredient_str.split(to_taste_str)[0]: {to_taste_str: 1.0}}

    ingredient_str_splitted = ingredient_str.split()
    measure_name = ""
    amount = 0.0
    ingredient_name = ""
    measure_index = 0
    # Go in reverse to parse measure name first, then amount, then ingredient name
    for idx, word in reversed(list(enumerate(ingredient_str_splitted))):
        if word[0].isdigit():
            # We found the amount.
            measure_index = idx
            amount = float(Fraction(word.replace(",", ".")))
            break

        measure_name = " ".join([word, measure_name])

    ingredient_name = " ".join(ingredient_str_splitted[:measure_index])

    return {ingredient_name: {measure_name: amount}}


def parse_recipe_from_json(element: JSONValue) -> Optional[JSONValue]:
    """ Takes json from eda.ru as argument and returns json in expected format. """
    if not isinstance(element, dict):
        return None

    # Blank layout of result recipe format.
    recipe = {
        "name": "",
        "serves_amount": 1,
        "ingredients": [],
        "text": "",
        "energy_value_per_serving": {"calories": 0.0, "protein": 0.0, "fat": 0.0, "carbohydrates": 0.0},
    }

    # Verify recipe layout.
    expected_fields = [
        ("name", str),
        ("recipeYield", str),
        ("recipeInstructions", list),
        ("recipeIngredient", list),
        ("nutrition", dict),
    ]
    for field, expected_type in expected_fields:
        if not element.get(field) or not isinstance(element[field], expected_type):
            continue

    recipe["name"] = element["name"]
    recipe["serves_amount"] = int(element["recipeYield"].split()[0])

    recipe_text_enumerated = [
        "{}. {}".format(idx, txt.rstrip()) for idx, txt in enumerate(element["recipeInstructions"], 1)
    ]
    recipe["text"] = os.linesep.join(recipe_text_enumerated)
    recipe["ingredients"] = [split_ingredient(ingr) for ingr in element["recipeIngredient"]]
    recipe["energy_value_per_serving"] = {
        "calories": element["nutrition"]["calories"],
        "protein": element["nutrition"]["proteinContent"],
        "fat": element["nutrition"]["fatContent"],
        "carbohydrates": element["nutrition"]["carbohydrateContent"],
    }

    return recipe


def load_and_parse_page(page: int) -> List[JSONValue]:
    """ Parses recipe links from the given page number. """
    page_content = requests.get(EDA_RU_URL, {"page": page}, headers=random_headers())

    result: List[JSONValue] = []

    recipes_json = get_recipes_json(page_content)

    if not isinstance(recipes_json, dict) or not isinstance(recipes_json["itemListElement"], list):
        # Not parsible.
        return []

    for element in recipes_json["itemListElement"]:
        # Skip all but recipes.
        if element.get("@type") != "Recipe":
            continue

        recipe = parse_recipe_from_json(element)

        if recipe:
            result.append(recipe)

    return result


def parser_generator(pages_amount: int) -> Generator[List[JSONValue], Optional[StepResult], None]:
    """ Generator that retrieves information from eda.ru """
    retries_amount = 10
    for page in range(1, pages_amount + 1):
        result: Optional[StepResult] = StepResult.OK
        for _ in range(retries_amount):
            result = yield load_and_parse_page(page)

            if result == StepResult.OK:
                break

        if result != StepResult.OK:
            print(f"Failed to load page {pages_amount}")


def main(args) -> None:
    """ Runs the application """
    output_folder = args.output

    def _flatten(data: List[List[Any]]) -> List[Any]:
        return [item for sublist in data for item in sublist]

    parser = parser_generator(PAGES_AMOUNT)
    result_entries = _flatten(run_with_proxy(parser))

    for idx, entry in enumerate(result_entries):
        file_name = f"{idx}.json"
        file_path = os.path.join(output_folder, file_name)
        with open(file_path, "w") as file:
            json.dump(entry, file, indent=2)


if __name__ == "__main__":
    DESTINATION_FOLDER = "../../../nutrition_data/recipes"

    class _Args:
        def __init__(self, destination_folder):
            self.output = destination_folder

    main(_Args(DESTINATION_FOLDER))
