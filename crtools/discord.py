from datetime import datetime
from discord_webhook import DiscordEmbed, DiscordWebhook
import logging
import math
from requests.exceptions import ConnectionError

from ._version import __version__

logger = logging.getLogger(__name__)

def trigger_webhooks(config, current_war, member_list):
    if not config['discord']['webhook_default']:
        return False

    return send_war_nag(config, current_war, member_list)

class WarNagConfig:

    abort = False
    nag_header = ''
    webhook_url = ''
    naughty_member_list = ''
    quit_member_list = ''

    def __init__(self, config, current_war, member_list):
        if current_war.state == 'notInWar':
            logger.debug('Not in war; no nagging')
            self.abort = True
            return

        self.webhook_url = config['discord']['webhook_default']
        if config['discord']['webhook_war_nag']:
            self.webhook_url = config['discord']['webhook_war_nag']

        if current_war.state == 'collectionDay':
            if config['discord']['nag_collection_battle'] == False:
                self.abort = True
                return

            war_end_timestamp = datetime.strptime(current_war.collection_end_time.split('.')[0], '%Y%m%dT%H%M%S')
            nag_threshold = config['discord']['nag_collection_battle_hours_left']
            war_day_label = config['strings']['discord-collection-label']

        elif current_war.state == 'warDay':
            if config['discord']['nag_war_battle'] == False:
                self.abort = True
                return
            war_end_timestamp = datetime.strptime(current_war.war_end_time.split('.')[0], '%Y%m%dT%H%M%S')
            nag_threshold = config['discord']['nag_war_battle_hours_left']
            war_day_label = config['strings']['discord-war-label']

        war_end_time_delta = math.floor((war_end_timestamp - config['crtools']['timestamp']).seconds / 3600)
        if war_end_time_delta > nag_threshold:
            logger.debug('Nag threshold is {} hours, and there are {} hours left. Not nagging.'.format(nag_threshold, war_end_time_delta))
            self.abort = True
            return

        logger.debug('Compiling list of users to nag')

        self._war_nag_get_naughty_member_list(current_war.participants, member_list)

        self.nag_header = config['strings']['discord-header-war-nag'].format(war_end_time_delta, war_day_label)

    def _war_nag_get_naughty_member_list(self, war_participants, member_list):
        for member in war_participants:
            if member.battles_played < member.number_of_battles:
                member_bullet = '- **{}**\n'.format(escape_markdown(member.name))
                if is_member_in_clan(member_list, member.tag):
                    self.naughty_member_list += member_bullet
                else:
                    self.quit_member_list += member_bullet

def send_war_nag(config, current_war, member_list):

    nag_config = WarNagConfig(config, current_war, member_list)

    if nag_config.abort or (nag_config.naughty_member_list == ''):
        return True

    webhook = DiscordWebhook(url=nag_config.webhook_url)

    # add list of naughty users as embed embed object to webhook
    embed = DiscordEmbed(
        title=nag_config.nag_header,
        description=nag_config.naughty_member_list,
        color = int('0xff5500', 16)
    )

    if nag_config.quit_member_list:
        webhook.add_embed(embed)
        embed = DiscordEmbed(
            title=config['strings']['discord-header-war-quit'].format(),
            description=nag_config.quit_member_list,
            color = int('0x660000', 16)
    )

    embed.set_footer(text='crtools v{}'.format(__version__))
    embed.set_timestamp()

    webhook.add_embed(embed)

    try:
        logger.info('Sending war nag to Discord')
        webhook.execute()
    except ConnectionError as e:
        logger.error('Connection to discord failed. Sending war nag webhook failed.')
        return False

    return True

def escape_markdown(s):
    markdown_escape_map = {'_' : '\\_', '*' : '\\*'}
    for search, replace in markdown_escape_map.items():
        s = s.replace(search, replace)
    return s

def is_member_in_clan(member_list, member_tag):
    for member in member_list:
        if member.tag == member_tag:
            return True
    return False

