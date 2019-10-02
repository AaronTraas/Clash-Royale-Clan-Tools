from crtools import load_config_file
from crtools.memberfactory import MemberFactory

def test_calc_activity_status():
    config = load_config_file(False)

    factory = MemberFactory(config, None, None, None)

    assert factory.calc_activity_status(0) == 'good'
    assert factory.calc_activity_status(-1) == 'good'
    assert factory.calc_activity_status(1) == 'na'
    assert factory.calc_activity_status(3) == 'normal'
    assert factory.calc_activity_status(7) == 'ok'
    assert factory.calc_activity_status(400) == 'bad'

def test_calc_member_status(tmpdir):
    config_file = tmpdir.mkdir('test_calc_member_status').join('config.ini')
    config_file.write('''
[Score]
threshold_promote=100
threshold_warn=10
''')
    config = load_config_file(config_file.realpath())

    factory = MemberFactory(config, None, None, None)

    assert factory.calc_member_status(-1, False)  == 'bad'
    assert factory.calc_member_status(5, False)   == 'ok'
    assert factory.calc_member_status(10, False)  == 'normal'
    assert factory.calc_member_status(100, False) == 'good'
    assert factory.calc_member_status(100, True)  == 'normal'

def test_calc_donation_status(tmpdir):
    config_file = tmpdir.mkdir('test_calc_donation_status').join('config.ini')
    config_file.write('''
[Score]
max_donations_bonus=40
min_donations_daily=10
''')
    config = load_config_file(config_file.realpath())

    factory = MemberFactory(config, None, None, None)

    assert factory.calc_donation_status(1000, 100, 6) == 'good'
    assert factory.calc_donation_status(0, 0, 6) == 'bad'
    assert factory.calc_donation_status(0, 5, 6) == 'ok'
    assert factory.calc_donation_status(0, 0, 0) == 'normal'

def test_get_role_label():
    config = load_config_file(False)

    factory = MemberFactory(config, None, None, None)

    assert factory.get_role_label('member', 0, 'good', False, True, False) == config['strings']['roleBlacklisted']
    assert factory.get_role_label('leader', 100, 'bad', True, True, False) == config['strings']['roleBlacklisted']
    assert factory.get_role_label('leader', 100, 'bad', True, False, False) == config['strings']['roleVacation']
    assert factory.get_role_label('leader', 100, 'bad', False, False, False) == config['strings']['roleInactive'].format(days=100)

    assert factory.get_role_label('leader', 0, 'good', False, False, False) == config['strings']['roleLeader']
    assert factory.get_role_label('coLeader', 0, 'good', False, False, False) == config['strings']['roleCoLeader']
    assert factory.get_role_label('elder', 0, 'good', False, False, False) == config['strings']['roleElder']
    assert factory.get_role_label('member', 0, 'good', False, False, False) == config['strings']['roleMember']

    assert factory.get_role_label('leader', 0, 'good', False, False, True) == config['strings']['roleNoPromote']

