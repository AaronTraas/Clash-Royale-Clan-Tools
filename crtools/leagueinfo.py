#!/usr/bin/python

"""Hardcoded data about arena and war leagues, and some functions
used to lookup specific data."""

__license__   = 'LGPLv3'
__docformat__ = 'reStructuredText'

import logging
from ._version import __version__

ARENA_LEAGUES = [
    { 'id':  'ultimate-champion', 'trophies': 7000, 'collection_win': { 'bronze': 180, 'silver': 360, 'gold': 630, 'legendary': 990 } },
    { 'id':  'royal-champion',    'trophies': 6600, 'collection_win': { 'bronze': 180, 'silver': 360, 'gold': 630, 'legendary': 990 } },
    { 'id':  'grand-champion',    'trophies': 6300, 'collection_win': { 'bronze': 180, 'silver': 360, 'gold': 630, 'legendary': 990 } },
    { 'id':  'champion',          'trophies': 6000, 'collection_win': { 'bronze': 180, 'silver': 360, 'gold': 630, 'legendary': 990 } },
    { 'id':  'master-3',          'trophies': 5600, 'collection_win': { 'bronze': 170, 'silver': 340, 'gold': 595, 'legendary': 935 } },
    { 'id':  'master-2',          'trophies': 5300, 'collection_win': { 'bronze': 170, 'silver': 340, 'gold': 595, 'legendary': 935 } },
    { 'id':  'master-1',          'trophies': 5000, 'collection_win': { 'bronze': 170, 'silver': 340, 'gold': 595, 'legendary': 935 } },
    { 'id':  'challenger-3',      'trophies': 4600, 'collection_win': { 'bronze': 160, 'silver': 320, 'gold': 560, 'legendary': 880 } },
    { 'id':  'challenger-2',      'trophies': 4300, 'collection_win': { 'bronze': 160, 'silver': 320, 'gold': 560, 'legendary': 880 } },
    { 'id':  'challenger-1',      'trophies': 4000, 'collection_win': { 'bronze': 160, 'silver': 320, 'gold': 560, 'legendary': 880 } },
    { 'id':  'arena-12',          'trophies': 3600, 'collection_win': { 'bronze': 150, 'silver': 300, 'gold': 525, 'legendary': 825 } },
    { 'id':  'arena-11',          'trophies': 3300, 'collection_win': { 'bronze': 140, 'silver': 280, 'gold': 490, 'legendary': 770 } },
    { 'id':  'arena-10',          'trophies': 3000, 'collection_win': { 'bronze': 130, 'silver': 260, 'gold': 455, 'legendary': 715 } },
    { 'id':  'arena-9',           'trophies': 2600, 'collection_win': { 'bronze': 120, 'silver': 240, 'gold': 420, 'legendary': 660 } },
    { 'id':  'arena-8',           'trophies': 2300, 'collection_win': { 'bronze': 110, 'silver': 220, 'gold': 385, 'legendary': 605 } },
    { 'id':  'arena-7',           'trophies': 2000, 'collection_win': { 'bronze': 100, 'silver': 200, 'gold': 350, 'legendary': 550 } },
    { 'id':  'arena-6',           'trophies': 1600, 'collection_win': { 'bronze': 90,  'silver': 180, 'gold': 315, 'legendary': 495 } },
    { 'id':  'arena-5',           'trophies': 1300, 'collection_win': { 'bronze': 80,  'silver': 160, 'gold': 280, 'legendary': 440 } },
    { 'id':  'arena-4',           'trophies': 1000, 'collection_win': { 'bronze': 70,  'silver': 140, 'gold': 245, 'legendary': 385 } },
    { 'id':  'arena-3',           'trophies':  600, 'collection_win': { 'bronze': 60,  'silver': 120, 'gold': 210, 'legendary': 330 } },
    { 'id':  'arena-2',           'trophies':  300, 'collection_win': { 'bronze': 50,  'silver': 100, 'gold': 175, 'legendary': 275 } },
    { 'id':  'arena-1',           'trophies':    0, 'collection_win': { 'bronze': 40,  'silver': 80,  'gold': 140, 'legendary': 220 } }
]

WAR_LEAGUE_LOOKUP = {
    0    : 'bronze',
    600  : 'silver',
    1500 : 'gold',
    3000 : 'legendary'
}

logger = logging.getLogger(__name__)

def get_arena_league_from_trophies(trophies):
    for league in ARENA_LEAGUES:
        if trophies >= league['trophies']:
            return league

def get_collection_win_cards(war_league, league):
    collection_win_lookup = league['collection_win']

    return collection_win_lookup[war_league]

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
    standing = war.standings

    clan_score = 0
    for clan in standing:
        if clan.clan.tag == clan_tag:
            clan_score = clan.clan.clan_score

    return get_war_league_from_score(clan_score)
