import logging
import re
import requests

from jinja2 import FileSystemLoader, Environment

logging.basicConfig(level=logging.INFO)

APP_IDS_FILE_PATH = 'ids.tsv'
SEPARATOR_CHAR = '\t'
VALIDATION_REGEX = "[0-9]+\t\".*\""

BASE_ITUNES_API_URL = 'https://itunes.apple.com/lookup?country=US&id='
NETFLIX_ID = '363590054'

TEMPLATE_FILE_NAME = 'README.md'
TEMPLATES_PATH = 'templates'
env = Environment(loader=FileSystemLoader(searchpath=TEMPLATES_PATH), trim_blocks=True)

OUTPUT_FILE_NAME = 'README.md'


class App:
    """
    App object representing an App Store applicaton
    """
    base_app_store_url = 'https://apps.apple.com/ie/app/awesome/id'

    def __init__(self, app_id: str, name: str = '', price: str = '', url: str = '', avg_score: float = '', developer: str = '', genre: str = 'Unknown'):
        self.id = app_id
        self.name = name
        self.price = 'Netflix' if developer == NETFLIX_ID else price
        self.url = url if url else self.base_app_store_url + app_id
        self.avg_score = avg_score
        self.developer = developer
        self.genre = genre

    def __str__(self):
        return f'{self.id} | {self.url} | {self.name} | {self.price} | {self.avg_score} | {self.genre}'

    def __repr__(self):
        return f'{self.id} | {self.url} | {self.name} | {self.price} | {self.avg_score} | {self.genre}'


def process_request(app_id: str, app_name: str, response: dict) -> App:
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
        return App(app_id=app_id, name=app_name)


def extract_genre_from_api(result: dict) -> str:
    """
    Extract genre from iTunes API response.
    The first genre is always "Games", so we skip it and look for the next meaningful genre.
    We also skip generic genres like "Board", "Family", and "Entertainment" to find more specific ones.
    :param result: iTunes API result dictionary
    :return: Genre string
    """
    genres = result.get('genres', [])
    
    # Genres to skip as they're too generic
    generic_genres = {'Games', 'Board', 'Family', 'Entertainment', 'Casual'}
    
    # Find the first genre that's not in our skip list
    for genre in genres:
        if genre not in generic_genres:
            return genre
    
    # If all genres are generic, return the last non-"Games" genre or fallback
    for genre in reversed(genres):
        if genre != 'Games':
            return genre
    
    return 'Unknown'


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
    developer = str(result.get('artistId'))
    avg_score = round(result.get('averageUserRatingForCurrentVersion'), 2)
    genre = extract_genre_from_api(result)
    
    return App(app_id=app_id, name=name, price=price, avg_score=avg_score, developer=developer, genre=genre)


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
    app_name = entry.split(SEPARATOR_CHAR)[1].strip('\"')
    full_url = BASE_ITUNES_API_URL + app_id
    response = get_api_response(full_url)
    return process_request(app_id, app_name, response)


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
        except:
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
        return sorted(apps, key= lambda app: app.name.lower())


def generate_readme(output_path: str, apps_list: list):
    """
    Given a list of Apps, generates a README.md file with their information using Jinja2 templating and
    writes the result to the given output path
    :param output_path: Path where the README.md file must be written to
    :param apps_list: List of App objects
    :return: None
    """
    found_apps = list(filter(lambda app: app.price, apps_list))
    missing_apps = list(filter(lambda app: not app.price, apps_list))
    
    # Group found apps by genre
    apps_by_genre = {}
    for app in found_apps:
        genre = app.genre
        if genre not in apps_by_genre:
            apps_by_genre[genre] = []
        apps_by_genre[genre].append(app)
    
    # Sort apps within each genre alphabetically
    for genre in apps_by_genre:
        apps_by_genre[genre].sort(key=lambda app: app.name.lower())
    
    # Get sorted list of genres for consistent ordering
    sorted_genres = sorted(apps_by_genre.keys())
    
    logging.info(f'Generating README.md file with results grouped by {len(sorted_genres)} genres...')
    base_template = env.get_template(TEMPLATE_FILE_NAME)
    with open(output_path, "w") as f:
        f.write(base_template.render(
            apps_by_genre=apps_by_genre,
            sorted_genres=sorted_genres,
            missing_apps=missing_apps,
            total_games=len(found_apps)
        ))


def main():
    """
    Main function. Parses the list of app ids into App objects, then generates the README file
    """
    apps = parse_app_ids(APP_IDS_FILE_PATH)
    generate_readme(OUTPUT_FILE_NAME, apps)


if __name__ == '__main__':
    main()
