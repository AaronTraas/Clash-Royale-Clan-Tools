import pytest
import requests_mock

from crtools import load_config_file
from crtools.config import PYPI_URL, LOCALE_NOT_FOUND_ERROR_TEMPLATE

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

__config_paths_template__ = '''
[Paths]
clan_logo={logo}
favicon={favicon}
description_html={description}
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
    assert type(config['members']['blacklist']) == type({})
    assert config['members']['blacklist']['Foo'].tag == 'Foo'

    # Properly stripped whitespace from list element
    assert config['members']['vacation']['Baz'].tag == 'Baz'
    assert config['members']['vacation']['Baz'].start_date == 0


def test_config_paths_empty(tmpdir):
    config_file = tmpdir.mkdir('test_config_paths_empty').join('config.ini')
    config_file.write(__config_paths_template__.format(
        logo        = False,
        favicon     = False,
        description = False
    ))
    config = load_config_file(config_file.realpath())

    assert config['paths']['clan_logo'].endswith('/templates/crtools-logo.png')
    assert config['paths']['favicon'].endswith('/templates/crtools-favicon.ico')
    assert config['paths']['description_html_src'] == None

def test_config_paths_invalid(tmpdir):
    config_file = tmpdir.mkdir('test_config_paths_empty').join('config.ini')
    config_file.write(__config_paths_template__.format(
        logo        = '~/path/to/invalid/logo',
        favicon     = '~/path/to/invalid/favicon',
        description = '~/path/to/invalid/description'
    ))
    config = load_config_file(config_file.realpath())

    assert config['paths']['clan_logo'].endswith('/templates/crtools-logo.png')
    assert config['paths']['favicon'].endswith('/templates/crtools-favicon.ico')
    assert config['paths']['description_html_src'] == None

def test_config_paths_valid(tmpdir):
    test_tmpdir = tmpdir.mkdir('test_config_paths_valid')
    logo = test_tmpdir.join('logo.png')
    favicon = test_tmpdir.join('favicon.ico')
    description = test_tmpdir.join('description.html')

    config_file = test_tmpdir.join('config.ini')
    config_file.write(__config_paths_template__.format(
        logo        = str(logo.realpath()),
        favicon     = favicon.realpath(),
        description = description.realpath()
    ))
    logo.write('foo')
    favicon.write('foo')
    description.write('foo')
    config = load_config_file(config_file.realpath())

    assert config['paths']['clan_logo'].endswith('/test_config_paths_valid/logo.png')
    assert config['paths']['favicon'].endswith('/test_config_paths_valid/favicon.ico')
    assert config['paths']['description_html'].endswith('/test_config_paths_valid/description.html')

def test_version_update(requests_mock, tmpdir):
    latest_version = '99.99.99'
    mock_object = {'releases': {latest_version: []}}

    requests_mock.get(PYPI_URL, json=mock_object, status_code=200)

    config_file = tmpdir.mkdir('test_config_unknown_key').join('config.ini')
    config_file.write(__config_debug)

    config = load_config_file(config_file.realpath(), True)

    assert config['crtools']['latest_version'] != config['crtools']['version']
    assert config['crtools']['latest_version'] == latest_version
    assert config['crtools']['update_available'] == True

def test_version_update_latest(requests_mock, tmpdir):
    latest_version = '0.0.0'
    mock_object = {'releases': {latest_version: []}}

    requests_mock.get(PYPI_URL, json=mock_object, status_code=200)

    config_file = tmpdir.mkdir('test_config_unknown_key').join('config.ini')
    config_file.write(__config_debug)

    config = load_config_file(config_file.realpath(), True)

    assert config['crtools']['latest_version'] == config['crtools']['version']
    assert config['crtools']['update_available'] == False

def test_version_update_request_fail(requests_mock, tmpdir):
    mock_object = {}

    requests_mock.get(PYPI_URL, json=mock_object, status_code=500)

    config_file = tmpdir.mkdir('test_config_unknown_key').join('config.ini')
    config_file.write(__config_debug)

    config = load_config_file(config_file.realpath(), True)

    assert config['crtools']['latest_version'] == config['crtools']['version']
    assert config['crtools']['update_available'] == False

def test_bad_locale_aborts_with_error(tmpdir, capsys):
    config_file = tmpdir.mkdir('test_bad_locale_defaults_to_default').join('config.ini')
    bad_locale = 'sdlkjfasldfjalsdfjalsdf'
    config_file.write('[crtools]\nlocale='+bad_locale)

    with pytest.raises(SystemExit):
        config = load_config_file(config_file.realpath())
    out, err = capsys.readouterr()
    expected = LOCALE_NOT_FOUND_ERROR_TEMPLATE.format(bad_locale)
    assert expected in out


