#!/usr/bin/python

"""Lightweight wrapper for the Clash Royale API V1 (https://api.clashroyale.com)."""

import logging
import requests
import urllib
import urllib.parse

class ClashRoyaleAPIError(Exception):
    """"""
    pass

class ClashRoyaleAPIMissingFieldsError(Exception):
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
    CURRENT_WAR_API_ENDPOINT = 'https://api.clashroyale.com/v1/clans/{clan_tag}/currentwar'

    api_key = False
    clan_tag = False

    def __init__(self, api_key, clan_tag):
        if api_key == False:
            raise ClashRoyaleAPIMissingFieldsError('API key not provided.');

        if clan_tag == False:
            raise ClashRoyaleAPIMissingFieldsError('Clan tag not provided.');

        self.api_key = api_key
        self.clan_tag = clan_tag

        self.headers = {
            'Accept': 'application/json',
            'authorization': 'Bearer ' + api_key
        }

    def __api_call(self, endpoint):
        # Make request and handle errors. If request returns a valid object,
        # return that object.
        r = requests.get(endpoint, headers=self.headers)

        if r.status_code == 200:
            return r.json()
        elif r.status_code == 404:
            raise ClashRoyaleAPIClanNotFound('Clan with tag "{}" not found'.format(self.clan_tag))
        else:
            if(r.json()['reason'] == 'accessDenied'):
                raise ClashRoyaleAPIAuthenticationError(r.json()['message'])
            else:
                raise ClashRoyaleAPIError(r.content);
            return False

    def get_clan(self):
        """Grab clan data from API."""

        logging.debug('Retrieving clan data for "{}"'.format(self.clan_tag))
        endpoint = self.CLAN_API_ENDPOINT.format(clan_tag=urllib.parse.quote_plus(self.clan_tag))
        return self.__api_call(endpoint)

    def get_warlog(self):
        """Grab war log data from API."""

        logging.debug('Retrieving warlog for "{}"'.format(self.clan_tag))
        endpoint = self.WARLOG_API_ENDPOINT.format(clan_tag=urllib.parse.quote_plus(self.clan_tag))
        warlog_api = self.__api_call(endpoint)
        if warlog_api and ('items' in warlog_api):
            return warlog_api['items']
        else:
            return warlog_api

    def get_current_war(self):
        """Grab war log data from API."""

        logging.debug('Retrieving current war data for "{}"'.format(self.clan_tag))
        endpoint = self.CURRENT_WAR_API_ENDPOINT.format(clan_tag=urllib.parse.quote_plus(self.clan_tag))
        return self.__api_call(endpoint)
