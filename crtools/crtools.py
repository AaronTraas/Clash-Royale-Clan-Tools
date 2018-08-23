#!/usr/bin/python
"""Tools for creating a clan maagement dashboard for Clash Royale."""

__license__   = 'LGPLv3'
__docformat__ = 'reStructuredText'

import codecs
from jinja2 import Environment, PackageLoader, select_autoescape
import json
import os
import pprint
import requests
import urllib


def get_clan(api_key, clan_id, output_path):
    """Grab clan data from API."""

    # curl -X GET --header 'Accept: application/json' --header "authorization: Bearer <API token>" 'https://api.clashroyale.com/v1/clans/%23JY8YVV'
    url = 'https://api.clashroyale.com/v1/clans/' + urllib.quote_plus(clan_id)
    headers = {
        'Accept': 'application/json',
        'authorization': 'Bearer ' + api_key
    }
    r = requests.get(url, headers=headers)
    clan = json.loads(r.text)

    log_filename = os.path.join(output_path, 'clan.json')
    with codecs.open(log_filename, 'w', 'utf-8') as f:
        f.write(json.dumps(clan, indent=4, sort_keys=True))

    return clan

def get_warlog(api_key, clan_id, output_path):
    """Grab war log data from API."""

    # curl -X GET --header 'Accept: application/json' --header "authorization: Bearer <API token>" 'https://api.clashroyale.com/v1/clans/%23JY8YVV/warlog'
    url = 'https://api.clashroyale.com/v1/clans/' + urllib.quote_plus(clan_id) + '/warlog'
    headers = {
        'Accept': 'application/json',
        'authorization': 'Bearer ' + api_key
    }
    r = requests.get(url, headers=headers)
    warlog = json.loads(r.text)

    log_filename = os.path.join(output_path, 'warlog.json')
    with codecs.open(log_filename, 'w', 'utf-8') as f:
        f.write(json.dumps(warlog, indent=4, sort_keys=True))

    return warlog['items']


def build_dashboard(api_key, clan_id, output_path):
    """Render clan dashboard."""

    log_path = os.path.join(output_path, 'log')
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        os.makedirs(log_path)

    clan = get_clan(api_key, clan_id, log_path)
    warlog = get_warlog(api_key, clan_id, log_path)

    members = clan['memberList']
    clan_name = clan['name']
    #pprint.pprint(clan['name']); return
    #pprint.pprint(warlog)

    member_headers = ['Rank', 'Name', 'Donations', 'Donations Recieved']
    member_dash = []
    for member in members:
        member_dash.append([member["clanRank"], member["name"], member["donations"], member["donationsReceived"]])


    env = Environment(
        loader=PackageLoader('crtools', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('dashboard.html.j2')
    dashboard_html = template.render(members = member_dash, clan_name = clan_name, member_headers=member_headers)

    dashboard_filename = os.path.join(output_path, 'index.html')
    with codecs.open(dashboard_filename, 'w', 'utf-8') as f:
        f.write(dashboard_html)
 

