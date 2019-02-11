from crtools import history

def test_get_role_change_status():
    assert history.get_role_change_status('foo',                 'foo')                 == False
    assert history.get_role_change_status('foo',                 'bar')                 == False
    assert history.get_role_change_status('foo',                 history.ROLE_MEMBER)   == False
    assert history.get_role_change_status(history.ROLE_MEMBER,   'foo')                 == False
    assert history.get_role_change_status('foo',                 'foo')                 == False
    assert history.get_role_change_status(history.ROLE_LEADER,   history.ROLE_LEADER)   == 'unchanged'
    assert history.get_role_change_status(history.ROLE_LEADER,   history.ROLE_COLEADER) == 'demotion'
    assert history.get_role_change_status(history.ROLE_LEADER,   history.ROLE_ELDER)    == 'demotion'
    assert history.get_role_change_status(history.ROLE_LEADER,   history.ROLE_MEMBER)   == 'demotion'
    assert history.get_role_change_status(history.ROLE_COLEADER, history.ROLE_COLEADER) == 'unchanged'
    assert history.get_role_change_status(history.ROLE_COLEADER, history.ROLE_LEADER)   == 'promotion'
    assert history.get_role_change_status(history.ROLE_COLEADER, history.ROLE_ELDER)    == 'demotion'
    assert history.get_role_change_status(history.ROLE_COLEADER, history.ROLE_MEMBER)   == 'demotion'
    assert history.get_role_change_status(history.ROLE_ELDER,    history.ROLE_ELDER)    == 'unchanged'
    assert history.get_role_change_status(history.ROLE_ELDER,    history.ROLE_LEADER)   == 'promotion'
    assert history.get_role_change_status(history.ROLE_ELDER,    history.ROLE_COLEADER) == 'promotion'
    assert history.get_role_change_status(history.ROLE_ELDER,    history.ROLE_MEMBER)   == 'demotion'
    assert history.get_role_change_status(history.ROLE_MEMBER,   history.ROLE_MEMBER)   == 'unchanged'
    assert history.get_role_change_status(history.ROLE_MEMBER,   history.ROLE_LEADER)   == 'promotion'
    assert history.get_role_change_status(history.ROLE_MEMBER,   history.ROLE_COLEADER) == 'promotion'
    assert history.get_role_change_status(history.ROLE_MEMBER,   history.ROLE_ELDER)    == 'promotion'
