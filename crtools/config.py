from configparser import SafeConfigParser
import copy
import logging
import os

# Create config dict with defaults
config_defaults = {
    'api' : {
        'server_url' :          'https://api.clashroyale.com',
        'api_key' :             False,
        'clan_id' :             False,
    },
    'paths' : {
        'out' :                 './crtools-out',
        'favicon' :             False,
        'clan_logo' :           False,
        'description_html' :    False,
        'temp_dir_name' :       'crtools'
    },
    'www' : {
        'canonical_url' :       False
    },
    'activity': {
        'threshold_warn':       7,
        'threshold_kick':       21
    },
    'score' : {
        'min_clan_size' :               46,
        'war_battle_played' :           15,
        'war_battle_incomplete' :       -30,
        'war_battle_won' :              5,
        'war_battle_lost' :             0,
        'collect_battle_played' :       0,
        'collect_battle_incomplete' :   -5,
        'collect_battle_won' :          2,
        'collect_battle_lost' :         0,
        'war_participation' :           0,
        'war_non_participation' :       -1,
        'min_donations_daily' :         12,
        'max_donations_bonus' :         40,
        'donations_zero' :              -40,
        'threshold_promote' :           160,
        'threshold_demote' :            0,
        'threshold_kick' :              0,
        'threshold_warn' :              30
    },
    'members': {
        'blacklist' : [],
        'vacation' : [],
        'safe' :     []
    },
    'crtools' : {
        'debug' : False
    }
}

def __validate_crtools_settings(config):
    if config['crtools']['debug'] == True:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    return config

def __validate_paths(config):
    logger = logging.getLogger(__name__)

    # If logo_path is provided, use logo from path given, and put it where
    # it needs to go. Otherwise, use the default from the template folder
    logo_src_path = os.path.join(os.path.dirname(__file__), 'templates', 'crtools-logo.png')
    if config['paths']['clan_logo']:
        logo_src_path_test = os.path.expanduser(config['paths']['clan_logo'])
        if os.path.isfile(logo_src_path_test):
            logo_src_path = logo_src_path_test
        else:
            logger.warn('custom logo file "{}" not found. Using default instead.'.format(logo_src_path_test))
    config['paths']['clan_logo'] = logo_src_path

    # If favicon_path is provided, use favicon from path given, and put it
    # where it needs to go. Otherwise, use the default from the template folder
    favicon_src_path = os.path.join(os.path.dirname(__file__), 'templates', 'crtools-favicon.ico')
    if config['paths']['favicon']:
        favicon_src_path_test = os.path.expanduser(config['paths']['favicon'])
        if os.path.isfile(favicon_src_path_test):
            favicon_src_path = favicon_src_path_test
        else:
            logger.warn('custom favicon file "{}" not found. Using default instead.'.format(favicon_src_path_test))
    config['paths']['favicon'] = favicon_src_path

    # if external clan description file is specified, read that file and
    # use it for the clan description section. If not, use the clan
    # description returned by the API
    config['paths']['description_html_src'] = None
    if config['paths']['description_html']:
        description_path = os.path.expanduser(config['paths']['description_html'])
        if os.path.isfile(description_path):
            with open(description_path, 'r') as myfile:
                config['paths']['description_html_src'] = myfile.read()
        else:
            logger.warn('custom description file "{}" not found. Using default instead.'.format(description_path))

    return config

def __parse_value(new_value, template_value):
    value = new_value
    if isinstance(template_value, list):
        value = value.split(',');
        value = [x.strip() for x in value]
    else:
        # if the value represents an integer, convert from string to int
        try:
            value = int(value)
        except ValueError:
            pass

        # if set to "true" or "false" or similar, convert to boolean
        if isinstance(value, str):
            if value.lower() in ['true', 'yes', 'on']:
                value = True
            elif value.lower() in ['false', 'no', 'off']:
                value = False
    return value

def load_config_file(config_file_name=None):
    """ Look for config file. If config file exists, load it, and try to
    extract config from config file"""

    config = copy.deepcopy(config_defaults)

    if os.path.isfile(config_file_name):
        parser = SafeConfigParser()
        parser.read(config_file_name)

        # Map the contents of the ini file with the structure for the config object found above.
        for section in parser.sections():
            section_key = section.lower()
            if section_key in config:
                for (key, value) in parser.items(section):
                    if key in config[section_key]:
                        config[section_key][key] = __parse_value(value, config[section_key][key])

    config = __validate_paths(config)
    config = __validate_crtools_settings(config)

    logging.getLogger(__name__).debug(config)
    return config
