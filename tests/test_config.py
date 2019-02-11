from crtools import load_config_file

__config_debug =  '''
[crtools]
debug=True
'''

__config_file_unknown_key =  '''
[garbage]
should_not_exist=True
'''

__config_file_booleans__ = '''
[score]
min_clan_size=False
war_battle_played=false
war_battle_incomplete=True
war_battle_won=true
'''

__config_file_list__ = '''
[api]
api_key=Foo,Bar,Baz
[members]
blacklist=Foo
vacation=Bar,     Baz    ,Quux
'''

def test_config_debug(tmpdir):
    """ Sections and properties in INI files should never be added to
    config object if they aren't in the template """
    config_file = tmpdir.mkdir('test_config_unknown_key').join('config.ini')
    config_file.write(__config_debug)

    config = load_config_file(config_file.realpath())

    assert config['crtools']['debug'] == True

def test_config_unknown_key(tmpdir):
    """ Sections and properties in INI files should never be added to
    config object if they aren't in the template """
    config_file = tmpdir.mkdir('test_config_unknown_key').join('config.ini')
    config_file.write(__config_file_unknown_key)

    config = load_config_file(config_file.realpath())

    assert ('garbage' in config) == False


def test_config_boolean(tmpdir):
    """ 'True' and 'False' should properly be parsed as booleans. Also,
    Should be case insensitive. """
    config_file = tmpdir.mkdir('test_config_boolean').join('config.ini')
    config_file.write(__config_file_booleans__)

    config = load_config_file(config_file.realpath())

    # input was 'False'
    assert config['score']['min_clan_size'] == False
    assert type(config['score']['min_clan_size']) == type(False)

    # input was 'false'
    assert config['score']['war_battle_played'] == False
    assert type(config['score']['war_battle_played']) == type(False)

    # input was 'True'
    assert config['score']['war_battle_incomplete'] == True
    assert type(config['score']['war_battle_incomplete']) == type(True)

    # input was 'true'
    assert config['score']['war_battle_won'] == True
    assert type(config['score']['war_battle_won']) == type(True)

def test_config_list(tmpdir):
    """ If the template property contains a list, parse the contents as a list """
    config_file = tmpdir.mkdir('test_config_list').join('config.ini')
    config_file.write(__config_file_list__)

    config = load_config_file(config_file.realpath())

    # did not parse ['api']['api_key'] as list, because was not a list in template
    assert type(config['api']['api_key']) == type('')

    # Parsed ['members']['blacklist'] in config as a list, because the template was a list
    assert config['members']['blacklist'][0] == 'Foo'
    assert type(config['members']['blacklist']) == type([])

    # Properly stripped whitespace from list element
    assert config['members']['vacation'][1] == 'Baz'


