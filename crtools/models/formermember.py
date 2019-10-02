from pyroyale import Clan

from crtools import history

class FormerMember():

    def __init__(self, config, historical_member, player_tag):
        self.name      = historical_member['name']
        self.tag       = player_tag
        self.blacklist = player_tag in config['members']['blacklist']
        self.events    = history.process_member_events(config, historical_member['events'])
        self.timestamp = self.events[-1].timestamp
