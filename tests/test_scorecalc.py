from datetime import datetime

import crtools
from crtools import crtools, load_config_file, history
from crtools import MemberFactory
from crtools.models import ProcessedCurrentWar, ProcessedMember, WarParticipation
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

CLAN_TAG = '#FakeClanTag'

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

__fake_clan__ = pyroyale.Clan(
    tag                = CLAN_TAG,
    name               = "Agrassar",
    description        = "Rules, stats, discord link, and info at https://agrassar.com",
    clan_score         = 38803,
    clan_war_trophies  = 1813,
    required_trophies  = 3000,
    donations_per_week = 7540,
    members            = 4,
    member_list        = __fake_member_list__
)

__fake_war_clan__ = pyroyale.WarClan(
        tag = CLAN_TAG,
        name = "Agrassar",
        clan_score = 1813,
        participants = 17,
        battles_played = 13,
        battles_remaining = 0,
        wins = 1,
        crowns = 5
    )

__fake_war_participants__ = [
    pyroyale.WarParticipant(
        tag                           =  '#AAAAAA',
        cards_earned                  = 1120,
        battles_played                = 1,
        wins                          = 1,
        number_of_battles             = 1,
        collection_day_battles_played = 3
    ),
    pyroyale.WarParticipant(
        tag                           =  '#BBBBBB',
        cards_earned                  = 1120,
        battles_played                = 1,
        wins                          = 1,
        number_of_battles             = 1,
        collection_day_battles_played = 1
    ),
    pyroyale.WarParticipant(
        tag                           =  '#CCCCCC',
        cards_earned                  = 1120,
        battles_played                = 0,
        wins                          = 1,
        number_of_battles             = 1,
        collection_day_battles_played = 1
    )
]

__fake_current_war__ = pyroyale.WarCurrent(
        state        = 'warDay',
        war_end_time = '20190209T212846.354Z',
        clan         = __fake_war_clan__,
        participants = __fake_war_participants__,
        clans        = [__fake_war_clan__]
    )

def test_war_score(tmpdir):

    config_file = tmpdir.mkdir('test_war_score').join('testfile')
    config_file.write(__config_file_score__)
    config = load_config_file(config_file.realpath())

    calc = ScoreCalculator(config)

    war_complete = ProcessedCurrentWar(config=config, current_war=__fake_current_war__)
    war_complete.status = 'na'
    war_complete.battles_played = 1
    war_complete.wins = 1
    war_complete.collection_day_battles_played = 3
    war_complete.collection_battle_wins = 2
    war_complete.collection_battle_losses = 0
    assert calc.get_war_score(war_complete)   == 24

    war_incomplete = ProcessedCurrentWar(config=config, current_war=__fake_current_war__)
    war_incomplete.status = 'na'
    war_incomplete.battles_played = 0
    war_incomplete.wins = 0
    war_incomplete.collection_day_battles_played = 3
    war_incomplete.collection_battle_wins = 2
    war_incomplete.collection_battle_losses = 0
    assert calc.get_war_score(war_incomplete) == -26

    war_na = WarParticipation(config=config, member=__fake_war_participants__[0], war=__fake_current_war__)
    war_na.status = 'na'
    assert calc.get_war_score(war_na)         == -1

    war_new = WarParticipation(config=config, member=__fake_war_participants__[0], war=__fake_current_war__)
    war_new.status = 'not-in-clan'
    assert calc.get_war_score(war_new)        == 0

def test_donations_score(tmpdir):
    config_file = tmpdir.mkdir('test_donations_score').join('testfile')
    config_file.write(__config_file_score__)
    config = load_config_file(config_file.realpath())

    calc = ScoreCalculator(config)

    war = ProcessedCurrentWar(config=config, current_war=pyroyale.WarCurrent(state='notInWar'))
    member_history = history.get_member_history(__fake_member_list__, '{}', war)
    date = datetime(2019, 2, 12, 7, 32, 1, 0)

    member_6 = MemberFactory(config=config, current_war=war, clan=__fake_clan__, member_history=member_history, warlog=pyroyale.WarLog(items=[]), days_from_donation_reset=6, now=date).get_processed_member(__fake_member_list__[0])
    member_3 = MemberFactory(config=config, current_war=war, clan=__fake_clan__, member_history=member_history, warlog=pyroyale.WarLog(items=[]), days_from_donation_reset=3, now=date).get_processed_member(__fake_member_list__[0])
    member_0 = MemberFactory(config=config, current_war=war, clan=__fake_clan__, member_history=member_history, warlog=pyroyale.WarLog(items=[]), days_from_donation_reset=0, now=date).get_processed_member(__fake_member_list__[0])

    assert calc.get_member_donations_score(member_6) == 11
    assert calc.get_member_donations_score(member_3) == 18
    assert calc.get_member_donations_score(member_0) == 31

