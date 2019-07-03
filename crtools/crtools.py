#!/usr/bin/python
"""Tools for creating a clan maagement dashboard for Clash Royale."""

__license__   = 'LGPLv3'
__docformat__ = 'reStructuredText'

import copy
from datetime import datetime, date, timezone, timedelta
import logging
import math
import os
import pyroyale
import shutil
import tempfile

from ._version import __version__
from crtools import history
from crtools import leagueinfo
from crtools import fankit
from crtools import io

MAX_CLAN_SIZE = 50

logger = logging.getLogger(__name__)

def get_war_league_from_war(war, clan_tag):
    """ Figure out which war league a clan was in during a given war. """
    standing = war['standings']

    clan_score = 0
    for clan in standing:
        if clan['clan']['tag'] == clan_tag:
            clan_score = clan['clan']['clanScore']

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
    if 'state' in war:
        if war['state'] == 'warDay':
            war_date_raw = datetime.strptime(war['warEndTime'].split('.')[0], '%Y%m%dT%H%M%S')
            war_date_raw -= timedelta(days=2)
        elif war['state'] == 'collectionDay':
            war_date_raw = datetime.strptime(war['collectionEndTime'].split('.')[0], '%Y%m%dT%H%M%S')
            war_date_raw -= timedelta(days=1)
    else:
        war_date_raw = datetime.strptime(war['createdDate'].split('.')[0], '%Y%m%dT%H%M%S')
        war_date_raw -= timedelta(days=1)

    return datetime.timestamp(war_date_raw)


def member_war(config, clan_member, war):

    # Bail early if this is for the current war, and there is no
    # current war
    if 'state' in war and war['state'] == 'notInWar':
        return {
            'status': 'na',
            'score': 0
        }

    member_tag = clan_member['tag']
    war_date = get_war_date(war)
    join_date = clan_member['join_date']

    participation = {
        'status': get_member_war_status_class(0, 0, war_date, join_date),
    }
    participation['score'] = war_score(config, participation)
    if 'state' in war:
        participation['score'] = 0

    if 'participants' in war:
        for member in war['participants']:
            if member['tag'] == member_tag:
                participation = member.copy()
                if 'state' in war:
                    participation['status'] = get_member_war_status_class(participation['collectionDayBattlesPlayed'], participation['battlesPlayed'], war_date, join_date, True, war['state']=='warDay')
                    participation['score'] = 0
                    continue;

                participation['status'] = get_member_war_status_class(participation['collectionDayBattlesPlayed'], participation['battlesPlayed'], war_date, join_date)

                participation['warLeague'] = get_war_league_from_war(war, config['api']['clan_id'])
                participation['collectionWinCards'] = leagueinfo.get_collection_win_cards(participation['warLeague'], clan_member['arena']['name'])

                participation['collectionBattleWins'] = round(member['cardsEarned'] / participation['collectionWinCards'])
                participation['collectionBattleLosses'] = participation['collectionDayBattlesPlayed'] - participation['collectionBattleWins']
                participation['score'] = war_score(config, participation)

    return participation

def member_warlog(config, clan_member, warlog):
    """ Return war participation records for a given member by member tag. """
    member_warlog = []
    for war in warlog:
        participation = member_war(config, clan_member, war)
        member_warlog.append(participation)

    return member_warlog

def donations_score(config, member):
    """ Calculate the score for a given member's daily donations. """

    donation_score = member['donationsDaily'] - config['score']['min_donations_daily']

    donation_score = donation_score if donation_score <= config['score']['max_donations_bonus'] else config['score']['max_donations_bonus']

    if member['totalDonations'] == 0:
        donation_score += config['score']['donations_zero']

    if member['new'] and donation_score <= 0:
        donation_score = 0

    #logger.debug('{:20}:\tdays: {:2}\tdonations: {:4}\n'.format(member['name'], days_from_donation_reset, member['donations']))

    return donation_score

def war_score(config, war):
    """ Tally the score for a given war """

    war_score = 0
    if war['status'] == 'not-in-clan':
        return 0;

    if 'battlesPlayed' not in war:
        return config['score']['war_non_participation']

    war_score += war['collectionBattleWins'] * config['score']['collect_battle_won']
    war_score += war['collectionBattleLosses'] * config['score']['collect_battle_lost']
    war_score += war['collectionDayBattlesPlayed'] * config['score']['collect_battle_played']
    war_score += (3-war['collectionDayBattlesPlayed']) * config['score']['collect_battle_incomplete']

    if war['battlesPlayed'] < 1:
        war_score += config['score']['war_battle_incomplete']
        return war_score

    war_score += war['battlesPlayed'] * config['score']['war_battle_played']
    war_score += war['wins'] * config['score']['war_battle_won']
    war_score += (war['battlesPlayed'] - war['wins']) * config['score']['war_battle_lost']

    return war_score

def get_suggestions(config, processed_members, clan_processed):
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
        if not (member['safe'] or member['vacation']) and member['currentWar']['status'] == 'na':
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
        if not member['no_promote'] and not member['blacklist'] and (member['score'] >= config['score']['threshold_promote']) and (member['role'] == 'member') and (member['trophies'] >= clan_processed['requiredTrophies']):
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

    enriched_member['totalDonations'] = total_donations
    if(days_from_donation_reset > 0):
        enriched_member['donationsDaily'] = round(total_donations / days_from_donation_reset)
    else:
        enriched_member['donationsDaily'] = total_donations

    enriched_member['events'] = process_member_events(config, historical_member['events'])

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

def process_member_events(config, events):
    processed_events = []
    for event in events:
        if event['date'] == 0:
            continue
        processed_events.append({
            'date'      : datetime.fromtimestamp(event['date']).strftime('%x'),
            'timestamp' : event['date'],
            'message'   : {
                'join'        : config['strings']['memberEventJoinedClan'],
                'role change' : config['strings']['memberEventRoleChange'].format(event['role']),
                'quit'        : config['strings']['memberEventExitClan']
            }[event['event']]
        })
    return processed_events


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
    members = clan['memberList'].copy()
    members_processed = []
    for member_src in members:
        member = enrich_member_with_history(config, member_src, member_history['members'], days_from_donation_reset, now)

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

        # get member warlog and add it to the record
        member['currentWar'] = member_war(config, member, current_war)
        member['warlog'] = member_warlog(config, member, warlog)

        member['donationScore'] = donations_score(config, member)

        # calculate score based on war participation
        member['warScore'] = 0
        for war in member['warlog']:
            member['warScore'] += war['score']

        # get member score
        member['score'] = member['warScore'] + member['donationScore']

        # calculate the number of daily donations, and the donation status
        # based on threshold set in config
        member['donationStatus'] = calc_donation_status(config, member['donationScore'], member['donationsDaily'], days_from_donation_reset)

        member['status'] = calc_member_status(config, member['score'], member['no_promote'])

        member['activity_status'] = calc_activity_status(config, member['days_inactive'])

        member['role_label'] = get_role_label(config, member['role'], member['days_inactive'], member['activity_status'], member['vacation'], member['blacklist'], member['no_promote'])

        if member['trophies'] >= clan['requiredTrophies']:
            member['trophiesStatus'] = 'normal'
        else:
            member['trophiesStatus'] = 'ok'

        member['arenaLeague'] = leagueinfo.get_arena_league_from_name(member['arena']['name'])['id']
        member['arenaLeagueLabel'] = config['strings']['league-' + member['arenaLeague']]

        # Figure out whether member is on the leadership team by role
        member['leadership'] = member['role'] == 'leader' or member['role'] == 'coLeader'

        members_processed.append(member)

    return members_processed

def process_absent_members(config, historical_members):
    absent_members = []

    for tag, member in historical_members.items():
        if member['status'] == 'absent':
            events = process_member_events(config, member['events'])
            absent_members.append({
                'name'      : member['name'],
                'tag'       : tag,
                'events'    : events,
                'timestamp' : events[len(events)-1]['timestamp']
            })

    return sorted(absent_members, key=lambda k: k['timestamp'], reverse=True)

def process_clan(config, clan, current_war):
    clan_processed = clan.copy()

    # remove memberlist from clan, as we're separating that out
    del clan_processed['memberList']

    # figure out clan war league from clan score
    league = leagueinfo.get_war_league_from_score(clan['clanWarTrophies'])

    clan_processed['warLeague']      = league
    clan_processed['warLeagueName']  = config['strings']['war-league-' + league]
    clan_processed['currentWarState'] = current_war['state']

    return clan_processed

def process_current_war(config, current_war):
    current_war_processed = current_war.copy()

    if current_war_processed['state'] == 'notInWar':
        current_war_processed['stateLabel'] = config['strings']['LabelNotInWar']
        return current_war_processed

    cards = 0;
    for member in current_war_processed['participants']:
        cards += member['cardsEarned']
    current_war_processed['cards'] = cards

    now = datetime.utcnow()
    if current_war_processed['state'] == 'collectionDay':
        current_war_processed['stateLabel'] = config['strings']['labelStateCollectionDay']

        collection_end_time = datetime.strptime(current_war_processed['collectionEndTime'].split('.')[0], '%Y%m%dT%H%M%S')
        collection_end_time_delta = math.floor((collection_end_time - now).seconds / 3600)
        current_war_processed['collectionEndTimeLabel'] = config['strings']['labelCollectionEndTime'].format(collection_end_time_delta)
        current_war_processed['endLabel'] = config['strings']['labelEndTime'].format(collection_end_time_delta)
    else:
        current_war_processed['stateLabel'] = config['strings']['labelStateWarDay']

        end_time = datetime.strptime(current_war_processed['warEndTime'].split('.')[0], '%Y%m%dT%H%M%S')
        end_time_delta = math.floor((end_time - now).seconds / 3600)
        current_war_processed['collectionEndTimeLabel'] = config['strings']['labelCollectionComplete']
        current_war_processed['endLabel'] = config['strings']['labelCollectionEndTime'].format(end_time_delta)

        # calculate battles remaining for each clan
        for clan in current_war_processed['clans']:
            clan['battlesRemaining'] = clan['participants'] - clan['battlesPlayed']
            if clan['battlesRemaining'] < 0:
                clan['battlesRemaining'] = 0; # pragma: no coverage

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
                clan['date'] = config['strings']['labelWarDate'].format(month=date.month, day=date.day)
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

    logger.debug('crtools version v{}'.format(__version__))
    logger.debug('pyroyale version v{}'.format(pyroyale.__version__))
    logger.debug(config)

    # Create temporary directory. All file writes, until the very end,
    # will happen in this directory, so that no matter what we do, it
    # won't hose existing stuff.
    tempdir = tempfile.mkdtemp(config['paths']['temp_dir_name'])

    # Putting everything in a `try`...`finally` to ensure `tempdir` is removed
    # when we're done. We don't want to pollute the user's disk.
    try:
        output_path = os.path.expanduser(config['paths']['out'])

        # Get clan data and war log from API.
        api = pyroyale.ClashRoyaleAPI(config['api']['api_key'], config['api']['clan_id'])
        clan = api.clan.clan_info()
        warlog = api.clan.warlog()
        current_war = api.clan.current_war()

        # process data from API
        current_war_processed = process_current_war(config, current_war)
        clan_processed = process_clan(config, clan, current_war)
        member_history = history.get_member_history(clan['memberList'], io.get_previous_history(output_path), current_war)
        members_processed = process_members(config, clan, warlog, current_war, member_history)
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
            get_suggestions(config, members_processed, clan_processed),
            get_scoring_rules(config)
        )

        if(config['crtools']['debug'] == True):
            # archive outputs of API for debugging
            io.dump_debug_logs(
                tempdir,
                {
                    'clan'                  : clan,
                    'warlog'                : warlog,
                    'currentwar'            : current_war,
                    'clan-processed'        : clan_processed,
                    'members-processed'     : members_processed,
                    'currentwar-processed'  : current_war_processed,
                    'recentwars-processed'  : recent_wars
                }
            )

        # if fankit is previously downloaded, it will copy fankit. Otherwise,
        # if fankit is enabled, it will download it.
        fankit.get_fankit(tempdir, output_path, config['paths']['use_fankit'])

        io.copy_static_assets(tempdir, config['paths']['clan_logo'], config['paths']['favicon'])

        io.move_temp_to_output_dir(tempdir, output_path)

    except pyroyale.ClashRoyaleAPIAuthenticationError as e:
        msg = 'developer.clashroyale.com authentication error: {}'.format(e)
        if not config['api']['api_key']:
            msg += '\n - API key not provided'
        else:
            msg += '\n - API key not valid'
        logger.error(msg)

    except pyroyale.ClashRoyaleAPIClanNotFound as e:
        logger.error('developer.clashroyale.com: {}'.format(e))

    except pyroyale.ClashRoyaleAPIError as e:
        logger.error('developer.clashroyale.com error: {}'.format(e))

    except pyroyale.ClashRoyaleAPIMissingFieldsError as e:
        logger.error('error: {}'.format(e))

    finally:
        # Ensure that temporary directory gets deleted no matter what
        shutil.rmtree(tempdir)
