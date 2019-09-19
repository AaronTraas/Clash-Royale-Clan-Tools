import pyroyale
from crtools import load_config_file
from crtools.models import ProcessedCurrentWar

CLAN_TAG = '#FakeClanTag'

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

def test_process_current_war_nowar():
    config = load_config_file(False)

    war = ProcessedCurrentWar(config=config, current_war=pyroyale.WarCurrent(state='notInWar'))

    assert war.state_label == 'The clan is not currently engaged in a war.'

def test_process_current_war_collection():
    config = load_config_file(False)

    war = ProcessedCurrentWar(config=config, current_war=pyroyale.WarCurrent(
        state               = 'collectionDay',
        collection_end_time = '20190209T212846.354Z',
        clan                = __fake_war_clan__,
        participants        = __fake_war_participants__
    ))

    assert war.collection_end_time
    assert war.end_label

def test_process_current_war_warday():
    config = load_config_file(False)

    war = ProcessedCurrentWar(config=config, current_war=pyroyale.WarCurrent(
        state        = 'warDay',
        war_end_time = '20190209T212846.354Z',
        clan         = __fake_war_clan__,
        participants = __fake_war_participants__,
        clans        = [__fake_war_clan__]
    ))

    assert war.state_label == 'War Day'
    assert war.collection_end_time_label == 'Complete'
    assert war.end_label
