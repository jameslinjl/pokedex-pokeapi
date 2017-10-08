import base64
from flask import Flask, render_template, request
import json
import memcache
import requests

app = Flask(__name__)
client = memcache.Client([('127.0.0.1', 11211)])

def memcached_external_api_get(url):
	b64_url = base64.b64encode(url)
	result = client.get(b64_url)
	if not result:
		result = requests.get(url).json()
		client.set(b64_url, result, time=0)
		print 'no cache'
	else:
		print 'cache hit'
	return result

@app.route('/')
def view_pokedex_main():
	api_response = memcached_external_api_get('https://pokeapi.co/api/v2/pokemon/')
	# text = '{"count":811,"next":"https://pokeapi.co/api/v2/pokemon/?offset=20","previous":null,"results":[{"name":"bulbasaur","url":"https://pokeapi.co/api/v2/pokemon/1/"},{"name":"ivysaur","url":"https://pokeapi.co/api/v2/pokemon/2/"},{"name":"venusaur","url":"https://pokeapi.co/api/v2/pokemon/3/"},{"name":"charmander","url":"https://pokeapi.co/api/v2/pokemon/4/"},{"name":"charmeleon","url":"https://pokeapi.co/api/v2/pokemon/5/"},{"name":"charizard","url":"https://pokeapi.co/api/v2/pokemon/6/"},{"name":"squirtle","url":"https://pokeapi.co/api/v2/pokemon/7/"},{"name":"wartortle","url":"https://pokeapi.co/api/v2/pokemon/8/"},{"name":"blastoise","url":"https://pokeapi.co/api/v2/pokemon/9/"},{"name":"caterpie","url":"https://pokeapi.co/api/v2/pokemon/10/"},{"name":"metapod","url":"https://pokeapi.co/api/v2/pokemon/11/"},{"name":"butterfree","url":"https://pokeapi.co/api/v2/pokemon/12/"},{"name":"weedle","url":"https://pokeapi.co/api/v2/pokemon/13/"},{"name":"kakuna","url":"https://pokeapi.co/api/v2/pokemon/14/"},{"name":"beedrill","url":"https://pokeapi.co/api/v2/pokemon/15/"},{"name":"pidgey","url":"https://pokeapi.co/api/v2/pokemon/16/"},{"name":"pidgeotto","url":"https://pokeapi.co/api/v2/pokemon/17/"},{"name":"pidgeot","url":"https://pokeapi.co/api/v2/pokemon/18/"},{"name":"rattata","url":"https://pokeapi.co/api/v2/pokemon/19/"},{"name":"raticate","url":"https://pokeapi.co/api/v2/pokemon/20/"}]}'
	# json_dict = json.loads(text)
	pokemon_results = api_response['results']
	return render_template('home.html', pokemon_results=pokemon_results)

@app.route('/pokemon/')
def view_pokedex_entry():
	name = request.args.get('name')

	data_dict = memcached_external_api_get('https://pokeapi.co/api/v2/pokemon-species/' + name)
	flavor_text = ''
	for data in data_dict['flavor_text_entries']:
		if data['version']['name'] == 'red' and data['language']['name'] == 'en':
			flavor_text = data['flavor_text']

	form_dict = memcached_external_api_get('https://pokeapi.co/api/v2/pokemon-form/' + name)
	return render_template('pokemon.html', pokemon_data=data_dict, sprite_url=form_dict['sprites']['front_default'], description=flavor_text)
