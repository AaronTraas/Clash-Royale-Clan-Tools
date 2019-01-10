#!/usr/bin/python

"""Lightweight wrapper for the Clash Royale API V1 (https://api.clashroyale.com)."""

import requests
import urllib
import urllib.parse


class ClashRoyaleAPIError(Exception):
    """"""
    pass

class ClashRoyaleAPIAuthenticationError(Exception):
    """Failed to authenticate with the API. Key is likely bad."""
    pass

class ClashRoyaleAPIClanNotFound(Exception):
    """"""
    pass


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

        if r.status_code == 200:
            clan = r.json()
            return clan
        elif r.status_code == 404: 
            raise ClashRoyaleAPIClanNotFound('Clan with tag "{}" not found'.format(self.clan_tag))
        else: 
            if(r.json()['reason'] == 'accessDenied'):
            	raise ClashRoyaleAPIAuthenticationError(r.json()['message'])
            else:
            	raise ClashRoyaleAPIError(r.content);
            return False

    def get_warlog(self):
        """Grab war log data from API."""

        url = self.WARLOG_API_ENDPOINT.format(clan_tag=urllib.parse.quote_plus(self.clan_tag))
        r = requests.get(url, headers=self.headers)

        if r.status_code == 200:
            warlog = r.json()
            return warlog['items']
        elif r.status_code == 404: 
            raise ClashRoyaleAPIClanNotFound('Clan with tag "{}" not found'.format(self.clan_tag))
        else: 
            if(r.json()['reason'] == 'accessDenied'):
            	raise ClashRoyaleAPIAuthenticationError(r.json()['message'])
            else:
            	raise ClashRoyaleAPIError(r.content);
            return False
