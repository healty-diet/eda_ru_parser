# Eda.ru site parser

This program is designed to parse recipes from the [eda.ru](http://eda.ru/).

Data is parsed to the json format and written to the directory provided by the user.

## Legal note

This software is designed _only_ for personal use and supposed to be an alternative form of web-site using. All the data obtained with this software belongs to [eda.ru](http://eda.ru/). In order to use collected data in your project or for business you should contact the site administration first to obtain the approval.

## Examples

Example of the result .json file:

```json
{
  "name": "Example name",
  "serves_amount": 4,
  "ingredients": [
    {
      "example_ingredient": {
        "example_measure": 1.0
      }
    }
  ],
  "text": "1. Do something\n2. Do something else",
  "energy_value_per_serving": {
    "calories": "245",
    "protein": "20",
    "fat": "11",
    "carbohydrates": "14"
  }
}
```

## Usage

```sh
usage: eda_ru_parser [-h] --output OUTPUT

Parser for eda.ru site

optional arguments:
  -h, --help       show this help message and exit
  --output OUTPUT  name of the output folder
```

In the destination folder a separate file will be created for every recipe. File names will be "0.json", "1.json" etc.

**Please note** that this application requires a Tor browser to be running during the whole process of parsing.
This is required because of proxy usage.

## LICENSE

Calorizator parser is licensed under the MIT License.
See [LICENSE](LICENSE) for details.
