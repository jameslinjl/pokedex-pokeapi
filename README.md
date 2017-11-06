# pokedex-pokeapi-memcache

Playing around with flask, pokeapi, and memcached as a teaching tool for beginner web development.

Assumes that memcached is running on the same host on port 11211.

Make sure to install memcached for your machine.

Ensure you have a memcache client module installed:
```bash
pip install pylibmc
```

Run standard flask application:
```bash
pip install Flask # if you haven't installed before
FLASK_APP=app.py flask run
```
