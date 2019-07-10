from datetime import datetime, timedelta
import copy
import os
import shutil

from crtools import crtools, load_config_file, history

CLAN_TAG = '#FakeClanTag'

__config_file__ = '''
[api]
clan_id={}
'''.format(CLAN_TAG)

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

__config_file_score_thresholds__ = '''
[Score]
threshold_promote=100
threshold_warn=10
'''

__config_file_score_donations__ = '''
[Score]
max_donations_bonus=40
min_donations_daily=10
'''

__fake_history__ = {
    "last_update": 0,
    "members": ""
}

__fake_history_old_member__ = {
    "last_update": 0,
    "members": {
        "#ZZZZZZ": {
            "join_date": 1549974720.0,
            "status": "present",
            "role": "leader",
            "donations": 100,
            "events": [
                {
                    "event": "join",
                    "status": "new",
                    "role": "leader",
                    "date": 1549974720.0
                }
            ]
        }
    }

}

__fake_clan__ = {
    "tag": CLAN_TAG,
    "name": "Agrassar",
    "description": "Rules, stats, discord link, and info at https://agrassar.com",
    "clan_score": 38803,
    "clan_war_trophies": 1813,
    "required_trophies": 3000,
    "donations_per_week": 7540,
    "members": 4,
    "member_list": [
        {
            "tag": "#AAAAAA",
            "name": "LeaderPerson",
            "role": "leader",
            "expLevel": 12,
            "trophies": 4153,
            "donations": 300,
            "arena": {
                "id": 54000012,
                "name": "Legendary Arena"
            },
            "join_date": 0
        },
        {
            "tag": "#BBBBBB",
            "name": "CoLeaderPerson",
            "role": "coLeader",
            "expLevel": 13,
            "trophies": 4418,
            "donations": 150,
            "arena": {
                "id": 54000013,
                "name": "Arena 12"
            },
            "join_date": 0
        },
        {
            "tag": "#CCCCCC",
            "name": "ElderPerson",
            "role": "elder",
            "expLevel": 12,
            "trophies": 4224,
            "donations": 0,
            "arena": {
                "id": 54000012,
                "name": "Legendary Arena"
            },
            "join_date": 0
        },
        {
            "tag": "#DDDDDD",
            "name": "MemberPerson",
            "role": "member",
            "expLevel": 8,
            "trophies": 3100,
            "donations": 0,
            "arena": {
                "id": 54000008,
                "name": "Arena 7"
            },
            "join_date": 0
        },
        {
            "tag": "#EEEEEE",
            "name": "MemberPersonToBePromoted",
            "role": "member",
            "expLevel": 8,
            "trophies": 3144,
            "donations": 100000000,
            "arena": {
                "id": 54000008,
                "name": "Arena 7"
            },
            "join_date": 0
        }
    ]
}

__fake_warlog__ = {
    "items": [
        {
            "created_date": "20190203T163246.000Z",
            "participants": [
                {
                    "tag": "#AAAAAA",
                    "cards_earned": 1120,
                    "battles_played": 1,
                    "wins": 1,
                    "collection_day_battles_played": 3
                }
            ],
            "standings": [
                {
                    "clan": {
                        "tag": CLAN_TAG,
                        "clan_score": 1000
                    },
                    "trophy_change": 999
                }
            ]
        }
    ]
}

__fake_war_base__ = {
    "clan": {
        "tag": CLAN_TAG,
        "name": "Agrassar",
        "clan_score": 1813,
        "participants": 17,
        "battles_played": 13,
        "wins": 1,
        "crowns": 5
    },
    "participants": [
        {
            "tag": "#AAAAAA",
            "cards_earned": 1120,
            "battles_played": 1,
            "wins": 1,
            "collection_day_battles_played": 3
        },
        {
            "tag": "#BBBBBB",
            "cards_earned": 1120,
            "battles_played": 1,
            "wins": 1,
            "collection_day_battles_played": 1
        },
        {
            "tag": "#CCCCCC",
            "cards_earned": 1120,
            "battles_played": 0,
            "wins": 1,
            "collection_day_battles_played": 1
        }
    ]
}

__fake_war__ = __fake_war_base__.copy()
__fake_war__['created_date'] = '20190209T212846.354Z'
__fake_war__['standings'] = [
    {
        "clan": {
            "tag": CLAN_TAG,
            "clan_score": 2428,
            "participants": 19,
            "battles_played": 20,
            "wins": 11,
            "crowns": 22
        },
        "trophy_change": 111
    }
]

__fake_currentwar_warday__ = __fake_war_base__.copy()
__fake_currentwar_warday__['state'] = 'warDay'
__fake_currentwar_warday__['war_end_time'] = '20190209T212846.354Z'
__fake_currentwar_warday__['clans'] = [
    {
        "tag": CLAN_TAG,
        "name": "Agrassar",
        "clan_score": 1813,
        "participants": 17,
        "battles_played": 13,
        "wins": 5,
        "crowns": 12,
        "battlesRemaining": 4
    }
]

__fake_currentwar_collectionday__ = __fake_war_base__.copy()
__fake_currentwar_collectionday__['state'] = 'collectionDay'
__fake_currentwar_collectionday__['collection_end_time'] = '20190209T212846.354Z'

def test_get_member_war_status_class():
    assert crtools.get_member_war_status_class(0, 0, 0, 1) == 'not-in-clan'
    assert crtools.get_member_war_status_class(0, 0, 0, 0) == 'na'
    assert crtools.get_member_war_status_class(3, 0, 0, 0) == 'bad'
    assert crtools.get_member_war_status_class(2, 1, 0, 0) == 'ok'
    assert crtools.get_member_war_status_class(3, 1, 0, 0) == 'good'
    assert crtools.get_member_war_status_class(3, 0, 0, 0, True) == 'normal incomplete'
    assert crtools.get_member_war_status_class(2, 0, 0, 0, True) == 'ok incomplete'
    assert crtools.get_member_war_status_class(2, 0, 0, 0, True, True) == 'ok incomplete'
    assert crtools.get_member_war_status_class(2, 1, 0, 0, True, True) == 'ok'
    assert crtools.get_member_war_status_class(3, 1, 0, 0, True, True) == 'good'

def test_get_war_date():
    raw_date_string = '20190213T000000.000Z'
    test_date = datetime.strptime(raw_date_string.split('.')[0], '%Y%m%dT%H%M%S')
    assert crtools.get_war_date({'created_date': raw_date_string}) == datetime.timestamp(test_date - timedelta(days=1))
    assert crtools.get_war_date({'state': 'warDay', 'war_end_time': raw_date_string}) == datetime.timestamp(test_date - timedelta(days=2))
    assert crtools.get_war_date({'state': 'collectionDay', 'collection_end_time': raw_date_string}) == datetime.timestamp(test_date - timedelta(days=1))

def test_member_war(tmpdir):
    config_file = tmpdir.mkdir('test_member_war').join('testfile')
    config_file.write(__config_file_score__)
    config = load_config_file(config_file.realpath())

    war_current_nowar = crtools.member_war(
        config,
        __fake_clan__['member_list'][0],
        {'state': 'notInWar'}
    )
    assert war_current_nowar['status'] == 'na'
    assert war_current_nowar['score'] == 0

    war_current_isparticipating = crtools.member_war(
        config,
        __fake_clan__['member_list'][0],
        __fake_currentwar_warday__
    )
    assert war_current_isparticipating['status'] == 'good'
    assert war_current_isparticipating['score'] == 0

    war_current_notparticipating = crtools.member_war(
        config,
        __fake_clan__['member_list'][3],
        __fake_currentwar_warday__
    )
    assert war_current_notparticipating['status'] == 'na'
    assert war_current_notparticipating['score'] == 0

    war_isparticipating_good = crtools.member_war(
        config,
        __fake_clan__['member_list'][0],
        __fake_war__
    )
    assert war_isparticipating_good['status'] == 'good'
    assert war_isparticipating_good['score'] == 34

    war_isparticipating_ok = crtools.member_war(
        config,
        __fake_clan__['member_list'][1],
        __fake_war__
    )
    print(__fake_clan__['member_list'][1]['arena'])
    assert war_isparticipating_ok['status'] == 'ok'
    assert war_isparticipating_ok['score'] == 24

    war_isparticipating_bad = crtools.member_war(
        config,
        __fake_clan__['member_list'][2],
        __fake_war__
    )
    assert war_isparticipating_bad['status'] == 'bad'
    assert war_isparticipating_bad['score'] == -26

    war_notparticipating = crtools.member_war(
        config,
        __fake_clan__['member_list'][3],
        __fake_war__
    )
    assert war_notparticipating['status'] == 'na'
    assert war_notparticipating['score'] == -1

def test_member_warlog(tmpdir):
    config_file = tmpdir.mkdir('test_member_warlog').join('testfile')
    config_file.write(__config_file_score__)
    config = load_config_file(config_file.realpath())

    warlog = crtools.member_warlog(config, __fake_clan__['member_list'][0], __fake_warlog__)
    assert warlog[0]['status'] == 'good'

    warlog = crtools.member_warlog(config, __fake_clan__['member_list'][1], __fake_warlog__)
    assert warlog[0]['status'] == 'na'

def test_donations_score(tmpdir):
    config_file = tmpdir.mkdir('test_donations_score').join('testfile')
    config_file.write(__config_file_score__)
    config = load_config_file(config_file.realpath())

    date = datetime(2019, 2, 12, 7, 32, 1, 0)
    timestamp = datetime.timestamp(date)
    members = history.get_member_history(__fake_clan__['member_list'], __fake_history__, None, date)["members"]

    member_tag_0 = __fake_clan__['member_list'][0]['tag']
    member_6 = crtools.enrich_member_with_history(config, __fake_clan__['member_list'][0], members, 6, date)
    member_3 = crtools.enrich_member_with_history(config, __fake_clan__['member_list'][0], members, 3, date)
    member_0 = crtools.enrich_member_with_history(config, __fake_clan__['member_list'][0], members, 0, date)

    assert crtools.donations_score(config, member_6) == 11
    assert crtools.donations_score(config, member_3) == 18
    assert crtools.donations_score(config, member_0) == 31

def test_get_scoring_rules(tmpdir):
    config_file = tmpdir.mkdir('test_get_scoring_rules').join('testfile')
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

def test_get_suggestions_recruit(tmpdir):
    config_file = tmpdir.mkdir('test_get_suggestions').join('testfile')
    config_file.write(__config_file_score__ + '\nthreshold_demote=-999999\nthreshold_promote=9999999')
    config = load_config_file(config_file.realpath())

    h = history.get_member_history(__fake_clan__['member_list'], None)

    members = crtools.process_members(config, __fake_clan__, __fake_warlog__, {"state": "notInWar"}, h)

    suggestions = crtools.get_suggestions(config, members, __fake_clan__)

    print(suggestions)

    assert len(suggestions) == 1
    assert suggestions[0] == config['strings']['suggestionRecruit']

def test_process_absent_members(tmpdir):
    config_file = tmpdir.mkdir('test_get_suggestions').join('testfile')
    config_file.write(__config_file_score__ + '\nthreshold_demote=-999999\nthreshold_promote=9999999')
    config = load_config_file(config_file.realpath())

    h = history.get_member_history(__fake_clan__['member_list'], __fake_history_old_member__)

    absent_members = crtools.process_absent_members(config, h['members'])

    assert len(absent_members) == 1
    assert absent_members[0]['tag'] == '#ZZZZZZ'

def test_get_suggestions_nosuggestions(tmpdir):
    config_file = tmpdir.mkdir('test_get_suggestions').join('testfile')
    config_file.write(__config_file_score__ + '\nthreshold_demote=-999999\nthreshold_promote=9999999\nmin_clan_size={}'.format(crtools.MAX_CLAN_SIZE))
    config = load_config_file(config_file.realpath())

    members = []
    for i in range(0, crtools.MAX_CLAN_SIZE):
        members.append({
            "role": "leader",
            "trophies": 9999,
            "donations": 999,
            "score": 999,
            "vacation": False,
            "safe": True,
            "blacklist": False,
            "no_promote": False
        })

    suggestions = crtools.get_suggestions(config, members, __fake_clan__)

    assert len(suggestions) == 1
    assert suggestions[0] == config['strings']['suggestionNone']

def test_get_suggestions_kick(tmpdir):
    config_file = tmpdir.mkdir('test_get_suggestions').join('testfile')
    config_file.write(__config_file_score__ + '\nmin_clan_size=1')
    config = load_config_file(config_file.realpath())

    h = history.get_member_history(__fake_clan__['member_list'], None)

    members = crtools.process_members(config, __fake_clan__, __fake_warlog__, {"state": "notInWar"}, h)

    suggestions = crtools.get_suggestions(config, members, __fake_clan__)

    print(suggestions)

    assert suggestions[0].startswith('Kick')
    assert members[3]['name'] in suggestions[0]

def test_get_suggestions_promote_demote(tmpdir):
    config_file = tmpdir.mkdir('test_get_suggestions').join('testfile')
    config_file.write(__config_file_score__ + '\nthreshold_promote=10')
    config = load_config_file(config_file.realpath())

    h = history.get_member_history(__fake_clan__['member_list'], None)

    members = crtools.process_members(config, __fake_clan__, __fake_warlog__, {"state": "notInWar"}, h)

    suggestions = crtools.get_suggestions(config, members, __fake_clan__)

    print(suggestions)

    assert suggestions[0].startswith('Demote')
    assert members[2]['name'] in suggestions[0]
    assert suggestions[1].startswith('Promote') or suggestions[2].startswith('Promote')
    assert members[4]['name'] in suggestions[1] or members[4]['name'] in suggestions[2]

def test_process_clan(tmpdir):
    config_file = tmpdir.mkdir('test_process_clan').join('testfile')
    config_file.write(__config_file_score__)
    config = load_config_file(config_file.realpath())

    processed_clan = crtools.process_clan(config, __fake_clan__, __fake_currentwar_warday__)

    assert 'member_list' not in processed_clan
    assert processed_clan['warLeague'] == 'gold'
    assert processed_clan['warLeagueName'] == 'Gold League'
    assert processed_clan['currentWarState'] == 'warDay'

def test_process_current_war_nowar():
    config = load_config_file(False)

    processed_current_war = crtools.process_current_war(config, {"state": "notInWar"})

    assert processed_current_war['stateLabel'] == 'The clan is not currently engaged in a war.'

def test_process_current_war_collection():
    config = load_config_file(False)

    processed_current_war = crtools.process_current_war(config, __fake_currentwar_collectionday__)

    assert 'collectionEndTimeLabel' in processed_current_war
    assert 'endLabel' in processed_current_war

def test_process_current_war_warday():
    config = load_config_file(False)

    processed_current_war = crtools.process_current_war(config, __fake_currentwar_warday__)

    assert processed_current_war['stateLabel'] == 'War Day'
    assert processed_current_war['collectionEndTimeLabel'] == 'Complete'
    assert 'endLabel' in processed_current_war

def test_war_score(tmpdir):
    # FIXME: should replace once we test crtools.process_members()
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

    assert crtools.war_score(config, war_complete)   == 24
    assert crtools.war_score(config, war_incomplete) == -26
    assert crtools.war_score(config, war_na)         == -1
    assert crtools.war_score(config, war_new)        == 0

def test_process_recent_wars(tmpdir):
    config_file = tmpdir.mkdir('test_process_recent_wars').join('config.ini')
    config_file.write(__config_file__)

    config = load_config_file(config_file.realpath())

    processed_warlog = crtools.process_recent_wars(config, __fake_warlog__)

    assert processed_warlog[0]['clan']['tag'] == CLAN_TAG
    assert processed_warlog[0]['rank'] == 1
    assert processed_warlog[0]['date'] == '2/3'
    assert processed_warlog[0]['trophy_change'] == 999

def test_calc_activity_status():
    config = load_config_file(False)

    assert crtools.calc_activity_status(config, 0) == 'good'
    assert crtools.calc_activity_status(config, -1) == 'good'
    assert crtools.calc_activity_status(config, 1) == 'na'
    assert crtools.calc_activity_status(config, 3) == 'normal'
    assert crtools.calc_activity_status(config, 7) == 'ok'
    assert crtools.calc_activity_status(config, 400) == 'bad'

def test_calc_member_status(tmpdir):
    config_file = tmpdir.mkdir('test_calc_member_status').join('config.ini')
    config_file.write(__config_file_score_thresholds__)
    config = load_config_file(config_file.realpath())

    assert crtools.calc_member_status(config, -1, False)  == 'bad'
    assert crtools.calc_member_status(config, 5, False)   == 'ok'
    assert crtools.calc_member_status(config, 10, False)  == 'normal'
    assert crtools.calc_member_status(config, 100, False) == 'good'
    assert crtools.calc_member_status(config, 100, True)  == 'normal'

def test_calc_donation_status(tmpdir):
    config_file = tmpdir.mkdir('test_calc_donation_status').join('config.ini')
    config_file.write(__config_file_score_donations__)
    config = load_config_file(config_file.realpath())

    assert crtools.calc_donation_status(config, 1000, 100, 6) == 'good'
    assert crtools.calc_donation_status(config, 0, 0, 6) == 'bad'
    assert crtools.calc_donation_status(config, 0, 5, 6) == 'ok'
    assert crtools.calc_donation_status(config, 0, 0, 0) == 'normal'

def test_get_role_label():
    config = load_config_file(False)

    assert crtools.get_role_label(config, 'member', 0, 'good', False, True, False) == config['strings']['roleBlacklisted']
    assert crtools.get_role_label(config, 'leader', 100, 'bad', True, True, False) == config['strings']['roleBlacklisted']
    assert crtools.get_role_label(config, 'leader', 100, 'bad', True, False, False) == config['strings']['roleVacation']
    assert crtools.get_role_label(config, 'leader', 100, 'bad', False, False, False) == config['strings']['roleInactive'].format(days=100)

    assert crtools.get_role_label(config, 'leader', 0, 'good', False, False, False) == config['strings']['roleLeader']
    assert crtools.get_role_label(config, 'coLeader', 0, 'good', False, False, False) == config['strings']['roleCoLeader']
    assert crtools.get_role_label(config, 'elder', 0, 'good', False, False, False) == config['strings']['roleElder']
    assert crtools.get_role_label(config, 'member', 0, 'good', False, False, False) == config['strings']['roleMember']

    assert crtools.get_role_label(config, 'leader', 0, 'good', False, False, True) == config['strings']['roleNoPromote']

