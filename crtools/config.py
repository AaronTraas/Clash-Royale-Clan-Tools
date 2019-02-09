from configparser import SafeConfigParser
import copy
import logging
import os

# Create config dict with defaults
config_defaults = {
    'api' : {
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
        'canonical_url' :       False,
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
                        if isinstance(config[section_key][key], list):
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
                        config[section_key][key] = value

    if config['crtools']['debug'] == True:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    logging.debug(config)
    return config
