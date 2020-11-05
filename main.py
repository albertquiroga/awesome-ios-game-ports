import requests
import logging

from jinja2 import FileSystemLoader, Environment

logging.basicConfig(level=logging.INFO)

APP_IDS_FILE_PATH = 'ids.txt'

BASE_ITUNES_API_URL = 'https://itunes.apple.com/lookup?country=US&id='

TEMPLATE_FILE_NAME = 'README.md'
TEMPLATES_PATH = 'templates'
env = Environment(loader=FileSystemLoader(searchpath=TEMPLATES_PATH), trim_blocks=True)

OUTPUT_FILE_NAME = 'README.md'


class App:
    """
    App object representing an App Store applicaton
    """
    base_app_store_url = 'https://apps.apple.com/ie/app/thronebreaker/id'

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
    if response['resultCount'] > 0:
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
    result = response['results'][0]
    price = result['price']
    name = result.get('trackName')
    avg_score = round(result.get('averageUserRatingForCurrentVersion'), 2)
    return App(app_id=app_id, name=name, price=price, avg_score=avg_score)


def process_app_id(app_id: str) -> App:
    """
    Given an app ID, turns that into an App object
    :param app_id: App ID in string format
    :return: App object representing the application
    """
    app_id = app_id.strip()
    full_url = BASE_ITUNES_API_URL + app_id
    response = requests.get(full_url).json()
    return process_request(app_id, response)


def parse_app_ids(file_path: str) -> list:
    """
    Given a list of app IDs, turns that into App objects
    :param file_path: Path to the file containing the list of app IDs
    :return: List of App objects representing those apps
    """
    logging.info(f'Parsing app IDs from {file_path}...')
    with open(file_path) as fp:
        results = list(map(lambda app_id: process_app_id(app_id), fp))
        return results


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
