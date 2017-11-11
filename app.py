import base64
from flask import Flask, render_template, request
import json
import memcache
import os
import requests
from urlparse import urlparse, parse_qs

app = Flask(__name__)

# memcache setup
memcached_host = os.environ.get('MEMCACHE_PORT_11211_TCP_ADDR')
if memcached_host is None:
	memcached_host = '127.0.0.1'
memcached_port = os.environ.get('MEMCACHE_PORT_11211_TCP_PORT')
if memcached_port is None:
	memcached_port = 11211
client = memcache.Client([(memcached_host, int(memcached_port))])

result_limits = [{'value': 20, 'selected': True}, {'value': 100, 'selected': False}, {'value': 250, 'selected': False}]

def memcached_external_api_get(url):
	b64_url = base64.b64encode(url)
	result = client.get(b64_url)
	if not result:
		result = requests.get(url).json()
		client.set(b64_url, result, time=0)
	return result

@app.route('/')
def view_pokedex_main():
	limit = request.args.get('limit')
	offset = request.args.get('offset')

	url = 'https://pokeapi.co/api/v2/pokemon/'
	if limit is not None and offset is not None:
		url = url + '?limit=' + limit + '&offset=' + offset
		for result_limit in result_limits:
			if int(limit) != result_limit['value']:
				result_limit['selected'] = False
			else:
				result_limit['selected'] = True

	api_response = memcached_external_api_get(url)
	prev_qs = {}
	next_qs = {}
	if api_response['previous']:
		prev_qs = parse_qs(urlparse(api_response['previous']).query)
	if api_response['next']:
		next_qs = parse_qs(urlparse(api_response['next']).query)

	return render_template(
		'home.html',
		pokemon_results=api_response['results'],
		next_limit_value=next_qs['limit'][0] if 'limit' in next_qs else None,
		next_offset_value=next_qs['offset'][0] if 'offset' in next_qs else 0,
		prev_limit_value=prev_qs['limit'][0] if 'limit' in prev_qs else None,
		prev_offset_value=prev_qs['offset'][0] if 'offset' in prev_qs else 0,
		ol_start=1 if offset is None else int(offset) + 1,
		select_options=result_limits
	)

@app.route('/pokemon/')
def view_pokedex_entry():
	name = request.args.get('name')

	data_dict = memcached_external_api_get('https://pokeapi.co/api/v2/pokemon-species/' + name)
	flavor_text = ''
	for data in data_dict['flavor_text_entries']:
		if data['language']['name'] == 'en':
			# replace is to make sure form feed character is replaced
			flavor_text = data['flavor_text'].replace('\x0C', ' ')
			# eh, just find the first english one
			break

	form_dict = memcached_external_api_get('https://pokeapi.co/api/v2/pokemon-form/' + name)
	return render_template('pokemon.html', pokemon_data=data_dict, sprite_url=form_dict['sprites']['front_default'], description=flavor_text)

if __name__ == "__main__":
	app.run(host="0.0.0.0")
