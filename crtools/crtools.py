#!/usr/bin/python
"""Tools for creating a clan maagement dashboard for Clash Royale."""

__license__   = 'LGPLv3'
__docformat__ = 'reStructuredText'

import codecs
from datetime import datetime, date, timezone
from jinja2 import Environment, PackageLoader, select_autoescape
import json
import math
import os
import shutil
import tempfile
from ._version import __version__

ARENA_LEAGUE_LOOKUP = {
    'League 1' : { 'id':  'arena-league-challenger-1' },
    'League 2' : { 'id':  'arena-league-challenger-2' },
    'League 3' : { 'id':  'arena-league-challenger-3' },
    'League 4' : { 'id':  'arena-league-master-1' },
    'League 5' : { 'id':  'arena-league-master-1' },
    'League 6' : { 'id':  'arena-league-master-1' },
    'League 7' : { 'id':  'arena-league-champion' },
    'League 8' : { 'id':  'arena-league-grand-champion' },
    'League 9' : { 'id':  'arena-league-ultimate-champion' }
}

WAR_LEAGUE_LOOKUP = {
    0    : { 'id': 'war-league-bronze',    'name': 'Bronze League',    'loss':  80, 'win': 160 },
    600  : { 'id': 'war-league-silver',    'name': 'Silver League',    'loss': 160, 'win': 320 },
    1500 : { 'id': 'war-league-gold',      'name': 'Gold League',      'loss': 280, 'win': 560 },
    3000 : { 'id': 'war-league-legendary', 'name': 'Legendary League', 'loss': 440, 'win': 880 }
}

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

def warlog_dates(warlog):
    """ Return list of date strings from warlog. One entry per war. """

    war_dates = []
    for war in warlog:
        war_dates.append(datetime.strptime(war['createdDate'].split('.')[0], '%Y%m%dT%H%M%S').strftime("%m-%d"))
    return war_dates


def member_warlog(member_tag, warlog, cardsPerCollectionBattleWin):
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
                participation['collectionBattleWins'] = math.floor(member['cardsEarned'] / cardsPerCollectionBattleWin)
                participation['collectionBattleLosses'] = participation['collectionDayBattlesPlayed'] - participation['collectionBattleWins']
        member_warlog.append(participation)

    return member_warlog

def member_score(member, member_warlog, days_from_donation_reset, config):
    """ Calculates a member's score based on war participation and donations. """

    # calculate score based `days_from_donation_reset`.
    donation_score = 0;
    target_donations = config['score']['min_donations_daily'] * (days_from_donation_reset)
    donation_score = member['donations'] - target_donations

    # exempt additional penalties if at least a day hasn't passed
    if days_from_donation_reset >= 1:
        donation_score = round(donation_score / days_from_donation_reset)

        # bigger penalty for 0 donations
        if member['donations'] == 0:
            donation_score += config['score']['donations_zero'];

    # calculate score based on war participation
    war_score = 0;
    for war in member_warlog:
        if war != None:
            #import pprint; pprint.pprint(war)

            if 'battlesPlayed' in war:
                if war['battlesPlayed'] >= 1:
                    war_score += war['battlesPlayed'] * config['score']['war_battle_played']
                    war_score += war['wins'] * config['score']['war_battle_won']
                    war_score += (war['battlesPlayed'] - war['wins']) * config['score']['war_battle_lost']
                else:
                    war_score += config['score']['war_battle_incomplete']

                war_score += war['collectionBattleWins'] * config['score']['collect_battle_won']
                war_score += war['collectionBattleLosses'] * config['score']['collect_battle_lost']

            else: 
                war_score += config['score']['war_non_participation']

    total_score = war_score + donation_score
    if (member['role'] == 'leader') and (total_score < 0):
        total_score = 0

    return total_score

def get_suggestions(members, config):
    """ Returns list of suggestions for the clan leadership to perform. 
    Suggestions are to kick, demote, or promote. Suggestions are based on 
    user score, and various thresholds in configuration. """

    members_by_score = sorted(members, key=lambda k: (k['score'], k['trophies']))

    suggestions = []
    for index, member in enumerate(members_by_score):
        if member['score'] < 0:
            if index < len(members_by_score) - config['score']['min_clan_size']:
                suggestions.append('Kick <strong>{}</strong> <strong class="bad">{}</strong>'.format(member['name'], member['score']))
            elif member['role'] != 'member':
                if member['role'] == 'elder':
                    demote_target = 'Member'
                else:
                    demote_target = 'Elder'
                suggestions.append('Demote <strong>{}</strong> <strong class="bad">{}</strong>'.format(member['name'], member['score']))
        elif (member['score'] >= config['score']['threshold_promote']) and (member['role'] == 'member'):
            suggestions.append('Consider premoting <strong>{}</strong> to <strong>Elder</strong> <strong class="good">{}</strong>'.format(member['name'], member['score']))

    if len(suggestions) == 0:
        suggestions.append('No suggestions at this time. The clan is in good order.')

    return suggestions

def get_score_rule_status( score ):
    if score > 0:
        return 'good'
    elif score < 0:
        return 'bad'
    else:
        return 'normal'

def get_scoring_rules(config):
    rules = [
        {'name': '...participate in the war?', 'yes': config['score']['war_participation'], 'no': config['score']['war_non_participation'] },
        {'name': '...complete each collection battle? (per battle)', 'yes': config['score']['collect_battle_played'], 'no': config['score']['collect_battle_incomplete']},
        {'name': '...win each collection battle? (per battle)', 'yes': config['score']['collect_battle_won'], 'no': config['score']['collect_battle_lost']},
        {'name': '...complete war day battle?', 'yes': config['score']['war_battle_played'], 'no': config['score']['war_battle_incomplete']},
        {'name': '...win war day battle? (per battle)', 'yes': config['score']['war_battle_won'], 'no': config['score']['war_battle_lost']}
    ]

    for rule in rules:
        rule['yes_status'] = get_score_rule_status(rule['yes'])
        rule['no_status'] = get_score_rule_status(rule['no'])

    return rules  

def process_members(clan, warlog, config):
    """ Process member list, adding calculated meta-data for rendering of 
    status in the clan member table. """

    # calculate the number of days since the donation last sunday, for 
    # donation tracking purposes:
    days_from_donation_reset = datetime.utcnow().isoweekday()
    if days_from_donation_reset == 7:
        days_from_donation_reset = 0

    cardsPerCollectionBattleWin = 0
    for score, lookupTable in WAR_LEAGUE_LOOKUP.items():
        if clan['clanWarTrophies'] >= score:
            cardsPerCollectionBattleWin = lookupTable['win']

            ###########################################################
            # FIXME -- this shouldn't be here. We shouldn't be 
            # modifying the clan object in this function. 
            clan['war_league'] = lookupTable['id']
            clan['war_league_name'] = lookupTable['name']
            ###########################################################

    # grab importent fields from member list for dashboard
    members = clan['memberList']
    members_processed = []
    for member in members:
        # calculate the number of daily donations, and the donation status 
        # based on threshold set in config
        member['donation_status'] = 'normal'
        if member['donations'] > (days_from_donation_reset) * 40:
            member['donation_status'] = 'good'
        if days_from_donation_reset >= 1:
            if member['donations'] == 0:
                member['donation_status'] = 'bad'
            elif member['donations'] < (days_from_donation_reset-1) * config['score']['min_donations_daily']:
                member['donation_status'] = 'ok'
            member['donations_daily'] = round(member['donations'] / (days_from_donation_reset))
        else:
            member['donations_daily'] = member['donations']

        # get member warlog and add it to the record
        member['warlog'] = member_warlog(member['tag'], warlog, cardsPerCollectionBattleWin)

        # get member score
        member['score'] = member_score(member, member['warlog'], days_from_donation_reset, config)
        
        # based on member score, infer an overall member status, which is 
        # either 'good', 'ok', 'bad', or 'normal'
        if member['score'] >= 0:
            if member['score'] >= config['score']['threshold_promote']:
                member['status'] = 'good'
            elif member['score'] < config['score']['threshold_warn']:
                member['status'] = 'ok'
            else:
                member['status'] = 'normal'
        else:
            member['status'] = 'bad'

        if member['trophies'] >= clan['requiredTrophies']:
            member['trophies_status'] = 'normal'
        else:
            member['trophies_status'] = 'ok'
        if member['arena']['name'] in ARENA_LEAGUE_LOOKUP:
            member['arena_league'] = ARENA_LEAGUE_LOOKUP[member['arena']['name']]['id']

        # Figure out whether member is on the leadership team by role
        if member['role'] == 'leader' or member['role'] == 'coLeader':
            member['leadership'] = True
        else: 
            member['leadership'] = False

        # Format 'co-leader" in sane way'
        if member['role'] == 'coLeader':
            member['role'] = 'co-leader'

        members_processed.append(member)

    return members_processed

def build_dashboard(api, config):
    """Compile and render clan dashboard."""

    # Putting everything in a `try`...`finally` to ensure `tempdir` is removed
    # when we're done. We don't want to pollute the user's disk.
    try:
        # Create temporary directory. All file writes, until the very end,
        # will happen in this directory, so that no matter what we do, it
        # won't hose existing stuff.
        tempdir = tempfile.mkdtemp(config['paths']['temp_dir_name'])

        # Get clan data and war log from API.
        clan = api.get_clan()
        warlog = api.get_warlog()

        # copy static assets to output path
        shutil.copytree(os.path.join(os.path.dirname(__file__), 'static'), os.path.join(tempdir, 'static'))

        # If logo_path is provided, grab logo from path given, and put it where 
        # it needs to go. Otherwise, grab the default from the template folder
        logo_dest_path = os.path.join(tempdir, 'clan_logo.png')
        if config['paths']['clan_logo']:
            logo_src_path = os.path.expanduser(config['paths']['clan_logo'])
            shutil.copyfile(logo_src_path, logo_dest_path)
        else:
            shutil.copyfile(os.path.join(os.path.dirname(__file__), 'templates/crtools-logo.png'), logo_dest_path)        

        # If favicon_path is provided, grab favicon from path given, and put it  
        # where it needs to go. Otherwise, grab the default from the template folder
        favicon_dest_path = os.path.join(tempdir, 'favicon.ico')
        if config['paths']['favicon']:
            favicon_src_path = os.path.expanduser(config['paths']['favicon'])
            shutil.copyfile(favicon_src_path, favicon_dest_path)
        else:
            shutil.copyfile(os.path.join(os.path.dirname(__file__), 'templates/crtools-favicon.ico'), favicon_dest_path)        

        # if external clan description file is specified, read that file and use it for 
        # the clan description section. If not, use the clan description returned by
        # the API
        clan_description_html = clan['description']
        if config['paths']['description_html']:
            description_path = os.path.expanduser(config['paths']['description_html'])
            if os.path.isfile(description_path):
                with open(description_path, 'r') as myfile:
                    clan_description_html = myfile.read()
            else:
                clan_description_html = "ERROR: File '{}' does not exist.".format(description_path)

        members_processed = process_members(clan, warlog, config)

        # Create environment for template parser
        env = Environment(
                loader=PackageLoader('crtools', 'templates'),
                autoescape=select_autoescape(['html', 'xml'])
            )

        member_table_html = env.get_template('member-table.html.j2').render(
            members      = members_processed, 
            clan_name    = clan['name'], 
            min_trophies = clan['requiredTrophies'], 
            war_dates    = warlog_dates(warlog)
        )

        dashboard_html = env.get_template('page.html.j2').render(
                version           = __version__,
                config            = config,
                update_date       = datetime.now().strftime('%c'),
                member_table      = member_table_html,
                clan              = clan,
                clan_description  = clan_description_html,
                suggestions       = get_suggestions(members_processed, config),
                scoring_rules     = get_scoring_rules(config)
            )
        write_object_to_file(os.path.join(tempdir, 'index.html'), dashboard_html)
        
        # archive outputs of API for debugging
        log_path = os.path.join(tempdir, 'log')
        os.makedirs(log_path)
        write_object_to_file(os.path.join(log_path, 'clan.json'), json.dumps(clan, indent=4))
        write_object_to_file(os.path.join(log_path, 'warlog.json'), json.dumps(warlog, indent=4))

        if config['www']['canonical_url'] != False:
            lastmod = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
            sitemap_xml = env.get_template('sitemap.xml.j2').render(
                    url     = config['www']['canonical_url'],
                    lastmod = lastmod
                )
            robots_txt = env.get_template('robots.txt.j2').render(
                    canonical_url = config['www']['canonical_url']
                )
            write_object_to_file(os.path.join(tempdir, 'sitemap.xml'), sitemap_xml)
            write_object_to_file(os.path.join(tempdir, 'robots.txt'), robots_txt)

        # remove output directory if previeously created to cleanup. Then 
        # create output path and log path.
        output_path = os.path.expanduser(config['paths']['out'])
        if os.path.exists(output_path):
            shutil.copystat(output_path, tempdir)
            shutil.rmtree(output_path)

        # Copy entire contents of temp directory to output directory
        shutil.copytree(tempdir, output_path)
    finally:
        # Ensure that temporary directory gets deleted no matter what
        shutil.rmtree(tempdir)

