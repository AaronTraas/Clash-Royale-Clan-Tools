from crtools import leagueinfo

def test_get_arena_league_from_trophies():
    assert leagueinfo.get_arena_league_from_trophies(200)['id'] == 'arena-1'
    assert leagueinfo.get_arena_league_from_trophies(4001)['id'] == 'challenger-1'
    assert leagueinfo.get_arena_league_from_trophies(99999999999999)['id'] == 'ultimate-champion'

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

    for arena in leagueinfo.ARENA_LEAGUES:
        for league in ['legendary', 'gold', 'silver', 'bronze']:
            assert leagueinfo.get_collection_win_cards(league, arena) > 1
