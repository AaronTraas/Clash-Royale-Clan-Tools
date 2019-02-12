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

__fake_clan__ = {
    "tag": CLAN_TAG,
    "name": "Agrassar",
    "description": "Rules, stats, discord link, and info at https://agrassar.com",
    "clanScore": 38803,
    "clanWarTrophies": 1813,
    "requiredTrophies": 3000,
    "donationsPerWeek": 7540,
    "members": 4,
    "memberList": [
        {
            "tag": "#AAAAAA",
            "name": "LeaderPerson",
            "role": "leader",
            "expLevel": 12,
            "trophies": 4153,
            "arena": {
                "id": 54000012,
                "name": "Arena 13"
            },
            "clanRank": 6,
            "previousClanRank": 3,
            "donations": 97,
            "donationsReceived": 240,
            "clanChestPoints": 11
        },
        {
            "tag": "#BBBBBB",
            "name": "CoLeaderPerson",
            "role": "coLeader",
            "expLevel": 13,
            "trophies": 4418,
            "arena": {
                "id": 54000013,
                "name": "League 2"
            },
            "clanRank": 1,
            "previousClanRank": 1,
            "donations": 648,
            "donationsReceived": 550,
            "clanChestPoints": 72
        },
        {
            "tag": "#CCCCCC",
            "name": "ElderPerson",
            "role": "elder",
            "expLevel": 12,
            "trophies": 4224,
            "arena": {
                "id": 54000012,
                "name": "Arena 13"
            },
            "clanRank": 2,
            "previousClanRank": 2,
            "donations": 142,
            "donationsReceived": 200
        },
        {
            "tag": "#DDDDDD",
            "name": "MemberPerson",
            "role": "member",
            "expLevel": 8,
            "trophies": 2144,
            "arena": {
                "id": 54000008,
                "name": "Arena 7"
            },
            "clanRank": 45,
            "previousClanRank": 44,
            "donations": 16,
            "donationsReceived": 0
        }
    ]
}

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

__fake_currentwar__ = {
    "state": "warDay",
    "warEndTime": "20190209T212846.354Z",
    "clan": {
        "tag": CLAN_TAG,
        "name": "Agrassar",
        "clanScore": 1813,
        "participants": 17,
        "battlesPlayed": 13,
        "wins": 1,
        "crowns": 5
    },
    "participants": [
        {
            "tag": "#9ULGLRCL",
            "name": "AaronTraas",
            "cardsEarned": 1120,
            "battlesPlayed": 1,
            "wins": 1,
            "collectionDayBattlesPlayed": 3
        }
    ],
    "clans": [
        {
            "tag": CLAN_TAG,
            "name": "Agrassar",
            "clanScore": 1813,
            "participants": 17,
            "battlesPlayed": 13,
            "wins": 5,
            "crowns": 12,
            "battlesRemaining": 4
        },
    ]
}

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

def test_get_collection_win_cards():
    assert crtools.get_collection_win_cards('gold', 'League 2') == 560
    assert crtools.get_collection_win_cards('silver', 'League 2') == 320
    assert crtools.get_collection_win_cards('silver', 'Garbage League (obviously fake)') == 1

def test_get_member_war_status_class():
    assert crtools.get_member_war_status_class(0, 0) == 'na'
    assert crtools.get_member_war_status_class(3, 0) == 'bad'
    assert crtools.get_member_war_status_class(2, 1) == 'ok'
    assert crtools.get_member_war_status_class(3, 1) == 'good'
    assert crtools.get_member_war_status_class(3, 0, True) == 'normal incomplete'
    assert crtools.get_member_war_status_class(2, 0, True) == 'ok incomplete'
    assert crtools.get_member_war_status_class(2, 0, True, True) == 'ok incomplete'
    assert crtools.get_member_war_status_class(2, 1, True, True) == 'ok'
    assert crtools.get_member_war_status_class(3, 1, True, True) == 'good'

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

def test_process_clan(tmpdir):
    config_file = tmpdir.mkdir('test_process_clan').join('testfile')
    config_file.write(__config_file_score__)
    config = load_config_file(config_file.realpath())

    processed_clan = crtools.process_clan(config, __fake_clan__, __fake_currentwar__)

    assert 'memberList' not in processed_clan
    assert processed_clan['warLeague'] == 'gold'
    assert processed_clan['warLeagueName'] == 'Gold League'
    assert processed_clan['currentWarState'] == 'warDay'


def test_process_current_war_nowar():
    config = load_config_file(False)

    processed_current_war = crtools.process_current_war(config, {"state": "notInWar"})

    assert processed_current_war['stateLabel'] == 'The clan is not currently engaged in a war.'

def test_process_current_war_collection():
    config = load_config_file(False)

    currentwar = __fake_currentwar__.copy()
    currentwar['state'] = 'collectionDay'
    currentwar['collectionEndTime'] = currentwar['warEndTime']
    processed_current_war = crtools.process_current_war(config, currentwar)

    assert 'collectionEndTimeLabel' in processed_current_war
    assert 'endLabel' in processed_current_war

def test_process_current_war_warday():
    config = load_config_file(False)

    processed_current_war = crtools.process_current_war(config, __fake_currentwar__)

    assert processed_current_war['cards'] == 1120
    assert processed_current_war['stateLabel'] == 'War Day'
    assert processed_current_war['collectionEndTimeLabel'] == 'Complete'
    assert 'endLabel' in processed_current_war

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

    config_file = tmpdir.mkdir('test_war_score').join('testfile')
    config_file.write(__config_file_score__)
    config = load_config_file(config_file.realpath())

    assert crtools.war_score(config, war_complete)   == 24
    assert crtools.war_score(config, war_incomplete) == -26
    assert crtools.war_score(config, war_na)         == -1

def test_process_recent_wars(tmpdir):
    config_file = tmpdir.mkdir('test_process_recent_wars').join('config.ini')
    config_file.write(__config_file__)

    config = load_config_file(config_file.realpath())

    processed_warlog = crtools.process_recent_wars(config, __fake_warlog__)

    assert processed_warlog[0]['tag'] == CLAN_TAG
    assert processed_warlog[0]['rank'] == 1
    assert processed_warlog[0]['date'] == '2/3'
    assert processed_warlog[0]['trophyChange'] == 999
