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
    assert leagueinfo.get_collection_win_cards('legendary', 'Arena 4') > 1
    assert leagueinfo.get_collection_win_cards('gold', 'Legendary Arena') > 1
    assert leagueinfo.get_collection_win_cards('silver', 'Arena 9') > 1
    assert leagueinfo.get_collection_win_cards('bronze', 'Arena 1') > 1
    assert leagueinfo.get_collection_win_cards('silver', 'Garbage League (obviously fake)') == 1
