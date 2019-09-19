from datetime import datetime

import crtools
from crtools import crtools, load_config_file, history
from crtools.scorecalc import ScoreCalculator
import pyroyale

__config_file_score__ = '''
[activity]
threshold_kick=99999999
threshold_warn=99999999
[Score]
war_battle_incomplete=-30
war_battle_won=5
war_battle_lost=0
collect_battle_played=0
collect_battle_incomplete=-5
collect_battle_won=2
collect_battle_lost=0
war_participation=0
war_non_participation=-1
'''

__fake_member_list__ = [
    pyroyale.ClanMember(
        tag       = "#AAAAAA",
        name      = "LeaderPerson",
        role      = "leader",
        exp_level = 12,
        trophies  = 4153,
        donations = 300,
        arena     = pyroyale.Arena(
            id    = 54000012,
            name  = 'Legendary Arena'
        ),
        last_seen = "20190802T154619.000Z"
    ),
    pyroyale.ClanMember(
        tag       = "#BBBBBB",
        name      = "CoLeaderPerson",
        role      = "coLeader",
        exp_level = 12,
        trophies  = 4418,
        donations = 150,
        arena     = pyroyale.Arena(
            id    = 54000013,
            name  = 'Arena 12'
        ),
        last_seen = "20190802T154619.000Z"
    ),
    pyroyale.ClanMember(
        tag       = "#CCCCCC",
        name      = "ElderPerson",
        role      = "elder",
        exp_level = 12,
        trophies  = 4224,
        donations = 0,
        arena     = pyroyale.Arena(
            id    = 54000012,
            name  = 'Legendary Arena'
        ),
        last_seen = "20190802T154619.000Z"
    ),
    pyroyale.ClanMember(
        tag       = "#DDDDDD",
        name      = "MemberPerson",
        role      = "member",
        exp_level = 8,
        trophies  = 3100,
        donations = 0,
        arena     = pyroyale.Arena(
            id    = 54000008,
            name  = 'Arena 7'
        ),
        last_seen = "20190802T154619.000Z"
    ),
    pyroyale.ClanMember(
        tag       = "#EEEEEE",
        name      = "MemberPersonToBePromoted",
        role      = "member",
        exp_level = 8,
        trophies  = 3144,
        donations = 100000000,
        arena     = pyroyale.Arena(
            id    = 54000008,
            name  = 'Arena 7'
        ),
        last_seen = "20190802T154619.000Z"
    )

]

def test_war_score(tmpdir):
    war_complete = {
        "battles_played": 1,
        "wins": 1,
        "collection_day_battles_played": 3,
        "collectionBattleWins": 2,
        "collectionBattleLosses": 0,
        "status": "na"
    }
    war_incomplete = {
        "battles_played": 0,
        "wins": 0,
        "collection_day_battles_played": 3,
        "collectionBattleWins": 2,
        "collectionBattleLosses": 0,
        "status": "na"
    }
    war_na = {"status": "na"}
    war_new = {"status": "not-in-clan"}

    config_file = tmpdir.mkdir('test_war_score').join('testfile')
    config_file.write(__config_file_score__)
    config = load_config_file(config_file.realpath())

    assert ScoreCalculator(config).get_war_score(war_complete)   == 24
    assert ScoreCalculator(config).get_war_score(war_incomplete) == -26
    assert ScoreCalculator(config).get_war_score(war_na)         == -1
    assert ScoreCalculator(config).get_war_score(war_new)        == 0

def test_donations_score(tmpdir):
    config_file = tmpdir.mkdir('test_donations_score').join('testfile')
    config_file.write(__config_file_score__)
    config = load_config_file(config_file.realpath())

    date = datetime(2019, 2, 12, 7, 32, 1, 0)
    timestamp = datetime.timestamp(date)
    members = history.get_member_history(__fake_member_list__, {"last_update": 0,"members": ""}, None, date)["members"]

    member_tag_0 = __fake_member_list__[0].tag
    member_6 = crtools.enrich_member_with_history(config, __fake_member_list__[0].to_dict(), members, 6, date)
    member_3 = crtools.enrich_member_with_history(config, __fake_member_list__[0].to_dict(), members, 3, date)
    member_0 = crtools.enrich_member_with_history(config, __fake_member_list__[0].to_dict(), members, 0, date)

    assert ScoreCalculator(config).get_member_donations_score(member_6) == 11
    assert ScoreCalculator(config).get_member_donations_score(member_3) == 18
    assert ScoreCalculator(config).get_member_donations_score(member_0) == 31
