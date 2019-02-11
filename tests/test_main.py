import crtools

__config_debug =  '''
[crtools]
debug=True
'''

def test_parse_args_config_file(tmpdir):
    config_file = tmpdir.mkdir('test_parse_args').join('config.ini')
    config_file.write(__config_debug)

    argv = [
        '--config', str(config_file.realpath())
    ]

    config = crtools.get_config_from_args(crtools.parse_args(argv))

    assert config['crtools']['debug'] == True

def test_parse_args_config_file_not_found(capsys):
    argv = [
        '--config', '~/fake/path/that/does/not/exist'
    ]

    try:
        config = crtools.get_config_from_args(crtools.parse_args(argv))
    except SystemExit as e:
        assert e.code == -1
        return

    # Fail if we didn't catch a SystemExit
    assert False

def test_parse_args_all(tmpdir):
    argv = [
        '--api_key',        'FakeAPIKey',
        '--clan',           '#FakeClanTag',
        '--out',            '/fake/output/path',
        '--favicon',        '/fake/favicon/path',
        '--clan_logo',      '/fake/clan/logo/path',
        '--description',    '/fake/description/path',
        '--canonical_url',  'https://fake-canonical-url.fake-tld/fake/path',
        '--debug'
    ]
    config = crtools.get_config_from_args(crtools.parse_args(argv))
    assert config['api']['api_key'] == argv[1]
    assert config['api']['clan_id'] == argv[3]
    assert config['paths']['out'] == argv[5]
    assert config['paths']['favicon'] == argv[7]
    assert config['paths']['clan_logo'] == argv[9]
    assert config['paths']['description_html'] == argv[11]
    assert config['www']['canonical_url'] == argv[13]
    assert config['crtools']['debug'] == True
