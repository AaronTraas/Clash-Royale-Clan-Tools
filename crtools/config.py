from configparser import SafeConfigParser
import copy
import gettext
import json
import logging
import os
import requests
try:
    from packaging.version import parse
except ImportError:
    from pip._vendor.packaging.version import parse

from ._version import __version__

logger = logging.getLogger(__name__)

PYPI_URL = 'https://pypi.org/pypi/crtools/json'

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
        'debug'            : False,
        'locale'           : 'en',
        'version'          : __version__,
        'latest_version'   : __version__,
        'update_available' : False
    }
}

def __localize_strings(locale):
    localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
    translate = gettext.translation('crtools', localedir, languages=[locale], fallback=True)
    _ = translate.gettext

    return {
        'mainHeader'                : _('{clan_name} Clan Dashboard'),

        'ctaLookingForClan'         : _('Looking for a clan?'),
        'buttonJoinUs'              : _('Join us!'),

        'sectionCurrentWar'         : _('Current war'),
        'sectionWarStandings'       : _('Standings'),
        'sectionRecentWars'         : _('Recent wars'),
        'sectionMemberTable'        : _('Member list and stats'),
        'sectionSuggestions'        : _('Suggestions'),
        'sectionScoring'            : _('Score explanation'),

        'labelClanStats'            : _('Clan Stats'),
        'labelClanName'             : _('Clan Name'),
        'labelClanScore'            : _('Clan Score'),
        'labelDonationsPerWeek'     : _('Donations/week'),
        'labelRequiredTrophies'     : _('Required Trophies'),
        'labelWarTrophies'          : _('War Trophies'),
        'labelClanTag'              : _('Clan Tag'),
        'labelClanRole'             : _('Clan Role'),
        'labelLastUpdate'           : _('Last update'),
        'labelYes'                  : _('Yes'),
        'labelNo'                   : _('No'),
        'labelNoWarInLog'           : _('No wars in war log'),
        'labelWarState'             : _('State'),
        'labelCollectionDayEnd'     : _('Collection Day End'),
        'labelWarEnd'               : _('War End'),
        'labelNumWarParticipants'   : _('Participants'),
        'labelWarCrowns'            : _('Crowns'),
        'labelWarVictories'         : _('Victories'),
        'labelWarCards'             : _('Cards Earned'),
        'labelMember'               : _('Member'),
        'labelMemberName'           : _('Member Name'),
        'labelMemberTag'            : _('Member Tag'),
        'labelMemberJoinDate'       : _('Join Date'),
        'labelMemberLastActivity'   : _('Last Activity Date'),
        'labelArena'                : _('Arena'),
        'labelXpLevel'              : _('XP Level'),
        'labelScore'                : _('Score'),
        'labelTrophies'             : _('Trophies'),
        'labelDonations'            : _('Dona&shy;tions'),
        'labelDaysInactive'         : _('Days Inactive'),
        'labelCurrentWar'           : _('Current War'),
        'labelNotInClan'            : _('Not in clan'),
        'labelNA'                   : _('N/A'),
        'LabelNotInWar'             : _('The clan is not currently engaged in a war.'),
        'labelScoreDonations'       : _('Score from donations'),
        'labelScoreWar'             : _('Score from war participation'),
        'labelCardsGiven'           : _('Cards given'),
        'labelCardRecieved'         : _('Cards recieved'),
        'labelDonationsLastWeek'    : _('Cards given last week'),
        'labelCollectionDayBattles' : _('Collection day battles'),
        'labelCollectionDayWins'    : _('Collection day wins'),
        'labelCardsEarned'          : _('Cards earned'),
        'labelWarDayBattles'        : _('War day battles'),
        'labelWarDayWins'           : _('War day wins'),
        'labelWarScore'             : _('War score'),
        'labelWarLeague'            : _('War league'),

        'dialogTitleMemberDetails'  : _('Member Details'),
        'dialogLabelPlayerStats'    : _('Player Stats and Info'),

        'tooltipMemberNotInWar'     : _('<strong>{name}</strong> was not in the clan at the time of this war.'),
        'tooltipCurrentWarNoScore'  : _('NOTE: current war <strong>does not</strong> affect score.'),

        'labelFilter'               : _('Filter'),
        'filterNone'                : _('None'),
        'filterLeadership'          : _('Leadership'),
        'filterRoleElder'           : _('Role: Elder'),
        'filterRoleMember'          : _('Role: Member'),
        'filterNewMembers'          : _('New Members'),
        'filterInCurrentWar'        : _('In current war'),
        'filterInactive'            : _('Inactive'),
        'filterDanger'              : _('In danger'),

        'suggestionKick'            : _('Members with a <strong class="bad">score below 0</strong> will be recommended for kicking or demotion.'),
        'suggestionInactive'        : _('Members inactive for <strong class="bad">{days_inactive} days</strong> will be kicked.'),
        'suggestionPromote'         : _('A member who achieves <strong class="good">{points} points</strong> is elegible for promotion to <strong>Elder</strong> at the discretion of leadership.'),
        'suggestionRecruit'         : _('<strong>Recruit new members!</strong> The team needs some fresh blood.'),
        'suggestionNone'            : _('No suggestions at this time. The clan is in good order.'),
        'suggestionKickBlacklist'   : _('Kick <strong>{name}</strong>. Member is blacklisted.'),
        'suggestionKickInactivity'  : _('Kick <strong>{name}</strong> <strong class="bad">{days} days inactive</strong>'),
        'suggestionKickScore'       : _('Kick <strong>{name}</strong> <strong class="bad">{score}</strong>'),
        'suggestionDemoteScore'     : _('Demote <strong>{name}</strong> <strong class="bad">{score}</strong>'),
        'suggestionPromoteScore'    : _('Promote <strong>{name}</strong> to <strong>Elder</strong> <strong class="good">{score}</strong>'),

        'scoreBreakdown'            : _('Score is made of two components: <strong>donation score</strong> and <strong>war participation score</strong>.'),
        'scoreDonationLabel'        : _('Donation Score'),
        'scoreDonationBreakdown'    : _('You are expected to donate <strong>{min_donations_daily} cards per day</strong>, on average. If you make more, you will gain points. If you make fewer, you will lose points. If you have zero, you will be penalized <strong class="bad">{donations_zero} points</strong>'),

        'scoreWarLabel'             : _('War Participation Score'),
        'scoreRuleHeader'           : _('For each of the last 10 wars, did member...'),
        'ruleParticipate'           : _('...participate in the war?'),
        'ruleCollectionComplete'    : _('...complete each collection battle? (per battle)'),
        'ruleCollectionWin'         : _('...win each collection battle? (per battle)'),
        'ruleWarDayComplete'        : _('...complete war day battle?'),
        'ruleWarDayWin'             : _('...win war day battle? (per battle)')
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

def __get_version_info(config):
    logger.debug('Grabbing current version from PyPI')

    req = requests.get(PYPI_URL)
    latest_version = current_version = parse(config['crtools']['version'])
    if req.status_code == requests.codes.ok:
        j = json.loads(req.text)
        releases = j.get('releases', [])
        for release in releases:
            ver = parse(release)
            latest_version = max(latest_version, ver)

    logger.info('crtools version: {}'.format(current_version))
    if latest_version > current_version:
        config['crtools']['latest_version'] = '{}'.format(latest_version)
        config['crtools']['update_available'] = True
        logger.info('*** update available: crtools {} ***'.format(latest_version))

    return config

def load_config_file(config_file_name=None, check_for_update=False, locale=None):
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

    if check_for_update:
        config = __get_version_info(config)

    logger.debug(config)

    if locale:
        config['crtools']['locale'] = locale

    config['strings'] = __localize_strings(config['crtools']['locale'])

    return config
