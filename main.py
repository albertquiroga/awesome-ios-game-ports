import logging
import re
import requests
from simplejson.errors import JSONDecodeError

from jinja2 import FileSystemLoader, Environment

logging.basicConfig(level=logging.INFO)

APP_IDS_FILE_PATH = 'ids.tsv'
SEPARATOR_CHAR = '\t'
VALIDATION_REGEX = "[0-9]+\t\".*\""

BASE_ITUNES_API_URL = 'https://itunes.apple.com/lookup?country=US&id='

TEMPLATE_FILE_NAME = 'README.md'
TEMPLATES_PATH = 'templates'
env = Environment(loader=FileSystemLoader(searchpath=TEMPLATES_PATH), trim_blocks=True)

OUTPUT_FILE_NAME = 'README.md'


class App:
    """
    App object representing an App Store applicaton
    """
    base_app_store_url = 'https://apps.apple.com/ie/app/awesome/id'

    def __init__(self, app_id: str, name: str = '', price: str = '', url: str = '', avg_score: float = ''):
        self.id = app_id
        self.name = name
        self.price = price
        self.url = url if url else self.base_app_store_url + app_id
        self.avg_score = avg_score

    def __str__(self):
        return f'{self.id} | {self.name} | {self.price} | {self.url}'

    def __repr__(self):
        return f'{self.id} | {self.name} | {self.price} | {self.url}'


def process_request(app_id: str, response: dict) -> App:
    """
    Processes the raw response of the iTunes API
    :param app_id: App ID in string format
    :param response: Response of the iTunes API
    :return: App object representing the application
    """
    if response.get('resultCount', 0) > 0:
        app = response_to_app(app_id, response)
        logging.info(app)
        return app
    else:
        logging.warning(f'No result for app id {app_id}, might be a collection')
        return App(app_id=app_id)


def response_to_app(app_id, response) -> App:
    """
    Turns the JSON response of the iTunes API into an App object
    :param app_id: App ID in string format
    :param response: JSON dictionary representing the response of the iTunes API
    :return: App object representing the application
    """
    result = response.get('results', list())[0]
    price = result.get('formattedPrice', 'Arcade') # If no price, it must be an Apple Arcade game
    name = result.get('trackName')
    avg_score = round(result.get('averageUserRatingForCurrentVersion'), 2)
    return App(app_id=app_id, name=name, price=price, avg_score=avg_score)


def filter_invalid_entries(entries: list) -> list:
    """
    Given a list of entries, it will filter out those that do not comply with the 
    regular expression defined in the VALIDATION_REGEX constant, and notify via
    logging
    :param entries: List of app entries
    :return: List of valid entries
    """
    def validate_entry(entry: str) -> bool:
        return bool(re.match(VALIDATION_REGEX, entry))

    filtered_entries = list(filter(lambda entry: validate_entry(entry), entries))
    if len(filtered_entries) < len(entries):
        logging.warning(f"Ignored {len(entries) - len(filtered_entries)} invalid entries from file")

    return filtered_entries


def process_entry(entry: str) -> App:
    """
    Given an app ID, turns that into an App object
    :param entry: App ID in string format
    :return: App object representing the application
    """
    entry = entry.strip()
    logging.info(f'Processing entry: {entry}')
    app_id = entry.split(SEPARATOR_CHAR)[0]
    full_url = BASE_ITUNES_API_URL + app_id
    response = get_api_response(full_url)
    return process_request(app_id, response)


def get_api_response(url: str) -> dict:
    """
    Given a URL, will try to run an HTTP GET on it and parse the response
    into a dictionary. The Apple API is sometimes failing to respond,
    so this method will try 3 times before giving up.
    :param url: URL to run GET to
    :return: JSON dictionary containing the API response
    """
    response = {}
    attempts = 3
    while attempts:
        try:
            response = requests.get(url).json()
            break
        except JSONDecodeError:
            logging.error(f'Error when parsing API response. Retrying... ({attempts})')
            attempts-=1

    return response


def parse_app_ids(file_path: str) -> list:
    """
    Given a list of app IDs, turns that into App objects
    :param file_path: Path to the file containing the list of app IDs
    :return: List of App objects representing those apps
    """
    logging.info(f'Parsing app IDs from {file_path}...')
    with open(file_path) as f:
        entries = f.readlines()
        entries.pop(0) # Remove header
        valid_entries = filter_invalid_entries(entries)
        apps = list(map(lambda entry: process_entry(entry), valid_entries))
        return sorted(apps, key= lambda app: app.name)


def generate_readme(output_path: str, apps_list: list):
    """
    Given a list of Apps, generates a README.md file with their information using Jinja2 templating and
    writes the result to the given output path
    :param output_path: Path where the README.md file must be written to
    :param apps_list: List of App objects
    :return: None
    """
    logging.info(f'Generating README.md file with results...')
    base_template = env.get_template(TEMPLATE_FILE_NAME)
    with open(output_path, "w") as f:
        f.write(base_template.render(apps_list=apps_list))


def main():
    """
    Main function. Parses the list of app ids into App objects, then generates the README file
    """
    apps = parse_app_ids(APP_IDS_FILE_PATH)
    generate_readme(OUTPUT_FILE_NAME, apps)


if __name__ == '__main__':
    main()
