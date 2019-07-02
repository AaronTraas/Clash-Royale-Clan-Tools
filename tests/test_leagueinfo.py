from crtools import leagueinfo

def test_get_arena_league_from_name():
    # The below isn't comprehensive, nor specific. As the league makeup
    # are likely to change from time to time, no reason to update the
    # tests every time that happens.
    assert leagueinfo.get_arena_league_from_name('Arena 1')['id'] == 'arena-1'
    assert leagueinfo.get_arena_league_from_name('Legendary Arena')['id'] == 'challenger-1'
    assert leagueinfo.get_arena_league_from_name('Garbage League (obviously fake)')['id'] == 'arena-unknown'

def test_get_war_league_from_score():
    assert leagueinfo.get_war_league_from_score(200) == 'bronze'
    assert leagueinfo.get_war_league_from_score(1501) == 'gold'
    assert leagueinfo.get_war_league_from_score(99999999999999) == 'legendary'

def test_get_collection_win_cards():
    # The below isn't comprehensive, nor specific. It's mostly checking
    # if all the war leagues exist and if all the valid arena leagues
    # result in a > 1 value. As the league makeup and scoring rules
    # are likely to change from time to time, no reason to update the
    # tests every time that happens.
    arenas = [
        'Arena 1',
        'Arena 2',
        'Arena 3',
        'Arena 4',
        'Arena 5',
        'Arena 6',
        'Arena 7',
        'Arena 8',
        'Arena 9',
        'Arena 10',
        'Arena 11',
        'Arena 12',
        'Legendary Arena',
        'Challenger II',
        'Challenger III',
        'Master I',
        'Master II',
        'Master III',
        'Champion',
        'Grand Champion',
        'Ultimate Champion'
    ]

    for arena in arenas:
        for league in ['legendary', 'gold', 'silver', 'bronze']:
            assert leagueinfo.get_collection_win_cards(league, arena) > 1

    assert leagueinfo.get_collection_win_cards('silver', 'Garbage League (obviously fake)') == 1
