import json
import requests
import urllib
import urllib.parse

class ClashRoyaleAPI:

	CLAN_API_ENDPOINT = 'https://api.clashroyale.com/v1/clans/{clan_tag}'
	WARLOG_API_ENDPOINT = 'https://api.clashroyale.com/v1/clans/{clan_tag}/warlog'

	def __init__(self, api_key, clan_tag):
		self.api_key = api_key
		self.clan_tag = clan_tag

		self.headers = {
	        'Accept': 'application/json',
	        'authorization': 'Bearer ' + api_key
	    }

	def get_clan(self):
	    """Grab clan data from API."""

	    url = self.CLAN_API_ENDPOINT.format(clan_tag=urllib.parse.quote_plus(self.clan_tag))
	    r = requests.get(url, headers=self.headers)
	    clan = json.loads(r.text)

	    return clan

	def get_warlog(self):
	    """Grab war log data from API."""

	    url = self.WARLOG_API_ENDPOINT.format(clan_tag=urllib.parse.quote_plus(self.clan_tag))
	    r = requests.get(url, headers=self.headers)
	    warlog = json.loads(r.text)

	    return warlog['items']
