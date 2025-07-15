# Awesome iOS Game Ports

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

This [awesome list](https://github.com/sindresorhus/awesome#readme) is a compilation of PC/Console games ported to iOS. For more information, please head to the FAQ below.

Want a game to be shown here? Use the button below:

[![Request new game](https://img.shields.io/badge/Request%20game%20to%20be%20added-8A2BE2)](https://github.com/albertquiroga/awesome-ios-game-ports/issues/new?assignees=&labels=&projects=&template=new-game-request.md&title=)

## Games

Total games: **{{ total_games }}** across **{{ sorted_genres|length }}** genres

{% for genre in sorted_genres %}
### {{ genre }}

Name | App ID | Average Rating | Price (USD)
--- | --- | --- | ---
{% for app in apps_by_genre[genre] -%}
[{{ app.name }}]({{ app.url }}) | {{ app.id }} | {{ app.avg_score }} | {{ app.price }}
{% endfor %}

{% endfor %}

### Missing games

These games used to be in the App Store, but they have been removed at some point

Name | App ID
--- | ---
{% for app in missing_apps %}
[{{ app.name }}]({{ app.url }}) | {{ app.id }}
{% endfor %}

## FAQ

### Why this list?

Mobile gaming is unfortunately famous for abusing anti-consumer practices such as timegating, lootboxes, gacha mechanics and encouranging gambling amongst others. This list tries to provide a safe set of games by listing games that were originally designed for other gaming platforms (PC, consoles) where these mechanics are not as widely accepted. This list does not guarantee the quality of the listed games, only that they are also PC/Console games and thus they probably don't have predatory mechanics.

### Why not also add good games that are not ports?

That would require manual review of each game, something I don't have the time (and money) for.

### How to add a game to the list?

I followed the simple criteria below to create this list:

* The game must also be present in the PS Store, the Xbox store or any of the popular PC stores (Steam, GOG, Epic, etc)
* The game must obviously not have any of the aforementioned anti-consumer practices

If you find a game not listed here that you'd like to add, please reach out to me or make a pull request and I'll add it as soon as possible.

### How does this list work?

Using the power of GitHub actions, the list is updated every day to refresh average review scores and prices. A list of App Store application IDs is kept in the `ids.tsv` file, which is then converted into table entries of this repo's `README.md` file by the `main.py` script and some Jinja2 magic.

### How are games categorized?

Games are automatically categorized by genre using data from the iTunes Store API. Each app's genre list is retrieved from the API, and since the first genre is always "Games", we use the second genre in the list as the specific category for each game. This provides an automated way to organize the games without manual categorization.
