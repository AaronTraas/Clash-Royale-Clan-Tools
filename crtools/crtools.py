#!/usr/bin/python
"""Tools for creating a clan maagement dashboard for Clash Royale."""

__license__   = 'LGPLv3'
__docformat__ = 'reStructuredText'

import copy
from datetime import datetime, date, timezone, timedelta
from html import escape
import logging
import math
import os
import pyroyale
from pyroyale.rest import ApiException
import shutil
import tempfile

from ._version import __version__
from crtools import history
from crtools import leagueinfo
from crtools import fankit
from crtools import io
from crtools import discord
from crtools.scorecalc import ScoreCalculator
from crtools.models import FormerMember, ProcessedClan, ProcessedCurrentWar

MAX_CLAN_SIZE = 50

logger = logging.getLogger(__name__)

def get_war_league_from_war(war, clan_tag):
    """ Figure out which war league a clan was in during a given war. """
    standing = war.standings

    clan_score = 0
    for clan in standing:
        if clan.clan.tag == clan_tag:
            clan_score = clan.clan.clan_score

    return leagueinfo.get_war_league_from_score(clan_score)

def get_member_war_status_class(collection_day_battles, war_day_battles, war_date, join_date, current_war=False, war_day=False):
    """ returns CSS class(es) for a war log entry for a given member """
    if war_date < join_date:
        return 'not-in-clan'

    status = 'normal'
    if current_war:
        if collection_day_battles < 3:
            status = 'ok'
        elif war_day and war_day_battles > 0:
            status = 'good'

        if war_day == False or war_day_battles == 0:
            status += ' incomplete'
    else:
        if collection_day_battles == 0:
            status = 'na'
        elif war_day_battles == 0:
            status = 'bad'
        elif collection_day_battles < 3:
            status = 'ok'
        else:
            status = 'good'
    return status

def get_war_date(war):
    """ returns the datetime this war was created. If it's an ongoing
    war, calculate based on the dates given when the war started.
    If it's a previous war fromt he warlog, we retrieve the creation
    date. What's returned is a timestamp. """
    if hasattr(war, 'state') :
        if war.state == 'warDay':
            war_date_raw = datetime.strptime(war.war_end_time.split('.')[0], '%Y%m%dT%H%M%S')
            war_date_raw -= timedelta(days=2)
        elif war.state == 'collectionDay':
            war_date_raw = datetime.strptime(war.collection_end_time.split('.')[0], '%Y%m%dT%H%M%S')
            war_date_raw -= timedelta(days=1)
    else:
        war_date_raw = datetime.strptime(war.created_date.split('.')[0], '%Y%m%dT%H%M%S')
        war_date_raw -= timedelta(days=1)

    return datetime.timestamp(war_date_raw)


def member_war(config, clan_member, war):

    # Bail early if this is for the current war, and there is no
    # current war
    if hasattr(war, 'state') and war.state == 'notInWar':
        return {
            'status': 'na',
            'score': 0
        }

    member_tag = clan_member['tag']
    war_date = get_war_date(war)
    join_date = clan_member['join_date'] if 'join_date' in clan_member else 0

    participation = {
        'status': get_member_war_status_class(0, 0, war_date, join_date),
    }
    participation['score'] = ScoreCalculator(config).get_war_score(participation)
    if hasattr(war, 'state') :
        participation['score'] = 0

    for member in war.participants:
        if member.tag == member_tag:
            participation = member.to_dict().copy()
            if hasattr(war, 'state') :
                participation['status'] = get_member_war_status_class(participation['collection_day_battles_played'], participation['battles_played'], war_date, join_date, True, war.state=='warDay')
                participation['score'] = 0
                continue;

            participation['status'] = get_member_war_status_class(participation['collection_day_battles_played'], participation['battles_played'], war_date, join_date)

            participation['warLeague'] = get_war_league_from_war(war, config['api']['clan_id'])
            participation['collectionWinCards'] = leagueinfo.get_collection_win_cards(participation['warLeague'], clan_member['arena']['name'])

            participation['collectionBattleWins'] = round(member.cards_earned / participation['collectionWinCards'])
            participation['collectionBattleLosses'] = participation['collection_day_battles_played'] - participation['collectionBattleWins']
            participation['score'] = ScoreCalculator(config).get_war_score(participation)

    return participation

def member_warlog(config, clan_member, warlog):
    """ Return war participation records for a given member by member tag. """
    member_warlog = []
    for war in warlog.items:
        participation = member_war(config, clan_member, war)
        member_warlog.append(participation)

    return member_warlog

def get_suggestions(config, processed_members, required_trophies):
    """ Returns list of suggestions for the clan leadership to perform.
    Suggestions are to kick, demote, or promote. Suggestions are based on
    user score, and various thresholds in configuration. """

    # sort members by score, and preserve trophy order if relevant
    members_by_score = sorted(processed_members, key=lambda k: (k['score'], k['trophies']))

    logger.debug("min_clan_size: {}".format(config['score']['min_clan_size']))
    logger.debug("# members: {}".format(len(members_by_score)))

    suggestions = []
    for index, member in enumerate(members_by_score):
        if member['blacklist']:
            suggestion = config['strings']['suggestionKickBlacklist'].format(name=member['name'])
            logger.debug(suggestion)
            suggestions.append(suggestion)
            continue

        # if member on the 'safe' or 'vacation' list, don't make
        # recommendations to kick or demote
        if not (member['safe'] or member['vacation']) and member['current_war']['status'] == 'na':
            # suggest kick if inactive for the set threshold
            if member['days_inactive'] >= config['activity']['threshold_kick']:
                suggestion = config['strings']['suggestionKickInactivity'].format(name=member['name'], days=member['days_inactive'])
                logger.debug(suggestion)
                suggestions.append(suggestion)
            # if members have a score below zero, we recommend to kick or
            # demote them.
            # if we're above the minimum clan size, recommend kicking
            # poorly participating member.
            elif member['score'] < config['score']['threshold_kick'] and index <= len(members_by_score) - config['score']['min_clan_size']:
                suggestion = config['strings']['suggestionKickScore'].format(name=member['name'], score=member['score'])
                logger.debug(suggestion)
                suggestions.append(suggestion)
            # If we aren't recommending kicking someone, and their role is
            # > member, recoomend demotion
            elif member['role'] != 'member' and member['score'] < config['score']['threshold_demote']:
                suggestions.append(config['strings']['suggestionDemoteScore'].format(name=member['name'], score=member['score']))

        # if user is above the threshold, and has not been promoted to
        # Elder or higher, recommend promotion.
        if not member['no_promote'] and not member['blacklist'] and (member['score'] >= config['score']['threshold_promote']) and (member['role'] == 'member') and (member['trophies'] >= required_trophies):
            suggestions.append(config['strings']['suggestionPromoteScore'].format(name=member['name'], score=member['score']))

    # If there are no other suggestions, give some sort of message
    if len(suggestions) == 0:
        if len(members_by_score) < MAX_CLAN_SIZE:
            suggestions.append(config['strings']['suggestionRecruit'])
        else:
            suggestions.append(config['strings']['suggestionNone'])

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
        {'name': config['strings']['ruleParticipate'],         'yes': config['score']['war_participation'],        'no': config['score']['war_non_participation'] },
        {'name': config['strings']['ruleCollectionComplete'], 'yes': config['score']['collect_battle_played'],    'no': config['score']['collect_battle_incomplete']},
        {'name': config['strings']['ruleCollectionWin'],      'yes': config['score']['collect_battle_won'],       'no': config['score']['collect_battle_lost']},
        {'name': config['strings']['ruleWarDayComplete'],     'yes': config['score']['war_battle_played'],        'no': config['score']['war_battle_incomplete']},
        {'name': config['strings']['ruleWarDayWin'],          'yes': config['score']['war_battle_won'],           'no': config['score']['war_battle_lost']}
    ]

    for rule in rules:
        rule['yes_status'] = get_score_rule_status(rule['yes'])
        rule['no_status'] = get_score_rule_status(rule['no'])

    return rules

def enrich_member_with_history(config, fresh_member, historical_members, days_from_donation_reset, now):
    enriched_member = copy.deepcopy(fresh_member)
    historical_member = historical_members[enriched_member['tag']]

    enriched_member['join_date'] = historical_member['join_date']
    enriched_member['last_activity_date'] = historical_member['last_activity_date']
    enriched_member['last_donation_date'] = historical_member['last_donation_date']
    enriched_member['donations_last_week'] = historical_member['donations_last_week']
    enriched_member['days_inactive'] = (now - datetime.fromtimestamp(enriched_member['last_activity_date'])).days
    enriched_member['days_inactive'] = enriched_member['days_inactive'] if enriched_member['days_inactive'] >= 0 else 0

    last_seen = datetime.strptime(enriched_member['last_seen'].split('.')[0], '%Y%m%dT%H%M%S')
    enriched_member['last_seen_formatted'] = last_seen.strftime('%c')

    last_seen_delta = now - last_seen
    enriched_member['last_seen_delta'] = ''
    if last_seen_delta.days >= 1:
        enriched_member['last_seen_delta'] = '{} {}, '.format(last_seen_delta.days, config['strings']['labelDays'])
    hours = round(last_seen_delta.seconds/3600)
    if hours < 1:
        enriched_member['last_seen_delta'] += '{} {}'.format(round(last_seen_delta.seconds/60), config['strings']['labelMinutes'])
    else:
        enriched_member['last_seen_delta'] += '{} {}'.format(hours, config['strings']['labelHours'])


    if enriched_member['join_date'] == 0:
        enriched_member['join_date_label'] = config['strings']['labelBeforeHistory']
    else:
        enriched_member['join_date_label'] = datetime.fromtimestamp(enriched_member['join_date']).strftime('%x')
    enriched_member['activity_date_label'] = datetime.fromtimestamp(enriched_member['last_activity_date']).strftime('%x')

    join_datetime = datetime.fromtimestamp(enriched_member['join_date'])
    days_from_join = (now - join_datetime).days
    if days_from_join <= 10:
        enriched_member['new'] = True
        logger.debug('New member {}'.format(enriched_member['name']))
    else:
        enriched_member['new'] = False

    if days_from_donation_reset > days_from_join:
        days_from_donation_reset = days_from_join

    if enriched_member['days_inactive'] > 7:
        enriched_member['donations_last_week'] = 0

    total_donations = enriched_member['donations']
    if days_from_join > days_from_donation_reset + 7 and 'donations_last_week' in enriched_member:
        days_from_donation_reset += 7
        total_donations += enriched_member['donations_last_week']

    enriched_member['total_donations'] = total_donations
    if(days_from_donation_reset > 0):
        enriched_member['donations_daily'] = round(total_donations / days_from_donation_reset)
    else:
        enriched_member['donations_daily'] = total_donations

    enriched_member['events'] = history.process_member_events(config, historical_member['events'])

    return enriched_member

def calc_donation_status(config, donation_score, donations_daily, days_from_donation_reset):
    """ calculate the number of daily donations, and the donation status
    based on threshold set in config """
    if donation_score >= config['score']['max_donations_bonus']:
        return 'good'

    if days_from_donation_reset >= 1:
        if donations_daily == 0:
            return 'bad'

        if donations_daily < config['score']['min_donations_daily']:
            return 'ok'

    return 'normal'

def calc_member_status(config, member_score, no_promote):
    # either 'good', 'ok', 'bad', or 'normal'
    if member_score < 0:
        return 'bad'

    if member_score >= config['score']['threshold_promote'] and not no_promote:
        return 'good'

    if member_score < config['score']['threshold_warn']:
        return 'ok'

    return 'normal'

def calc_activity_status(config, days_inactive):
    if days_inactive <= 0:
        return 'good'

    if days_inactive <= 2:
        return 'na'

    if days_inactive >= config['activity']['threshold_kick']:
        return 'bad'

    if days_inactive >= config['activity']['threshold_warn']:
        return 'ok'

    return 'normal'

def calc_recent_war_stats(member):
    war_wins = 0
    war_battles = 0
    collection_wins = 0
    collection_cards = 0
    for war in member['warlog']:
        if 'wins' in war:
            war_wins += war['wins']
            war_battles += war['number_of_battles']
        if 'collectionBattleWins' in war:
            collection_wins += war['collectionBattleWins']
        if 'collectionWinCards' in war:
            collection_cards += war['collectionWinCards']

    if war_battles > 0:
        member['war_win_rate'] = round((war_wins/war_battles) * 100)
    else:
        member['war_win_rate'] = 0

    member['war_collection_win_rate'] = round(((collection_wins / 10) / 3) * 100)
    member['war_collection_cards_average'] = round(collection_cards / 10)
    member['war_score_average'] = round(member['war_score'] / 10)

    return member


def get_role_label(config, member_role, days_inactive, activity_status, on_vacation, blacklisted, no_promote):
    """ Format roles in sane way """

    if blacklisted:
        return config['strings']['roleBlacklisted']

    if on_vacation:
        return config['strings']['roleVacation']

    if activity_status in ['bad', 'ok']:
        return config['strings']['roleInactive'].format(days=days_inactive)

    if no_promote:
        return config['strings']['roleNoPromote']

    return {
        'leader'   : config['strings']['roleLeader'],
        'coLeader' : config['strings']['roleCoLeader'],
        'elder'    : config['strings']['roleElder'],
        'member'   : config['strings']['roleMember'],
    }[member_role]

def calc_derived_member_stats(config, clan, warlog, current_war, member, days_from_donation_reset):
    member['name'] = escape(member['name'])

    # get special statuses.
    # vacation = member is on vacation. Don't reccomend demote or kick, dont show score
    # safe = member marked as safe. Don't reccomend demote or kick
    # blacklist = member on blacklist. Recommend kick immediately.
    member['vacation'] = member['tag'] in config['members']['vacation']
    member['safe'] = member['tag'] in config['members']['safe']
    member['no_promote'] = member['tag'] in config['members']['no_promote']
    member['blacklist'] = member['tag'] in config['members']['blacklist']

    # Automatically add inactive 'safe' members to vacation
    if member['safe'] and (member['days_inactive'] >= config['activity']['threshold_warn']):
        member['vacation'] = True

    calc = ScoreCalculator(config)

    # get member warlog and add it to the record
    member['current_war'] = member_war(config, member, current_war)
    member['warlog'] = member_warlog(config, member, warlog)

    member['donation_score'] = calc.get_member_donations_score(member)

    # calculate score based on war participation
    member['war_score'] = 0
    for war in member['warlog']:
        member['war_score'] += war['score']

    # get member score
    member['score'] = member['war_score'] + member['donation_score']

    # calculate the number of daily donations, and the donation status
    # based on threshold set in config
    member['donation_status'] = calc_donation_status(config, member['donation_score'], member['donations_daily'], days_from_donation_reset)

    member['status'] = calc_member_status(config, member['score'], member['no_promote'])

    member['activity_status'] = calc_activity_status(config, member['days_inactive'])

    member['role_label'] = get_role_label(config, member['role'], member['days_inactive'], member['activity_status'], member['vacation'], member['blacklist'], member['no_promote'])

    if member['trophies'] >= clan.required_trophies:
        member['trophiesStatus'] = 'normal'
    else:
        member['trophiesStatus'] = 'ok'

    member['arena_league'] = leagueinfo.get_arena_league_from_name(member['arena']['name'])['id']
    member['arena_league_label'] = config['strings']['league-' + member['arena_league']]

    # Figure out whether member is on the leadership team by role
    member['leadership'] = member['role'] == 'leader' or member['role'] == 'coLeader'

    member = calc_recent_war_stats(member)

    return member


def process_members(config, clan, warlog, current_war, member_history):
    """ Process member list, adding calculated meta-data for rendering of
    status in the clan member table. """

    # calculate the number of days since the donation last sunday, for
    # donation tracking purposes:
    now = datetime.utcnow()
    days_from_donation_reset = now.isoweekday()
    if days_from_donation_reset > 7 or days_from_donation_reset <= 0:
        days_from_donation_reset = 1

    # grab importent fields from member list for dashboard
    members_processed = []
    for member_src in clan.member_list:
        #members_processed.append(ProcessedClanMember(member, config, clan, current_war, member_history, days_from_donation_reset, now))

        member = enrich_member_with_history(config, member_src.to_dict(), member_history['members'], days_from_donation_reset, now)
        member = calc_derived_member_stats(config, clan, warlog, current_war, member, days_from_donation_reset)
        members_processed.append(member)

    return members_processed

def process_absent_members(config, historical_members):
    absent_members = []

    for tag, member in historical_members.items():
        if member['status'] == 'absent':
            absent_members.append(FormerMember(config=config, historical_member=member, player_tag=tag))

    return sorted(absent_members, key=lambda k: k.timestamp, reverse=True)

def process_recent_wars(config, warlog):
    wars = []
    for war in warlog.items:
        clan = None
        for rank, war_clan in enumerate(war.standings):
            if war_clan.clan.tag == config['api']['clan_id']:
                clan = war_clan
                clan.rank = rank+1
                date = datetime.strptime(war.created_date.split('.')[0], '%Y%m%dT%H%M%S')
                clan.date = config['strings']['labelWarDate'].format(month=date.month, day=date.day)
                wars.append(clan)

    return wars

# NOTE: we're not testing this function because this is where we're
# isolating all of the I/O for the application here. The real "work"
# here is done in all of the calls to functions in this file, or in the
# ClashRoyaleAPI class, both of which are fully covered. (or soon will
# be)
#
# Similarly, we've tagged this function, and this function alone, to
# be ignored by static analysis. I don't want to spread out all of
# the I/O and there's no way to make the exception handling anything
# other than a mess that will trigger teh cognitive complexity
# warnings.
def build_dashboard(config): # pragma: no coverage
    """Compile and render clan dashboard."""

    # Create temporary directory. All file writes, until the very end,
    # will happen in this directory, so that no matter what we do, it
    # won't hose existing stuff.
    tempdir = tempfile.mkdtemp(config['paths']['temp_dir_name'])

    # get API instance
    configuration = pyroyale.Configuration()
    configuration.api_key['authorization'] = config['api']['api_key']
    if config['api']['proxy']:
        configuration.proxy = config['api']['proxy']
    if config['api']['proxy_headers']:
        configuration.proxy_headers = config['api']['proxy_headers']
    api = pyroyale.ClansApi(pyroyale.ApiClient(configuration))

    print('- requesting info for clan id: {}'.format(config['api']['clan_id']))

    # Putting everything in a `try`...`finally` to ensure `tempdir` is removed
    # when we're done. We don't want to pollute the user's disk.
    try:
        output_path = os.path.expanduser(config['paths']['out'])

        # Get clan data and war log from API.
        clan = api.get_clan(config['api']['clan_id'])
        warlog = api.get_clan_war_log(config['api']['clan_id'])
        current_war = api.get_current_war(config['api']['clan_id'])

        print('- clan: {} ({})'.format(clan.name, clan.tag))

        # process data from API
        current_war_processed = ProcessedCurrentWar(current_war, config)
        clan_processed = ProcessedClan(clan, current_war_processed, config)

        member_history = history.get_member_history(clan.member_list, io.get_previous_history(output_path), current_war_processed)

        members_processed = process_members(config, clan, warlog, current_war_processed, member_history)
        recent_wars = process_recent_wars(config, warlog)
        former_members = process_absent_members(config, member_history['members'])

        io.parse_templates(
            config,
            member_history,
            tempdir,
            clan_processed,
            members_processed,
            former_members,
            current_war_processed,
            recent_wars,
            get_suggestions(config, members_processed, clan_processed.required_trophies),
            get_scoring_rules(config)
        )

        if(config['crtools']['debug'] == True):
            # archive outputs of API for debugging
            io.dump_debug_logs(
                tempdir,
                {
                    'clan'                  : clan.to_dict(),
                    'warlog'                : warlog.to_dict(),
                    'current_war'            : current_war.to_dict(),
                    'clan-processed'        : clan_processed.to_dict(),
                    'members-processed'     : members_processed,
                    'current_war-processed'  : current_war_processed.to_dict(),
                    'recentwars-processed'  : list(map(lambda war: war.to_dict(), recent_wars))
                }
            )

        # if fankit is previously downloaded, it will copy fankit. Otherwise,
        # if fankit is enabled, it will download it.
        fankit.get_fankit(tempdir, output_path, config['paths']['use_fankit'])

        io.copy_static_assets(tempdir, config['paths']['clan_logo'], config['paths']['favicon'])

        io.move_temp_to_output_dir(tempdir, output_path)

        discord.trigger_webhooks(config, current_war.to_dict(), members_processed)

    except ApiException as e:
        logger.error('error: {}'.format(e))

    finally:
        # Ensure that temporary directory gets deleted no matter what
        shutil.rmtree(tempdir)
