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
import shutil
import urllib

def write_object_to_file(file_path, obj): 
    """ Writes contents of object to file. If object is a string, write it 
    directly. Otherwise, convert it to JSON first """

    # open file for UTF-8 output, and write contents of object to file
    with codecs.open(file_path, 'w', 'utf-8') as f:
        if isinstance(obj, str) or isinstance(obj, unicode):
            string = obj
        else:
            string = json.dumps(obj, indent=4)
        f.write(string)


def get_clan(api_key, clan_id):
    """Grab clan data from API."""

    # curl -X GET --header 'Accept: application/json' --header "authorization: Bearer <API token>" 'https://api.clashroyale.com/v1/clans/%23JY8YVV'
    url = 'https://api.clashroyale.com/v1/clans/' + urllib.quote_plus(clan_id)
    headers = {
        'Accept': 'application/json',
        'authorization': 'Bearer ' + api_key
    }
    r = requests.get(url, headers=headers)
    clan = json.loads(r.text)


    return clan

def get_warlog(api_key, clan_id):
    """Grab war log data from API."""

    # curl -X GET --header 'Accept: application/json' --header "authorization: Bearer <API token>" 'https://api.clashroyale.com/v1/clans/%23JY8YVV/warlog'
    url = 'https://api.clashroyale.com/v1/clans/' + urllib.quote_plus(clan_id) + '/warlog'
    headers = {
        'Accept': 'application/json',
        'authorization': 'Bearer ' + api_key
    }
    r = requests.get(url, headers=headers)
    warlog = json.loads(r.text)

    return warlog['items']

def render_dashboard(members, clan_name):
    """Render clan dashboard."""
    env = Environment(
        loader=PackageLoader('crtools', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template_vars = {
        'members' : members, 
        'clan_name' : clan_name, 
        'member_headers' : ['Rank', 'Name', 'Donations', 'Donations Recieved']
    }

    template = env.get_template('dashboard.html.j2')
    return template.render(template_vars)

def build_dashboard(api_key, clan_id, output_path):
    """Compile and render clan dashboard."""

    # remove output directory if previeously created to cleanup. Then 
    # create output path and log path.
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    log_path = os.path.join(output_path, 'log')
    os.makedirs(output_path)
    os.makedirs(log_path)

    # Get clan data from API. Write to log.
    clan = get_clan(api_key, clan_id)
    write_object_to_file(os.path.join(log_path, 'clan.json'), json.dumps(clan, indent=4))

    # Get war log data from API. Write to log.
    warlog = get_warlog(api_key, clan_id)
    write_object_to_file(os.path.join(log_path, 'warlog.json'), json.dumps(warlog, indent=4))

    # grab importent fields from member list for dashboard
    member_dash = []
    for member in clan['memberList']:
        member_dash.append([member['clanRank'], member['name'], member['donations'], member['donationsReceived']])

    dashboard_html = render_dashboard(member_dash, clan['name'])
    write_object_to_file(os.path.join(output_path, 'index.html'), dashboard_html)
 


