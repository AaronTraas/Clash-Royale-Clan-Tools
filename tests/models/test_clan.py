import pyroyale
from crtools import load_config_file
from crtools.models import ProcessedClan
from crtools.models import ProcessedCurrentWar

CLAN_TAG = '#FakeClanTag'

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

__fake_clan__ = pyroyale.Clan(
    tag                = CLAN_TAG,
    name               = "Agrassar",
    description        = "Rules, stats, discord link, and info at https://agrassar.com",
    clan_score         = 38803,
    clan_war_trophies  = 1813,
    required_trophies  = 3000,
    donations_per_week = 7540,
    members            = 4,
    member_list        = [
        pyroyale.ClanMember(
            tag       = "#AAAAAA",
            name      = "LeaderPerson",
            role      = "leader",
            exp_level = 12,
            trophies  = 4153,
            donations = 300,
            last_seen = "20190802T154619.000Z"
        )
    ]
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

__fake_current_war__ = pyroyale.WarCurrent(
    state        = 'warDay',
    war_end_time = '20190209T212846.354Z',
    clan         = __fake_war_clan__,
    participants = [
        pyroyale.WarParticipant(
            tag                           =  '#AAAAAA',
            cards_earned                  = 1120,
            battles_played                = 1,
            wins                          = 1,
            number_of_battles             = 1,
            collection_day_battles_played = 3
        )
    ],
    clans        = [__fake_war_clan__]
)

def test_process_clan(tmpdir):
    config_file = tmpdir.mkdir('test_process_clan').join('testfile')
    config_file.write(__config_file_score__)
    config = load_config_file(config_file.realpath())

    clan = ProcessedClan(
        config=config,
        clan=__fake_clan__,
        current_war=ProcessedCurrentWar(config=config, current_war=__fake_current_war__)
    )

    assert clan.war_league == 'gold'
    assert clan.war_league_name == 'Gold League'
    assert clan.current_war_state == 'warDay'

