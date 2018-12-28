#!/usr/bin/python
"""Tools for creating a clan maagement dashboard for Clash Royale."""

__license__   = 'LGPLv3'
__docformat__ = 'reStructuredText'

import codecs
from datetime import datetime
import dateutil.parser
from jinja2 import Environment, PackageLoader, select_autoescape
import json
import os
import requests
import shutil
import urllib
import urllib.parse

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
    url = 'https://api.clashroyale.com/v1/clans/' + urllib.parse.quote_plus(clan_id)
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
    url = 'https://api.clashroyale.com/v1/clans/' + urllib.parse.quote_plus(clan_id) + '/warlog?limit=8'
    headers = {
        'Accept': 'application/json',
        'authorization': 'Bearer ' + api_key
    }
    r = requests.get(url, headers=headers)
    warlog = json.loads(r.text)

    return warlog['items']

def warlog_dates(warlog):
    """ Return list of date strings from warlog. One entry per war. """

    war_dates = []
    for war in warlog:
        war_dates.append(dateutil.parser.parse(war['createdDate']).strftime("%m-%d"))
    return war_dates


def member_warlog(member_tag, warlog):
    """ Return war participation records for a given member by member tag. """

    member_warlog = []
    for war in warlog:
        participation = ''
        for member in war['participants']:
            if member['tag'] == member_tag:
                participation = {
                    'battlesPlayed': member['battlesPlayed'],
                    'wins': member['wins'],
                    'collectionDayBattlesPlayed': member['collectionDayBattlesPlayed']
                }
        member_warlog.append(participation)
    return member_warlog

def render_html_page(env, page_title, content, clan_name, clan_id):
    template = env.get_template('page.html.j2')
    return template.render(
            page_title = page_title,
            update_date = datetime.now().strftime('%c'),
            content = content,
            clan_name = clan_name,
            clan_id    = clan_id
        )

def render_dashboard(env, members, clan_name, clan_id, war_dates):
    """Render clan dashboard."""

    template_vars = {
        'members' : members, 
        'clan_name' : clan_name, 
        'war_dates' : war_dates
    }

    template = env.get_template('member-table.html.j2')
    return render_html_page( 
            env, 
            page_title = "Dashboard for " + clan_name,
            content    = template.render(template_vars),
            clan_name  = clan_name,
            clan_id    = clan_id
        )

def build_dashboard(api_key, clan_id, output_path):
    """Compile and render clan dashboard."""

    # remove output directory if previeously created to cleanup. Then 
    # create output path and log path.
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    log_path = os.path.join(output_path, 'log')
    os.makedirs(output_path)
    os.makedirs(log_path)

    # copy static assets to output path
    shutil.copytree(os.path.join(os.path.dirname(__file__), 'static'), os.path.join(output_path, 'static'))

    # Get clan data from API. Write to log.
    clan = get_clan(api_key, clan_id)
    write_object_to_file(os.path.join(log_path, 'clan.json'), json.dumps(clan, indent=4))

    # Get war log data from API. Write to log.
    warlog = get_warlog(api_key, clan_id)
    write_object_to_file(os.path.join(log_path, 'warlog.json'), json.dumps(warlog, indent=4))

    # grab importent fields from member list for dashboard
    member_dash = []
    for member in clan['memberList']:
        #member_row = [member['clanRank'], member['name'], member['donations'], member['donationsReceived']] + member_warlog(member['tag'], warlog)
        member_row = member
        member_row['warlog'] = member_warlog(member['tag'], warlog)
        member_dash.append(member_row)

    env = Environment(
        loader=PackageLoader('crtools', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    dashboard_html = render_dashboard(env, member_dash, clan['name'], clan['tag'], warlog_dates(warlog))
    write_object_to_file(os.path.join(output_path, 'index.html'), dashboard_html)
 
