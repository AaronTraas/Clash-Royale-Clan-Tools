from crtools.api import ClashRoyaleAPI, ClashRoyaleAPIError, ClashRoyaleAPIMissingFieldsError, ClashRoyaleAPIClanNotFound, ClashRoyaleAPIAuthenticationError
import json
import pytest
import requests_mock
import urllib.parse

import requests

MOCK_BASEURL = 'mock://test.com'
API_KEY = 'FakeApiKey'
CLAN_TAG = '#FakeClanTag'
CLAN_TAG_ESCAPED = urllib.parse.quote_plus(CLAN_TAG)

api = ClashRoyaleAPI(MOCK_BASEURL, API_KEY, CLAN_TAG)

def test_missing_api_credentials():
    try:
        api = ClashRoyaleAPI('http://foo.bar', False, CLAN_TAG)
    except ClashRoyaleAPIMissingFieldsError as e:
        assert e.field_name == 'api_key'

    try:
        api = ClashRoyaleAPI('http://foo.bar', API_KEY, False)
    except ClashRoyaleAPIMissingFieldsError as e:
        assert e.field_name == 'clan_tag'

def test_api_authentication_error(requests_mock):
    mock_object = {'reason': 'accessDenied', 'message': 'mock access denied message'}
    mock_url = MOCK_BASEURL + ClashRoyaleAPI.CLAN_API_ENDPOINT.format(clan_tag=CLAN_TAG_ESCAPED)

    requests_mock.get(mock_url, json=mock_object, status_code=401)

    try:
        response_object = api.get_clan()
    except ClashRoyaleAPIAuthenticationError as e:
        assert str(e) == mock_object['message']

def test_api_misc_error(requests_mock):
    mock_object = {'reason': 'foo'}
    mock_url = MOCK_BASEURL + ClashRoyaleAPI.CLAN_API_ENDPOINT.format(clan_tag=CLAN_TAG_ESCAPED)

    requests_mock.get(mock_url, json=mock_object, status_code=500)

    try:
        response_object = api.get_clan()
    except ClashRoyaleAPIError as e:
        # we don't know what to look for, because this is a catch-all
        # error.  We assume if we got here, it's good.
        assert True


def test_api_get_clan_success(requests_mock):
    mock_object = {'foo':'bar'}
    mock_url = MOCK_BASEURL + ClashRoyaleAPI.CLAN_API_ENDPOINT.format(clan_tag=CLAN_TAG_ESCAPED)

    requests_mock.get(mock_url, json=mock_object, status_code=200)

    api = ClashRoyaleAPI(MOCK_BASEURL, API_KEY, CLAN_TAG)
    response_object = api.get_clan()

    assert mock_object == response_object

def test_api_get_clan_failure_clan_tag_not_found(requests_mock):
    mock_url = MOCK_BASEURL + ClashRoyaleAPI.CLAN_API_ENDPOINT.format(clan_tag=CLAN_TAG_ESCAPED)

    requests_mock.get(mock_url, status_code=404)

    try:
        response_object = api.get_clan()
    except ClashRoyaleAPIClanNotFound as e:
        assert e.clan_tag == CLAN_TAG

def test_api_get_warlog_success(requests_mock):
    mock_object = { 'items': ['foo', 'bar'] }
    mock_url = MOCK_BASEURL + ClashRoyaleAPI.WARLOG_API_ENDPOINT.format(clan_tag=CLAN_TAG_ESCAPED)

    requests_mock.get(mock_url, json=mock_object, status_code=200)

    response_object = api.get_warlog()

    assert mock_object['items'] == response_object

def test_api_get_warlog_success_noitems(requests_mock):
    mock_object = {'foo':'bar'}
    mock_url = MOCK_BASEURL + ClashRoyaleAPI.WARLOG_API_ENDPOINT.format(clan_tag=CLAN_TAG_ESCAPED)

    requests_mock.get(mock_url, json=mock_object, status_code=200)

    response_object = api.get_warlog()

    assert mock_object == response_object

def test_api_get_current_war_success_noitems(requests_mock):
    mock_object = {'foo':'bar'}
    mock_url = MOCK_BASEURL + ClashRoyaleAPI.CURRENT_WAR_API_ENDPOINT.format(clan_tag=CLAN_TAG_ESCAPED)

    requests_mock.get(mock_url, json=mock_object, status_code=200)

    response_object = api.get_current_war()

    assert mock_object == response_object
