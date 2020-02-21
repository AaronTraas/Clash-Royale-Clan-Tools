import logging
import pyroyale

from crtools import leagueinfo

logger = logging.getLogger(__name__)
api_instance = False

class ApiWrapper:
    def __init__(self, config):
        logger.debug("Creating API instnce")
        api_config = pyroyale.Configuration()
        api_config.api_key['authorization'] = config['api']['api_key']
        if config['api']['proxy']:
            api_config.proxy = config['api']['proxy']
        if config['api']['proxy_headers']:
            api_config.proxy_headers = config['api']['proxy_headers']

        self.clans = pyroyale.ClansApi(pyroyale.ApiClient(api_config))
        self.players = pyroyale.PlayersApi(pyroyale.ApiClient(api_config))


def get_war_readiness_for_member(config, member_tag, war_trophies):
    api = ApiWrapper(config)

    logger.debug("Getting card for player {}".format(member_tag))
    try:
        # Get clan data and war log from API.
        player = api.players.get_player(member_tag)

        war_league = leagueinfo.get_war_league_from_score(war_trophies)

        war_readiness_delta_target = {
            'legendary': 1,
            'gold': 2,
            'silver': 3,
            'bronze': 4
        }[war_league]

        ready_count = 0
        for card in player.cards:
            delta = card.max_level - card.level
            if delta <= war_readiness_delta_target:
                ready_count += 1

        return (ready_count / len(player.cards)) * 100
    except pyroyale.ApiException as e:
        if e.body:
            body = json.loads(e.body)
            if body['reason'] == 'accessDenied':
                logger.error('developer.clashroyale.com claims that your API key is invalid. Please make sure you are setting up crtools with a valid key.')
            elif body['reason'] == 'accessDenied.invalidIp':
                logger.error('developer.clashroyale.com says: {}'.format(body['message']))
            else:
                logger.error('error: {}'.format(body))
        else:
            logger.error('error: {}'.format(e))
    except pyroyale.OpenApiException as e:
        logger.error('error: {}'.format(e))

    return False

def get_data_from_api(config): # pragma: no coverage
    api = ApiWrapper(config)

    try:
        # Get clan data and war log from API.
        clan = api.clans.get_clan(config['api']['clan_id'])
        warlog = api.clans.get_clan_war_log(config['api']['clan_id'])
        current_war = api.clans.get_current_war(config['api']['clan_id'])

        print('- clan: {} ({})'.format(clan.name, clan.tag))

        return (clan, warlog, current_war)
    except pyroyale.ApiException as e:
        if e.body:
            body = json.loads(e.body)
            if body['reason'] == 'accessDenied':
                logger.error('developer.clashroyale.com claims that your API key is invalid. Please make sure you are setting up crtools with a valid key.')
            elif body['reason'] == 'accessDenied.invalidIp':
                logger.error('developer.clashroyale.com says: {}'.format(body['message']))
            else:
                logger.error('error: {}'.format(body))
        else:
            logger.error('error: {}'.format(e))
    except pyroyale.OpenApiException as e:
        logger.error('error: {}'.format(e))

    # If we've gotten here, something has gone wrong. We need to abort the application.
    exit(0)
