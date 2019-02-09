from crtools.api import ClashRoyaleAPI, ClashRoyaleAPIMissingFieldsError
import json
import pytest
import requests_mock
import urllib.parse

import requests

MOCK_BASEURL = 'mock://test.com'
API_KEY = 'FakeApiKey'
CLAN_TAG = '#FakeClanTag'
CLAN_TAG_ESCAPED = urllib.parse.quote_plus(CLAN_TAG)

def test_missing_api_credentials():
    try:
        api = ClashRoyaleAPI('http://foo.bar', False, CLAN_TAG)
    except ClashRoyaleAPIMissingFieldsError as e:
        assert e.field_name == 'api_key'

    try:
        api = ClashRoyaleAPI('http://foo.bar', API_KEY, False)
    except ClashRoyaleAPIMissingFieldsError as e:
        assert e.field_name == 'clan_tag'

def test_api_get_clan_success(requests_mock):
    mock_object = {'foo':'bar'}
    mock_url = MOCK_BASEURL + ClashRoyaleAPI.CLAN_API_ENDPOINT.format(clan_tag=CLAN_TAG_ESCAPED)

    requests_mock.get(mock_url, json=mock_object, status_code=200)

    api = ClashRoyaleAPI(MOCK_BASEURL, API_KEY, CLAN_TAG)
    clan = api.get_clan()

    assert mock_object == clan

def test_api_get_warlog_success(requests_mock):
    mock_object = {'foo':'bar'}
    mock_url = MOCK_BASEURL + ClashRoyaleAPI.WARLOG_API_ENDPOINT.format(clan_tag=CLAN_TAG_ESCAPED)

    requests_mock.get(mock_url, json=mock_object, status_code=200)

    api = ClashRoyaleAPI(MOCK_BASEURL, API_KEY, CLAN_TAG)
    clan = api.get_warlog()

    assert mock_object == clan

def test_api_get_current_war_success(requests_mock):
    mock_object = {'foo':'bar'}
    mock_url = MOCK_BASEURL + ClashRoyaleAPI.CURRENT_WAR_API_ENDPOINT.format(clan_tag=CLAN_TAG_ESCAPED)

    requests_mock.get(mock_url, json=mock_object, status_code=200)

    api = ClashRoyaleAPI(MOCK_BASEURL, API_KEY, CLAN_TAG)
    clan = api.get_current_war()

    assert mock_object == clan
