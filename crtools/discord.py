from datetime import datetime #, date, timezone, timedelta
from discord_webhook import DiscordEmbed, DiscordWebhook
import logging
import math

from ._version import __version__

logger = logging.getLogger(__name__)

def trigger_webhooks(config, current_war, member_list):
    if not config['discord']['webhook_default']:
        return

    app_url = config['www']['canonical_url']

    send_war_nag(config, app_url, current_war, member_list)

def send_war_nag(config, app_url, current_war, member_list):

    now = datetime.utcnow()
    war_day_label = ''
    war_end_timestamp = 0
    nag_threshold = 0
    if current_war['state'] == 'collectionDay':
        if config['discord']['nag_collection_battle'] == False:
            return
        war_end_timestamp = datetime.strptime(current_war['collection_end_time'].split('.')[0], '%Y%m%dT%H%M%S')
        nag_threshold = config['discord']['nag_collection_battle_hours_left']
        war_day_label = config['strings']['discord-collection-label']
    elif current_war['state'] == 'warDay':
        if config['discord']['nag_war_battle'] == False:
            return
        war_end_timestamp = datetime.strptime(current_war['war_end_time'].split('.')[0], '%Y%m%dT%H%M%S')
        nag_threshold = config['discord']['nag_war_battle_hours_left']
        war_day_label = config['strings']['discord-war-label']
    else:
        logger.debug('Not in war; no nagging')
        return

    logger.debug('Sending nag webhook')

    war_end_time_delta = math.floor((war_end_timestamp - now).seconds / 3600)
    if war_end_time_delta > nag_threshold:
        logger.debug('Nag threshold is {} hours, and there are {} hours left. Not nagging.'.format(nag_threshold, war_end_time_delta))
        return

    naughty_member_list = ''
    quit_member_list = ''
    for member in current_war['participants']:
        if member['battles_played'] < member['number_of_battles']:
            member_bullet = '- **{}**\n'.format(escape_markdown(member['name']))
            if is_member_in_clan(member_list, member['tag']):
                naughty_member_list += member_bullet
            else:
                quit_member_list += member_bullet

    if naughty_member_list == '':
        logger.debug('No members need nagging')
        return

    webhook_url = config['discord']['webhook_default']
    if config['discord']['webhook_war_nag']:
        webhook_url = config['discord']['webhook_war_nag']

    webhook = DiscordWebhook(url=webhook_url)

    # add list of naughty users as embed embed object to webhook
    embed = DiscordEmbed(
        title=config['strings']['discord-header-war-nag'].format(war_end_time_delta, war_day_label),
        description=naughty_member_list,
        color = int('0xff5500', 16)
    )

    if quit_member_list:
        webhook.add_embed(embed)
        embed = DiscordEmbed(
            title=config['strings']['discord-header-war-quit'].format(war_end_time_delta, war_day_label),
            description=quit_member_list,
            color = int('0x660000', 16)
    )

    embed.set_footer(text='crtools v{}'.format(__version__))
    embed.set_timestamp()

    webhook.add_embed(embed)

    webhook.execute()

def escape_markdown(s):
    markdown_escape_map = {'_' : '\\_', '*' : '\\*'}
    for search, replace in markdown_escape_map.items():
        s = s.replace(search, replace)
    return s

def is_member_in_clan(member_list, member_tag):
    for member in member_list:
        if member['tag'] == member_tag:
            return True
    return False

