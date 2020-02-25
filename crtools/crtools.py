#!/usr/bin/python
"""Tools for creating a clan management dashboard for Clash Royale."""

__license__   = 'LGPLv3'
__docformat__ = 'reStructuredText'

from datetime import datetime
import logging
import os
import shutil
import tempfile

import pyroyale
import json

from ._version import __version__
from crtools.api_wrapper import ApiWrapper
from crtools import history
from crtools import fankit
from crtools import io
from crtools import discord
from crtools.memberfactory import MemberFactory
from crtools.models import FormerMember, ProcessedClan, ProcessedCurrentWar

MAX_CLAN_SIZE = 50

logger = logging.getLogger(__name__)

def get_suggestions(config, processed_members, required_trophies):
    """ Returns list of suggestions for the clan leadership to perform.
    Suggestions are to kick, demote, or promote. Suggestions are based on
    user score, and various thresholds in configuration. """

    # sort members by score, and preserve trophy order if relevant
    members_by_score = sorted(processed_members, key=lambda m: (m.score, m.trophies))

    logger.debug("min_clan_size: {}".format(config['score']['min_clan_size']))
    logger.debug("# members: {}".format(len(members_by_score)))

    suggestions = []
    for index, member in enumerate(members_by_score):
        if member.blacklist:
            suggestion = config['strings']['suggestionKickBlacklist'].format(name=member.name)
            logger.debug(suggestion)
            suggestions.append(suggestion)
            continue

        # if member on the 'safe' or 'vacation' list, don't make
        # recommendations to kick or demote
        if not (member.safe or member.vacation) and member.current_war.status == 'na':
            # suggest kick if inactive for the set threshold
            if member.days_inactive >= config['activity']['threshold_kick']:
                suggestion = config['strings']['suggestionKickInactivity'].format(name=member.name, days=member.days_inactive)
                logger.debug(suggestion)
                suggestions.append(suggestion)
            # if members have a score below zero, we recommend to kick or
            # demote them.
            # if we're above the minimum clan size, recommend kicking
            # poorly participating member.
            elif member.score < config['score']['threshold_kick'] and index <= len(members_by_score) - config['score']['min_clan_size']:
                suggestion = config['strings']['suggestionKickScore'].format(name=member.name, score=member.score)
                logger.debug(suggestion)
                suggestions.append(suggestion)
            # If we aren't recommending kicking someone, and their role is
            # > member, recoomend demotion
            elif member.role != 'member' and member.score < config['score']['threshold_demote']:
                suggestions.append(config['strings']['suggestionDemoteScore'].format(name=member.name, score=member.score))

        # if user is above the threshold, and has not been promoted to
        # Elder or higher, recommend promotion.
        if not member.no_promote and not member.blacklist and (member.score >= config['score']['threshold_promote']) and (member.role == 'member') and (member.trophies >= required_trophies) and (member.days_from_join > config['activity']['min_days_to_promote']):
            suggestions.append(config['strings']['suggestionPromoteScore'].format(name=member.name, score=member.score))

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

def process_members(config, clan, warlog, current_war, member_history, war_readiness_map={}):
    """ Process member list, adding calculated meta-data for rendering of
    status in the clan member table. """

    # calculate the number of days since the donation last sunday, for
    # donation tracking purposes:
    days_from_donation_reset = config['crtools']['timestamp'].isoweekday()
    if days_from_donation_reset > 7 or days_from_donation_reset <= 0:
        days_from_donation_reset = 1

    # process members with results from the API
    factory = MemberFactory(
        config=config,
        clan=clan,
        current_war=current_war,
        warlog=warlog,
        member_history=member_history,
        days_from_donation_reset=days_from_donation_reset)
    members_processed = []
    for member_src in clan.member_list:
        war_readiness = war_readiness_map.get(member_src.tag)
        members_processed.append(factory.get_processed_member(member_src, war_readiness))

    return members_processed

def process_absent_members(config, historical_members):
    absent_members = []

    for tag, member in historical_members.items():
        if member['status'] == 'absent':
            absent_members.append(FormerMember(
                config=config,
                historical_member=member,
                player_tag=tag,
                processed_events=history.process_member_events(config, member['events'])
            ))

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

    print('- requesting info for clan id: {}'.format(config['api']['clan_id']))

    api = ApiWrapper(config)

    clan, warlog, current_war = api.get_data_from_api()

    war_readiness_map = {}
    if config['member_table']['calc_war_readiness'] == True:
        war_readiness_map = api.get_war_readiness_map(clan.member_list, clan.clan_war_trophies)

    # Create temporary directory. All file writes, until the very end,
    # will happen in this directory, so that no matter what we do, it
    # won't hose existing stuff.
    tempdir = tempfile.mkdtemp(config['paths']['temp_dir_name'])

    # Putting everything in a `try`...`finally` to ensure `tempdir` is removed
    # when we're done. We don't want to pollute the user's disk.
    try:
        output_path = os.path.expanduser(config['paths']['out'])

        # process data from API
        current_war_processed = ProcessedCurrentWar(current_war, config)
        clan_processed = ProcessedClan(clan, current_war_processed, config)

        member_history = history.get_member_history(clan.member_list, config['crtools']['timestamp'], io.get_previous_history(output_path), current_war_processed)

        members_processed = process_members(config, clan, warlog, current_war_processed, member_history, war_readiness_map)
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
                    'current_war'           : current_war.to_dict(),
                    'clan-processed'        : clan_processed,
                    'members-processed'     : members_processed,
                    'current_war-processed' : current_war_processed,
                    'recentwars-processed'  : list(map(lambda war: war.to_dict(), recent_wars))
                }
            )

        # if fankit is previously downloaded, it will copy fankit. Otherwise,
        # if fankit is enabled, it will download it.
        fankit.get_fankit(tempdir, output_path, config['paths']['use_fankit'])

        io.copy_static_assets(tempdir, config['paths']['clan_logo'], config['paths']['favicon'])

        io.move_temp_to_output_dir(tempdir, output_path)

        discord.trigger_webhooks(config, current_war, members_processed)

    except Exception as e:
        logger.error('error: {}'.format(e))

    finally:
        # Ensure that temporary directory gets deleted no matter what
        shutil.rmtree(tempdir)
