#!/usr/bin/python
"""Tools for creating a clan maagement dashboard for Clash Royale."""

__license__   = 'LGPLv3'
__docformat__ = 'reStructuredText'

import codecs
from datetime import datetime, date, timezone
import json
import os
import requests
import shutil
import tempfile
import urllib
import urllib.parse
from ._version import __version__

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
    url = 'https://api.clashroyale.com/v1/clans/' + urllib.parse.quote_plus(clan_id) + '/warlog?limit=20'
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
        war_dates.append(datetime.strptime(war['createdDate'].split('.')[0], '%Y%m%dT%H%M%S').strftime("%m-%d"))
    return war_dates


def member_warlog(member_tag, warlog):
    """ Return war participation records for a given member by member tag. """

    member_warlog = []
    for war in warlog:
        participation = {'status': 'na'}
        for member in war['participants']:
            if member['tag'] == member_tag:
                if member['collectionDayBattlesPlayed'] == 0:
                    member['status'] = 'na'
                elif member['battlesPlayed'] == 0:
                    member['status'] = 'bad'
                elif member['collectionDayBattlesPlayed'] < 3:
                    member['status'] = 'ok'
                else:
                    member['status'] = 'good'
                participation = member
        member_warlog.append(participation)
    return member_warlog

def member_rating(member, member_warlog, days_from_donation_reset):
    good = ok = bad = na = 0
    for war in member_warlog:
        if war != None:
            if war['status'] == 'good':
                good += 1
            elif war['status'] == 'ok':
                ok += 1
            elif war['status'] == 'bad':
                bad += 1
            else:
                na += 1

    # then calculate score based on based on 20/day. We exempt them the first day
    donation_score = 0;
    if days_from_donation_reset > 1:
        target_donations = 12 * (days_from_donation_reset - 1)
        donation_score = member['donations'] - target_donations

        # bigger penalty for 0 donations
        if member['donations'] == 0:
            donation_score -= (days_from_donation_reset - 1) * 10;

    return (good * 20) + (ok) + (bad * -30) + (na * -1) + donation_score

def render_dashboard(clan, warlog, config, clan_description):
    """Render clan dashboard."""

    template = config['env'].get_template('clan-stats-table.html.j2')
    stats_html = template.render( clan )

    # calculate the number of days since the donation last sunday, for donation tracking purposes:
    today = date.today().toordinal()
    sunday = today - (today % 7)
    days_from_donation_reset = today - sunday

    # grab importent fields from member list for dashboard
    member_dash = []
    for member in clan['memberList']:
        member_row = member

        member['donation_status'] = 'normal'
        if member['donations'] > (days_from_donation_reset) * 40:
            member['donation_status'] = 'good'
        if days_from_donation_reset > 1:
            if member['donations'] == 0:
                member['donation_status'] = 'bad'
            elif member['donations'] < (days_from_donation_reset-1) * 10:
                member['donation_status'] = 'ok'

        member_row['warlog'] = member_warlog(member['tag'], warlog)
        
        member_row['rating'] = member_rating(member, member_row['warlog'], days_from_donation_reset)
        if member_row['rating'] > 0:
            member_row['danger'] = False
        else:
            member_row['danger'] = True

        if member['role'] == 'leader' or member['role'] == 'coLeader':
            member_row['leadership'] = True
        else: 
            member_row['leadership'] = False
        if member['role'] == 'coLeader':
            member['role'] = 'co-leader'
        member_dash.append(member_row)

    member_table = config['env'].get_template('member-table.html.j2').render(
        members      = member_dash, 
        clan_name    = clan['name'], 
        min_trophies = clan['requiredTrophies'], 
        war_dates    = warlog_dates(warlog)
    )

    members_by_score = newlist = sorted(member_dash, key=lambda k: k['rating']) 

    suggestions = [];
    for index, member in enumerate(members_by_score):
        if member['rating'] < 0:
            if index < len(members_by_score) - 46:
                suggestions.append('Kick <strong>{}</strong> (score: {})'.format(member['name'], member['rating']))
            elif member['role'] != 'member':
                suggestions.append('Demote <strong>{}</strong> (score: {})'.format(member['name'], member['rating']))

    return config['env'].get_template('page.html.j2').render(
            version          = __version__,
            update_date      = datetime.now().strftime('%c'),
            canonical_url    = config['canonical_url'],
            member_table     = member_table,
            clan_name        = clan['name'],
            clan_id          = clan['tag'],
            clan_description = clan_description,
            suggestions      = suggestions,
            clan_stats       = stats_html
        )

def build_dashboard(config):
    """Compile and render clan dashboard."""

    # Putting everything in a `try`...`finally` to ensure `tempdir` is removed
    # when we're done. We don't want to pollute the user's disk.
    try:
        # Create temporary directory. All file writes, until the very end,
        # will happen in this directory, so that no matter what we do, it
        # won't hose existing stuff.
        tempdir = tempfile.mkdtemp(config['temp_dir_name'])
        
        log_path = os.path.join(tempdir, 'log')
        os.makedirs(log_path)

        # copy static assets to output path
        shutil.copytree(os.path.join(os.path.dirname(__file__), 'static'), os.path.join(tempdir, 'static'))

        # If logo_path is provided, grab logo from path given, and put it where 
        # it needs to go. Otherwise, grab the default from the static folder
        logo_dest_path = os.path.join(tempdir, 'clan_logo.png')
        if config['logo_path']:
            logo_src_path = os.path.expanduser(config['logo_path'])
            shutil.copyfile(logo_src_path, logo_dest_path)
        else:
            shutil.copyfile(os.path.join(os.path.dirname(__file__), 'static/crtools-logo.png'), logo_dest_path)        

        # If favicon_path is provided, grab favicon from path given, and put it  
        # where it needs to go. Otherwise, grab the default from the static folder
        favicon_dest_path = os.path.join(tempdir, 'favicon.ico')
        if config['favicon_path']:
            favicon_src_path = os.path.expanduser(config['favicon_path'])
            shutil.copyfile(favicon_src_path, favicon_dest_path)
        else:
            shutil.copyfile(os.path.join(os.path.dirname(__file__), 'static/crtools-favicon.ico'), favicon_dest_path)        

        # Get clan data from API. Write to log.
        clan = get_clan(config['api_key'], config['clan_id'])
        write_object_to_file(os.path.join(log_path, 'clan.json'), json.dumps(clan, indent=4))

        clan_description = clan['description']
        if config['description_path']:
            description_path = os.path.expanduser(config['description_path'])
            if os.path.isfile(description_path):
                with open(description_path, 'r') as myfile:
                    clan_description = myfile.read()
            else:
                clan_description = "ERROR: File '{}' does not exist.".format(description_path)

        # Get war log data from API. Write to log.
        warlog = get_warlog(config['api_key'], config['clan_id'])
        write_object_to_file(os.path.join(log_path, 'warlog.json'), json.dumps(warlog, indent=4))

        dashboard_html = render_dashboard(clan, warlog, config, clan_description)
        write_object_to_file(os.path.join(tempdir, 'index.html'), dashboard_html)
        
        if config['canonical_url'] != False:
            lastmod = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
            sitemap_xml = config['env'].get_template('sitemap.xml.j2').render(
                    url     = config['canonical_url'],
                    lastmod = lastmod
                )
            robots_txt = config['env'].get_template('robots.txt.j2').render(
                    canonical_url = config['canonical_url']
                )
            write_object_to_file(os.path.join(tempdir, 'sitemap.xml'), sitemap_xml)
            write_object_to_file(os.path.join(tempdir, 'robots.txt'), robots_txt)

        # remove output directory if previeously created to cleanup. Then 
        # create output path and log path.
        output_path = os.path.expanduser(config['output_path'])
        if os.path.exists(output_path):
            shutil.copystat(output_path, tempdir)
            shutil.rmtree(output_path)

        # Copy entire contents of temp directory to output directory
        shutil.copytree(tempdir, output_path)
    finally:
        # Ensure that temporary directory gets deleted no matter what
        shutil.rmtree(tempdir)

