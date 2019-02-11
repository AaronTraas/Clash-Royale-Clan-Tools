import json
import os
import shutil
from crtools import crtools, load_config_file

CLAN_TAG = '#FakeClanTag'

__config_file__ = '''
[api]
clan_id={}
'''.format(CLAN_TAG)

__config_file_score__ = '''
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

__fake_warlog__ = [
    {
        "createdDate": "20190203T163246.000Z",
        "participants": [
            {
                "tag": "#FFFFFF",
                "name": "Fake Player",
                "cardsEarned": 560,
                "battlesPlayed": 1,
                "wins": 1,
                "collectionDayBattlesPlayed": 3
            }
        ],
        "standings": [
            {
                "clan": {
                    "tag": CLAN_TAG,
                    "clanScore": 1000
                },
                "trophyChange": 999
            }
        ]
    }
]

def test_write_object_to_file(tmpdir):
    config_file = tmpdir.mkdir('test_write_object_to_file').join('testfile')

    file_path = config_file.realpath()
    file_contents_text = 'hello world!'
    file_contents_object = {'foo': 'bar'}

    crtools.write_object_to_file(file_path, file_contents_text)

    with open(file_path, 'r') as myfile:
        file_out_contents = myfile.read()

    assert file_contents_text == file_out_contents

    crtools.write_object_to_file(file_path, file_contents_object)

    with open(file_path, 'r') as myfile:
        file_out_contents = myfile.read()

    assert file_contents_object == json.loads(file_out_contents)

def test_get_war_league_from_score():
    assert crtools.get_war_league_from_score(200)['name'] == 'Bronze League'
    assert crtools.get_war_league_from_score(1501)['name'] == 'Gold League'
    assert crtools.get_war_league_from_score(99999999999999)['name'] == 'Legendary League'

def test_warlog_labels(tmpdir):
    labels = crtools.warlog_labels(__fake_warlog__, CLAN_TAG)

    assert labels[0]['date'] == '2/3'
    assert labels[0]['league']['name'] == 'Silver League'

def test_get_scoring_rules(tmpdir):
    config_file = tmpdir.mkdir('test_write_object_to_file').join('testfile')
    config_file.write(__config_file_score__)
    config = load_config_file(config_file.realpath())

    rules = crtools.get_scoring_rules(config)

    assert rules[0]['yes']          == 0
    assert rules[0]['no']           == -1
    assert rules[0]['yes_status']   == 'normal'
    assert rules[0]['no_status']    == 'bad'
    assert rules[1]['yes']          == 0
    assert rules[1]['no']           == -5
    assert rules[1]['yes_status']   == 'normal'
    assert rules[1]['no_status']    == 'bad'
    assert rules[2]['yes']          == 2
    assert rules[2]['no']           == 0
    assert rules[2]['yes_status']   == 'good'
    assert rules[2]['no_status']    == 'normal'
    assert rules[3]['yes']          == 15
    assert rules[3]['no']           == -30
    assert rules[3]['yes_status']   == 'good'
    assert rules[3]['no_status']    == 'bad'
    assert rules[4]['yes']          == 5
    assert rules[4]['no']           == 0
    assert rules[4]['yes_status']   == 'good'
    assert rules[4]['no_status']    == 'normal'

def test_war_score(tmpdir):
    # FIXME -- should replace once we test crtools.process_members()
    war_complete = {
        "battlesPlayed": 1,
        "wins": 1,
        "collectionDayBattlesPlayed": 3,
        "collectionBattleWins": 2,
        "collectionBattleLosses": 0
    }
    war_incomplete = {
        "battlesPlayed": 0,
        "wins": 0,
        "collectionDayBattlesPlayed": 3,
        "collectionBattleWins": 2,
        "collectionBattleLosses": 0
    }
    war_na = {}

    config_file = tmpdir.mkdir('test_write_object_to_file').join('testfile')
    config_file.write(__config_file_score__)
    config = load_config_file(config_file.realpath())

    assert crtools.war_score(config, war_complete)   == 24
    assert crtools.war_score(config, war_incomplete) == -26
    assert crtools.war_score(config, war_na)         == -1

def test_process_recent_wars(tmpdir):
    config_file = tmpdir.mkdir('test_config_boolean').join('config.ini')
    config_file.write(__config_file__)

    config = load_config_file(config_file.realpath())

    processed_warlog = crtools.process_recent_wars(config, __fake_warlog__)

    assert processed_warlog[0]['tag'] == CLAN_TAG
    assert processed_warlog[0]['rank'] == 1
    assert processed_warlog[0]['date'] == '2/3'
    assert processed_warlog[0]['trophyChange'] == 999
