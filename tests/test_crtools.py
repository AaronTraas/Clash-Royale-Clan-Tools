from datetime import datetime, timedelta
import copy
import os
import shutil

import pyroyale
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
        battles_played                = 1,
        wins                          = 1,
        number_of_battles             = 1,
        collection_day_battles_played = 1
    ),
    pyroyale.WarParticipant(
        tag                           =  '#DDDDDD',
        cards_earned                  = 1120,
        battles_played                = 0,
        wins                          = 1,
        number_of_battles             = 1,
        collection_day_battles_played = 1
    )
]

__fake_war__ = pyroyale.War(
    created_date = '20190209T212846.354Z',
    participants = __fake_war_participants__,
    standings = [
        pyroyale.WarStanding(
            clan = pyroyale.WarStandingClan(
                tag            = CLAN_TAG,
                clan_score     = 2428,
                participants   = 19,
                battles_played = 20,
                wins           = 11,
                crowns         = 22
            ),
            trophy_change = 111
        )
    ]
)

__fake_warlog__ = pyroyale.WarLog(
    items = [
        __fake_war__
    ]
)

__fake_currentwar_warday__ = pyroyale.WarCurrent(
    state        = 'warDay',
    war_end_time = '20190209T212846.354Z',
    clan         = __fake_war_clan__,
    participants = __fake_war_participants__,
    clans        = [__fake_war_clan__]
)

__fake_currentwar_collectionday__ = pyroyale.WarCurrent(
    state               = 'collectionDay',
    collection_end_time = '20190209T212846.354Z',
    clan                = __fake_war_clan__,
    participants        = __fake_war_participants__
)

__fake_currentwar_notinwar__ = pyroyale.WarCurrent(
    state='notInWar',
    participants=[],
#    clan=__fake_clan__,
    clans=[]
)

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

    assert crtools.get_war_date(pyroyale.War(created_date=raw_date_string)) == datetime.timestamp(test_date - timedelta(days=1))

    assert crtools.get_war_date(pyroyale.WarCurrent(state='warDay', war_end_time=raw_date_string)) == datetime.timestamp(test_date - timedelta(days=2))

    assert crtools.get_war_date(pyroyale.WarCurrent(state='collectionDay', collection_end_time=raw_date_string)) == datetime.timestamp(test_date - timedelta(days=1))

def test_member_war(tmpdir):
    config_file = tmpdir.mkdir('test_member_war').join('testfile')
    config_file.write(__config_file_score__)
    config = load_config_file(config_file.realpath())

    war_current_nowar = crtools.member_war(
        config,
        __fake_clan__.member_list[0],
        pyroyale.WarCurrent(state='notInWar')
    )
    assert war_current_nowar['status'] == 'na'
    assert war_current_nowar['score'] == 0

    war_current_isparticipating = crtools.member_war(
        config,
        __fake_clan__.member_list[0].to_dict(),
        __fake_currentwar_warday__
    )
    assert war_current_isparticipating['status'] == 'good'
    assert war_current_isparticipating['score'] == 0

    war_current_notparticipating = crtools.member_war(
        config,
        __fake_clan__.member_list[3].to_dict(),
        __fake_currentwar_warday__
    )
    assert war_current_notparticipating['status'] == 'ok incomplete'
    assert war_current_notparticipating['score'] == 0

    war_isparticipating_good = crtools.member_war(
        config,
        __fake_clan__.member_list[0].to_dict(),
        __fake_war__
    )
    assert war_isparticipating_good['status'] == 'good'
    assert war_isparticipating_good['score'] == 34

    war_isparticipating_ok = crtools.member_war(
        config,
        __fake_clan__.member_list[1].to_dict(),
        __fake_war__
    )
    print(__fake_clan__.member_list[1].arena)
    assert war_isparticipating_ok['status'] == 'ok'
    assert war_isparticipating_ok['score'] == 24

    war_isparticipating_bad = crtools.member_war(
        config,
        __fake_clan__.member_list[2].to_dict(),
        __fake_war__
    )
    assert war_isparticipating_bad['status'] == 'ok'
    assert war_isparticipating_bad['score'] == 24

    war_notparticipating = crtools.member_war(
        config,
        __fake_clan__.member_list[3].to_dict(),
        __fake_war__
    )
    assert war_notparticipating['status'] == 'bad'
    assert war_notparticipating['score'] == -18

def test_member_warlog(tmpdir):
    config_file = tmpdir.mkdir('test_member_warlog').join('testfile')
    config_file.write(__config_file_score__)
    config = load_config_file(config_file.realpath())

    warlog = crtools.member_warlog(config, __fake_clan__.member_list[0].to_dict(), __fake_warlog__)
    assert warlog[0]['status'] == 'good'

    warlog = crtools.member_warlog(config, __fake_clan__.member_list[1].to_dict(), __fake_warlog__)
    assert warlog[0]['status'] == 'ok'

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

    h = history.get_member_history(__fake_clan__.member_list, None)

    members = crtools.process_members(config, __fake_clan__, __fake_warlog__, __fake_currentwar_notinwar__, h)

    suggestions = crtools.get_suggestions(config, members, __fake_clan__)

    print(suggestions)

    assert len(suggestions) == 1
    assert suggestions[0] == config['strings']['suggestionRecruit']

def test_process_absent_members(tmpdir):
    config_file = tmpdir.mkdir('test_get_suggestions').join('testfile')
    config_file.write(__config_file_score__ + '\nthreshold_demote=-999999\nthreshold_promote=9999999')
    config = load_config_file(config_file.realpath())

    h = history.get_member_history(__fake_clan__.member_list, __fake_history_old_member__)

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

    h = history.get_member_history(__fake_clan__.member_list, None)

    members = crtools.process_members(config, __fake_clan__, __fake_warlog__, __fake_currentwar_notinwar__, h)

    suggestions = crtools.get_suggestions(config, members, __fake_clan__)

    print(suggestions)

    assert suggestions[0].startswith('Kick')
    assert members[3]['name'] in suggestions[0]

def test_get_suggestions_promote_demote(tmpdir):
    config_file = tmpdir.mkdir('test_get_suggestions').join('testfile')
    config_file.write(__config_file_score__ + '\nthreshold_promote=10')
    config = load_config_file(config_file.realpath())

    h = history.get_member_history(__fake_clan__.member_list, None)

    members = crtools.process_members(config, __fake_clan__, __fake_warlog__, __fake_currentwar_notinwar__, h)

    suggestions = crtools.get_suggestions(config, members, __fake_clan__.required_trophies)

    print(suggestions)

    assert suggestions[0].startswith('Demote')
    assert members[2]['name'] in suggestions[0]
    assert suggestions[1].startswith('Promote') or suggestions[2].startswith('Promote')
    assert members[4]['name'] in suggestions[1] or members[4]['name'] in suggestions[2]


def test_process_recent_wars(tmpdir):
    config_file = tmpdir.mkdir('test_process_recent_wars').join('config.ini')
    config_file.write(__config_file__)

    config = load_config_file(config_file.realpath())

    processed_warlog = crtools.process_recent_wars(config, __fake_warlog__)

    assert processed_warlog[0].clan.tag == CLAN_TAG
    assert processed_warlog[0].rank == 1
    assert processed_warlog[0].date == '2/9'
    assert processed_warlog[0].trophy_change == 111

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

