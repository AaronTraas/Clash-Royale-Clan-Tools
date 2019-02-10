#!/usr/bin/python

"""Lightweight wrapper for the Clash Royale API V1 (https://api.clashroyale.com)."""

import logging
import requests
import urllib
import urllib.parse

class ClashRoyaleAPIError(Exception):
    """Catch-all for all generic errors involved with accessing the
    ClashRoyale API"""
    pass

class ClashRoyaleAPIMissingFieldsError(Exception):
    """One of the required fields is empty, thus we're bailing early,
    knowing we're going to fail. The reason for this error is that the
    two fields that the end user NEEDS to provide are clan tag and API
    key, so we can't rely on defaults. We want to give nice error
    messages in this state to aid in troubleshooting."""
    field_name = None

    def __init__(self, field_name):
        Exception.__init__(self, "'{}' not provided".format(field_name))
        self.field_name = field_name


class ClashRoyaleAPIAuthenticationError(Exception):
    """Failed to authenticate with the API. Key is likely bad."""
    pass

class ClashRoyaleAPIClanNotFound(Exception):
    """clan_id is likely incorrect or invalid."""
    def __init__(self, clan_tag):
        Exception.__init__(self, 'Clan with tag "{}" not found'.format(clan_tag))
        self.clan_tag = clan_tag

class ClashRoyaleAPI:

    CLAN_API_ENDPOINT = '/v1/clans/{clan_tag}'
    WARLOG_API_ENDPOINT = '/v1/clans/{clan_tag}/warlog'
    CURRENT_WAR_API_ENDPOINT = '/v1/clans/{clan_tag}/currentwar'

    baseurl = False
    api_key = False
    clan_tag = False

    def __init__(self, baseurl, api_key, clan_tag):
        self.logger = logging.getLogger('.'.join([__name__, self.__class__.__name__]))

        if api_key == False:
            raise ClashRoyaleAPIMissingFieldsError('api_key');

        if clan_tag == False:
            raise ClashRoyaleAPIMissingFieldsError('clan_tag');

        self.api_key = api_key
        self.clan_tag = clan_tag
        self.baseurl = baseurl

        self.headers = {
            'Accept': 'application/json',
            'authorization': 'Bearer ' + api_key
        }

    def __api_call(self, endpoint):
        # Make request and handle errors. If request returns a valid object,
        # return that object.
        r = requests.get(self.baseurl + endpoint, headers=self.headers)

        if r.status_code == 200:
            return r.json()
        elif r.status_code == 404:
            raise ClashRoyaleAPIClanNotFound(self.clan_tag)
        else:
            if(r.json()['reason'] == 'accessDenied'):
                raise ClashRoyaleAPIAuthenticationError(r.json()['message'])
            else:
                raise ClashRoyaleAPIError(r.content);

    def get_clan(self):
        """Grab clan data from API."""

        self.logger.debug('Retrieving clan data for "{}"'.format(self.clan_tag))
        endpoint = self.CLAN_API_ENDPOINT.format(clan_tag=urllib.parse.quote_plus(self.clan_tag))
        return self.__api_call(endpoint)

    def get_warlog(self):
        """Grab war log data from API."""

        self.logger.debug('Retrieving warlog for "{}"'.format(self.clan_tag))
        endpoint = self.WARLOG_API_ENDPOINT.format(clan_tag=urllib.parse.quote_plus(self.clan_tag))
        warlog_api = self.__api_call(endpoint)
        if warlog_api and ('items' in warlog_api):
            return warlog_api['items']
        else:
            return warlog_api

    def get_current_war(self):
        """Grab war log data from API."""

        self.logger.debug('Retrieving current war data for "{}"'.format(self.clan_tag))
        endpoint = self.CURRENT_WAR_API_ENDPOINT.format(clan_tag=urllib.parse.quote_plus(self.clan_tag))
        return self.__api_call(endpoint)
