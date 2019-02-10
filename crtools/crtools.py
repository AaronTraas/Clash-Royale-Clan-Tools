#!/usr/bin/python
"""Tools for creating a clan maagement dashboard for Clash Royale."""

__license__   = 'LGPLv3'
__docformat__ = 'reStructuredText'

import codecs
from datetime import datetime, date, timezone
from jinja2 import Environment, PackageLoader, StrictUndefined, select_autoescape
import json
import logging
import math
import os
import shutil
import tempfile

from .api import ClashRoyaleAPI, ClashRoyaleAPIError, ClashRoyaleAPIMissingFieldsError, ClashRoyaleAPIAuthenticationError, ClashRoyaleAPIClanNotFound
from ._version import __version__

ARENA_LEAGUE_LOOKUP = {
    'Arena Unknown' : { 'id':  'arena-unknown',     'collection_win': { 'bronze': 1,   'silver': 1,   'gold': 1,   'legendary': 1   } },
    'Arena 1'       : { 'id':  'arena-1',           'collection_win': { 'bronze': 40,  'silver': 80,  'gold': 140, 'legendary': 220 } },
    'Arena 2'       : { 'id':  'arena-2',           'collection_win': { 'bronze': 50,  'silver': 100, 'gold': 175, 'legendary': 275 } },
    'Arena 3'       : { 'id':  'arena-3',           'collection_win': { 'bronze': 60,  'silver': 120, 'gold': 210, 'legendary': 330 } },
    'Arena 4'       : { 'id':  'arena-4',           'collection_win': { 'bronze': 70,  'silver': 140, 'gold': 245, 'legendary': 385 } },
    'Arena 5'       : { 'id':  'arena-5',           'collection_win': { 'bronze': 80,  'silver': 160, 'gold': 280, 'legendary': 440 } },
    'Arena 6'       : { 'id':  'arena-6',           'collection_win': { 'bronze': 90,  'silver': 180, 'gold': 315, 'legendary': 495 } },
    'Arena 7'       : { 'id':  'arena-7',           'collection_win': { 'bronze': 100, 'silver': 200, 'gold': 350, 'legendary': 550 } },
    'Arena 8'       : { 'id':  'arena-8',           'collection_win': { 'bronze': 110, 'silver': 220, 'gold': 385, 'legendary': 605 } },
    'Arena 9'       : { 'id':  'arena-9',           'collection_win': { 'bronze': 120, 'silver': 240, 'gold': 420, 'legendary': 660 } },
    'Arena 10'      : { 'id':  'arena-10',          'collection_win': { 'bronze': 130, 'silver': 260, 'gold': 455, 'legendary': 715 } },
    'Arena 11'      : { 'id':  'arena-11',          'collection_win': { 'bronze': 140, 'silver': 280, 'gold': 490, 'legendary': 770 } },
    'Arena 12'      : { 'id':  'arena-12',          'collection_win': { 'bronze': 150, 'silver': 300, 'gold': 525, 'legendary': 825 } },
    'Arena 13'      : { 'id':  'arena-13',          'collection_win': { 'bronze': 150, 'silver': 300, 'gold': 525, 'legendary': 825 } },
    'League 1'      : { 'id':  'challenger-1',      'collection_win': { 'bronze': 160, 'silver': 320, 'gold': 560, 'legendary': 880 } },
    'League 2'      : { 'id':  'challenger-2',      'collection_win': { 'bronze': 160, 'silver': 320, 'gold': 560, 'legendary': 880 } },
    'League 3'      : { 'id':  'challenger-3',      'collection_win': { 'bronze': 160, 'silver': 320, 'gold': 560, 'legendary': 880 } },
    'League 4'      : { 'id':  'master-1',          'collection_win': { 'bronze': 170, 'silver': 340, 'gold': 595, 'legendary': 935 } },
    'League 5'      : { 'id':  'master-2',          'collection_win': { 'bronze': 170, 'silver': 340, 'gold': 595, 'legendary': 935 } },
    'League 6'      : { 'id':  'master-3',          'collection_win': { 'bronze': 170, 'silver': 340, 'gold': 595, 'legendary': 935 } },
    'League 7'      : { 'id':  'champion',          'collection_win': { 'bronze': 180, 'silver': 360, 'gold': 630, 'legendary': 990 } },
    'League 8'      : { 'id':  'grand-champion',    'collection_win': { 'bronze': 180, 'silver': 360, 'gold': 630, 'legendary': 990 } },
    'League 9'      : { 'id':  'ultimate-champion', 'collection_win': { 'bronze': 180, 'silver': 360, 'gold': 630, 'legendary': 990 } }
}

WAR_LEAGUE_LOOKUP = {
    0    : { 'id': 'bronze',    'name': 'Bronze League' },
    600  : { 'id': 'silver',    'name': 'Silver League' },
    1500 : { 'id': 'gold',      'name': 'Gold League' },
    3000 : { 'id': 'legendary', 'name': 'Legendary League' }
}

logger = logging.getLogger(__name__)

def write_object_to_file(file_path, obj):
    """ Writes contents of object to file. If object is a string, write it
    directly. Otherwise, convert it to JSON first """

    # open file for UTF-8 output, and write contents of object to file
    with codecs.open(file_path, 'w', 'utf-8') as f:
        if isinstance(obj, str):
            string = obj
        else:
            string = json.dumps(obj, indent=4)
        f.write(string)

def warlog_labels(warlog, clan_tag):
    """ Return list of date strings from warlog. One entry per war. """

    labels = []
    for war in warlog:
        date = datetime.strptime(war['createdDate'].split('.')[0], '%Y%m%dT%H%M%S')
        label = {
            'date'   : '{}/{}'.format(date.month, date.day),
            'league' : get_war_league_from_war(war, clan_tag)
        }
        labels.append(label)
    return labels

def get_war_league_from_score(clan_score):
    """ Figure out which war league a clan trophy count corresponds to,
    and return war league details. """
    league = 'ERROR'
    for score, lookup_table in WAR_LEAGUE_LOOKUP.items():
        if clan_score >= score:
            league = lookup_table

    return league

def get_war_league_from_war(war, clan_tag):
    """ Figure out which war league a clan was in during a given war. """
    standing = war['standings']

    clan_score = 0
    for clan in standing:
        if clan['clan']['tag'] == clan_tag:
            clan_score = clan['clan']['clanScore']

    return get_war_league_from_score(clan_score)

def member_war(config, clan_member, clan, war):
    member_tag = clan_member['tag']
    participation = {'status': 'na', 'score': config['score']['war_non_participation']}
    if 'participants' in war:
        for member in war['participants']:
            if member['tag'] == member_tag:
                participation = member.copy()
                if 'standings' in war:
                    if member['collectionDayBattlesPlayed'] == 0:
                        participation['status'] = 'na'
                    elif member['battlesPlayed'] == 0:
                        participation['status'] = 'bad'
                    elif member['collectionDayBattlesPlayed'] < 3:
                        participation['status'] = 'ok'
                    else:
                        participation['status'] = 'good'

                    participation['warLeague'] = get_war_league_from_war(war, clan['tag'])['id']

                    if clan_member['arena']['name'] in ARENA_LEAGUE_LOOKUP:
                        league_lookup = ARENA_LEAGUE_LOOKUP[clan_member['arena']['name']]
                    else:
                        league_lookup = ARENA_LEAGUE_LOOKUP['Arena Unknown']
                    collection_win_lookup = league_lookup['collection_win']

                    participation['collectionWinCards'] = collection_win_lookup[participation['warLeague']]

                    participation['collectionBattleWins'] = round(member['cardsEarned'] / participation['collectionWinCards'])
                    participation['collectionBattleLosses'] = participation['collectionDayBattlesPlayed'] - participation['collectionWinCards']
                    participation['score'] = war_score(config, participation)
                else:
                    participation['status'] = 'normal'
                    if participation['collectionDayBattlesPlayed'] < 3:
                        participation['status'] = 'ok'
                    if war['state'] == 'warDay' and participation['battlesPlayed'] > 0:
                        participation['status'] = 'good'
                    else:
                        participation['status'] += ' incomplete'

    return participation

def member_warlog(config, clan_member, clan, warlog):
    """ Return war participation records for a given member by member tag. """
    member_warlog = []
    for war in warlog:
        participation = member_war(config, clan_member, clan, war)
        member_warlog.append(participation)

    return member_warlog

def donations_score(config, member, days_from_donation_reset):
    """ Calculate the score for a given member's daily donations. """

    # calculate score based `days_from_donation_reset`.
    target_donations = config['score']['min_donations_daily'] * (days_from_donation_reset)
    donation_score = member['donations'] - target_donations

    # exempt additional penalties if at least a day hasn't passed
    if days_from_donation_reset > 1:
        donation_score = round(donation_score / days_from_donation_reset)

        # bigger penalty for 0 donations
        if member['donations'] == 0:
            donation_score += config['score']['donations_zero']

    donation_score = donation_score if donation_score <= config['score']['max_donations_bonus'] else config['score']['max_donations_bonus']

    return donation_score

def war_score(config, war):
    """ Tally the score for a given war """

    war_score = 0
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

    return war_score

def get_suggestions(config, members):
    """ Returns list of suggestions for the clan leadership to perform.
    Suggestions are to kick, demote, or promote. Suggestions are based on
    user score, and various thresholds in configuration. """

    # sort members by score, and preserve trophy order if relevant
    members_by_score = sorted(members, key=lambda k: (k['score'], k['trophies']))

    logger.debug("min_clan_size: {}".format(config['score']['min_clan_size']))
    logger.debug("# members: {}".format(len(members_by_score)))

    suggestions = []
    for index, member in enumerate(members_by_score):
        # if member on the 'safe' or 'vacation' list, don't make
        # recommendations to kick or demote
        if not (member['safe'] or member['vacation']) and member['currentWar']['status'] == 'na':
            # if  members have a score below zero, we recommend to kick or
            # demote them.
            # if we're above the minimum clan size, recommend kicking
            # poorly participating member.
            if member['score'] < config['score']['threshold_kick'] and index <= len(members_by_score) - config['score']['min_clan_size']:
                suggestion = 'Kick <strong>{}</strong> <strong class="bad">{}</strong>'.format(member['name'], member['score'])
                logger.debug(suggestion)
                suggestions.append(suggestion)
            # If we aren't recommending kicking someone, and their role is
            # > member, recoomend demotion
            elif member['role'] != 'member' and member['score'] < config['score']['threshold_demote']:
                suggestions.append('Demote <strong>{}</strong> <strong class="bad">{}</strong>'.format(member['name'], member['score']))

        # if user is above the threshold, and has not been promoted to
        # Elder or higher, recommend promotion.
        if not member['blacklist'] and (member['score'] >= config['score']['threshold_promote']) and (member['role'] == 'member'):
            suggestions.append('Promote <strong>{}</strong> to <strong>Elder</strong> <strong class="good">{}</strong>'.format(member['name'], member['score']))

    # If there are no other suggestions, give some sort of message
    if len(suggestions) == 0:
        if config['score']['min_clan_size'] >= len(members_by_score):
            suggestions.append('<strong>Recruit new members!</strong> The team needs some fresh blood.')
        else:
            suggestions.append('No suggestions at this time. The clan is in good order.')

    return suggestions


def get_scoring_rules(config):
    """ Get list of scoring rules to display on the site """

    def get_score_rule_status(score):
        if score > 0:
            return 'good'
        elif score < 0:
            return 'bad'
        else:
            return 'normal'

    rules = [
        {'name': '...participate in the war?',                          'yes': config['score']['war_participation'],        'no': config['score']['war_non_participation'] },
        {'name': '...complete each collection battle? (per battle)',    'yes': config['score']['collect_battle_played'],    'no': config['score']['collect_battle_incomplete']},
        {'name': '...win each collection battle? (per battle)',         'yes': config['score']['collect_battle_won'],       'no': config['score']['collect_battle_lost']},
        {'name': '...complete war day battle?',                         'yes': config['score']['war_battle_played'],        'no': config['score']['war_battle_incomplete']},
        {'name': '...win war day battle? (per battle)',                 'yes': config['score']['war_battle_won'],           'no': config['score']['war_battle_lost']}
    ]

    for rule in rules:
        rule['yes_status'] = get_score_rule_status(rule['yes'])
        rule['no_status'] = get_score_rule_status(rule['no'])

    return rules

def process_members(config, clan, warlog, current_war):
    """ Process member list, adding calculated meta-data for rendering of
    status in the clan member table. """

    # calculate the number of days since the donation last sunday, for
    # donation tracking purposes:
    days_from_donation_reset = datetime.utcnow().isoweekday()
    if days_from_donation_reset >= 7 or days_from_donation_reset <= 0:
        days_from_donation_reset = 1

    # grab importent fields from member list for dashboard
    members = clan['memberList'].copy()
    members_processed = []
    for member_src in members:
        member = member_src.copy()
        # calculate the number of daily donations, and the donation status
        # based on threshold set in config
        member['donationStatus'] = 'normal'
        if member['donations'] > (days_from_donation_reset) * 40:
            member['donationStatus'] = 'good'
        if days_from_donation_reset >= 1:
            if member['donations'] == 0:
                member['donationStatus'] = 'bad'
            elif member['donations'] < (days_from_donation_reset-1) * config['score']['min_donations_daily']:
                member['donationStatus'] = 'ok'
            member['donationsDaily'] = round(member['donations'] / (days_from_donation_reset))
        else:
            member['donationsDaily'] = member['donations']

        # get member warlog and add it to the record
        member['currentWar'] = member_war(config, member, clan, current_war)
        member['warlog'] = member_warlog(config, member, clan, warlog)

        member['donationScore'] = donations_score(config, member, days_from_donation_reset)

        # calculate score based on war participation
        member['warScore'] = 0
        for war in member['warlog']:
            member['warScore'] += war['score']

        # get member score
        member['score'] = member['warScore'] + member['donationScore']

        # it's good to be the king -- leader score floor of zero
        if (member['role'] == 'leader') and (member['score'] < 0):
            member['score'] = 0

        member['vacation'] = member['tag'] in config['members']['vacation']
        member['safe'] = member['tag'] in config['members']['safe']
        member['blacklist'] = member['tag'] in config['members']['blacklist']

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
            member['trophiesStatus'] = 'normal'
        else:
            member['trophiesStatus'] = 'ok'

        if member['arena']['name'] in ARENA_LEAGUE_LOOKUP:
            member['arenaLeague'] = ARENA_LEAGUE_LOOKUP[member['arena']['name']]['id']
        else:
            member['arenaLeague'] = ARENA_LEAGUE_LOOKUP['Arena Unknown']['id']

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

def process_clan(config, clan, current_war):
    clan_processed = clan.copy()
    del clan_processed['memberList']

    # figure out clan war league from clan score
    league = get_war_league_from_score(clan['clanWarTrophies'])
    clan_processed['warLeague']      = league['id']
    clan_processed['warLeagueName']  = league['name']

    clan_processed['currentWarState'] = current_war['state']

    return clan_processed

def process_current_war(config, current_war):
    current_war_processed = current_war.copy()

    if current_war_processed['state'] == 'notInWar':
        current_war_processed['stateLabel'] = 'The clan is not currently engaged in a war.'
    else:
        cards = 0;
        for member in current_war_processed['participants']:
            cards += member['cardsEarned']
        current_war_processed['cards'] = cards

        now = datetime.utcnow()
        if current_war_processed['state'] == 'collectionDay':
            current_war_processed['stateLabel'] = 'Collection Day'

            collection_end_time = datetime.strptime(current_war_processed['collectionEndTime'].split('.')[0], '%Y%m%dT%H%M%S')
            collection_end_time_delta = math.floor((collection_end_time - now).seconds / 3600)
            current_war_processed['collectionEndTimeLabel'] = '{} hours'.format(collection_end_time_delta)
            current_war_processed['endLabel'] = '1 day, {} hours'.format(collection_end_time_delta)
        else:
            current_war_processed['stateLabel'] = 'War Day'

            end_time = datetime.strptime(current_war_processed['warEndTime'].split('.')[0], '%Y%m%dT%H%M%S')
            end_time_delta = math.floor((end_time - now).seconds / 3600)
            current_war_processed['collectionEndTimeLabel'] = 'Complete'
            current_war_processed['endLabel'] = '{} hours'.format(end_time_delta)

            # calculate battles remaining for each clan
            for clan in current_war_processed['clans']:
                clan['battlesRemaining'] = clan['participants'] - clan['battlesPlayed']
                if clan['battlesRemaining'] < 0:
                    clan['battlesRemaining'] = 0;

            # sort clans by who's winning
            current_war_processed['clans'] = sorted(current_war_processed['clans'], key=lambda k: (k['wins'], k['crowns']), reverse=True)

    return current_war_processed

def process_recent_wars(config, warlog):
    wars = []
    for war in warlog:
        clan = None
        for rank, war_clan in enumerate(war['standings']):
            if war_clan['clan']['tag'] == config['api']['clan_id']:
                clan = war_clan['clan']
                clan['trophyChange'] = war_clan['trophyChange']
                clan['rank'] = rank+1
                date = datetime.strptime(war['createdDate'].split('.')[0], '%Y%m%dT%H%M%S')
                clan['date'] = '{}/{}'.format(date.month, date.day)
                wars.append(clan)

    return wars

def build_dashboard(config):
    """Compile and render clan dashboard."""

    logger.debug('crtools version v{}'.format(__version__))
    logger.debug(config)

    # Putting everything in a `try`...`finally` to ensure `tempdir` is removed
    # when we're done. We don't want to pollute the user's disk.
    try:
        # Create temporary directory. All file writes, until the very end,
        # will happen in this directory, so that no matter what we do, it
        # won't hose existing stuff.
        tempdir = tempfile.mkdtemp(config['paths']['temp_dir_name'])

        api = ClashRoyaleAPI(config['api']['server_url'], config['api']['api_key'], config['api']['clan_id'])

        # Get clan data and war log from API.
        clan = api.get_clan()
        warlog = api.get_warlog()
        current_war = api.get_current_war()

        # copy static assets to output path
        shutil.copytree(os.path.join(os.path.dirname(__file__), 'static'), os.path.join(tempdir, 'static'))

        # If logo_path is provided, grab logo from path given, and put it where
        # it needs to go. Otherwise, grab the default from the template folder
        logo_dest_path = os.path.join(tempdir, 'clan_logo.png')
        logo_src_path = os.path.join(os.path.dirname(__file__), 'templates', 'crtools-logo.png')
        if config['paths']['clan_logo']:
            logo_src_path_test = os.path.expanduser(config['paths']['clan_logo'])
            if os.path.isfile(logo_src_path_test):
                logo_src_path = logo_src_path_test
            else:
                logger.warn('custom logo file "{}" not found. Using default instead.'.format(logo_src_path_test))

        shutil.copyfile(logo_src_path, logo_dest_path)

        # If favicon_path is provided, grab favicon from path given, and put it
        # where it needs to go. Otherwise, grab the default from the template folder
        favicon_dest_path = os.path.join(tempdir, 'favicon.ico')
        favicon_src_path = os.path.join(os.path.dirname(__file__), 'templates', 'crtools-favicon.ico')
        if config['paths']['favicon']:
            favicon_src_path_test = os.path.expanduser(config['paths']['favicon'])
            if os.path.isfile(favicon_src_path_test):
                favicon_src_path = favicon_src_path_test
            else:
                logger.warn('custom favicon file "{}" not found. Using default instead.'.format(favicon_src_path_test))

        shutil.copyfile(favicon_src_path, favicon_dest_path)

        # if external clan description file is specified, read that file and use it for
        # the clan description section. If not, use the clan description returned by
        # the API
        clan_hero_html = None
        if config['paths']['description_html']:
            description_path = os.path.expanduser(config['paths']['description_html'])
            if os.path.isfile(description_path):
                with open(description_path, 'r') as myfile:
                    clan_hero_html = myfile.read()
            else:
                logger.warn('custom description file "{}" not found. Using default instead.'.format(description_path))

        clan_processed = process_clan(config, clan, current_war)
        members_processed = process_members(config, clan, warlog, current_war)
        current_war_processed = process_current_war(config, current_war)
        recent_wars = process_recent_wars(config, warlog)

        # Create environment for template parser
        env = Environment(
            loader=PackageLoader('crtools', 'templates'),
            autoescape=select_autoescape(['html', 'xml']),
            undefined=StrictUndefined
        )

        dashboard_html = env.get_template('page.html.j2').render(
            version           = __version__,
            config            = config,
            update_date       = datetime.now().strftime('%c'),
            members           = members_processed,
            war_labels        = warlog_labels(warlog, clan['tag']),
            clan              = clan_processed,
            clan_hero         = clan_hero_html,
            current_war       = current_war_processed,
            recent_wars       = recent_wars,
            suggestions       = get_suggestions(config, members_processed),
            scoring_rules     = get_scoring_rules(config)
        )

        write_object_to_file(os.path.join(tempdir, 'index.html'), dashboard_html)

        # If canonical URL is provided, also render the robots.txt and
        # sitemap.xml
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

        # archive outputs of API for debugging
        if(config['crtools']['debug'] == True):
            log_path = os.path.join(tempdir, 'log')
            os.makedirs(log_path)
            write_object_to_file(os.path.join(log_path, 'clan.json'),                  clan)
            write_object_to_file(os.path.join(log_path, 'warlog.json'),                warlog)
            write_object_to_file(os.path.join(log_path, 'currentwar.json'),            current_war)
            write_object_to_file(os.path.join(log_path, 'clan-processed.json'),        clan_processed)
            write_object_to_file(os.path.join(log_path, 'members-processed.json'),     members_processed)
            write_object_to_file(os.path.join(log_path, 'currentwar-processed.json'),  current_war_processed)
            write_object_to_file(os.path.join(log_path, 'recent_wars-processed.json'), recent_wars)

        output_path = os.path.expanduser(config['paths']['out'])
        if os.path.exists(output_path):
            # remove contents of output directory to cleanup.
            try:
                for file in os.listdir(output_path):
                    file_path = os.path.join(output_path, file)
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
            except PermissionError as e:
                logger.error('Permission error: could not delete: \n\t{}'.format(e.filename))
        else:
            # Output directory doesn't exist. Create it.
            if(config['crtools']['debug'] == True):
                logger.info('Output directory {} doesn\'t exist. Creating it.'.format(output_path))
            try:
                os.mkdir(output_path)
            except PermissionError as e:
                logger.error('Permission error: could create output folder: \n\t{}'.format(e.filename))

        try:
            # Copy all contents of temp directory to output directory
            for file in os.listdir(tempdir):
                file_path = os.path.join(tempdir, file)
                file_out_path = os.path.join(output_path, file)
                if os.path.isfile(file_path):
                    shutil.copyfile(file_path, file_out_path)
                elif os.path.isdir(file_path):
                    shutil.copytree(file_path, file_out_path)
        except PermissionError as e:
            logger.error('Permission error: could not write output to: \n\t{}'.format(e.filename))
        except FileExistsError as e:
            logger.error('File Exists: could not write output to: \n\t{}'.format(e.filename))

    except ClashRoyaleAPIAuthenticationError as e:
        msg = 'developer.clashroyale.com authentication error: {}'.format(e)
        if not config['api']['api_key']:
            msg += '\n - API key not provided'
        else:
            msg += '\n - API key not valid'
        logger.error(msg)

    except ClashRoyaleAPIClanNotFound as e:
        logger.error('developer.clashroyale.com: {}'.format(e))

    except ClashRoyaleAPIError as e:
        logger.error('developer.clashroyale.com error: {}'.format(e))

    except ClashRoyaleAPIMissingFieldsError as e:
        logger.error('error: {}'.format(e))

    finally:
        # Ensure that temporary directory gets deleted no matter what
        shutil.rmtree(tempdir)
