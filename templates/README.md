# Awesome iOS Game Ports

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

This [awesome list](https://github.com/sindresorhus/awesome#readme) is a compilation of PC/Console games ported to iOS

## Games

Name | App ID | Average Rating | Price (USD)
--- | --- | --- | ---
{% for app in apps_list %}
[{{ app.name }}]({{ app.url }}) | {{ app.id }} | {{app.avg_score}} | {{ app.price }}$ 
{% endfor %}
