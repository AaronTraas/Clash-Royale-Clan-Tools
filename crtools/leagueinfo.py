#!/usr/bin/python

"""Hardcoded data about arena and war leagues, and some functions
used to lookup specific data."""

__license__   = 'LGPLv3'
__docformat__ = 'reStructuredText'

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
    'Arena 13'      : { 'id':  'challenger-1',      'collection_win': { 'bronze': 160, 'silver': 320, 'gold': 560, 'legendary': 880 } },
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

def get_arena_league_from_name(league_name):
    if league_name in ARENA_LEAGUE_LOOKUP:
        return ARENA_LEAGUE_LOOKUP[league_name]
    else:
        return ARENA_LEAGUE_LOOKUP['Arena Unknown']

def get_collection_win_cards(war_league, arena_league_name):
    collection_win_lookup = get_arena_league_from_name(arena_league_name)['collection_win']

    return collection_win_lookup[war_league]

def get_war_league_from_score(clan_score):
    """ Figure out which war league a clan trophy count corresponds to,
    and return war league details. """
    league = 'ERROR'
    for score, lookup_table in WAR_LEAGUE_LOOKUP.items():
        if clan_score >= score:
            league = lookup_table

    return league
