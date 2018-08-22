#!/usr/bin/python
"""Tools for creating a clan maagement dashboard for Clash Royale."""

__license__   = 'LGPLv3'
__docformat__ = 'reStructuredText'

import json
import pprint
import requests
import urllib


def get_clan(api_key, clan_id):
    # curl -X GET --header 'Accept: application/json' --header "authorization: Bearer <API token>" 'https://api.clashroyale.com/v1/clans/%23JY8YVV'
    url = 'https://api.clashroyale.com/v1/clans/' + urllib.quote_plus(clan_id)
    headers = {
        'Accept': 'application/json',
        'authorization': 'Bearer ' + api_key
    }
    r = requests.get(url, headers=headers)
    clan = json.loads(r.text)

    return clan

def make_request(api_key, clan_id):

    clan = get_clan(api_key, clan_id)

    members = clan['memberList']
    #pprint.pprint(members)

    print '<table>'
    print '<tr><th>Name</th><th>Donations</th><th>Donations</th></tr>'
    for member in members:
        print '<tr><td>%s</td><td>%s</td></tr>' % (member['name'],member['donations'])
    print '</table>'
