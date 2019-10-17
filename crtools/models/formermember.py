from pyroyale import Clan

from crtools import history
from crtools.models import Demerit

class FormerMember():

    def __init__(self, config, historical_member, player_tag):
        self.name          = historical_member['name']
        self.tag           = player_tag
        self.blacklist     = False
        self.events        = history.process_member_events(config, historical_member['events'])
        self.timestamp     = self.events[-1].timestamp
        self.reason        = 'Quit'
        self.notes         = ''

        if player_tag in config['members']['warned']:
        	demerit = config['members']['warned'][player_tag]
        	if type(demerit) is Demerit:
		        self.reason = 'Warned'
        		self.notes = demerit.notes

        if player_tag in config['members']['kicked']:
        	demerit = config['members']['kicked'][player_tag]
        	if type(demerit) is Demerit:
		        self.reason = 'Kicked'
        		self.notes = demerit.notes

        if player_tag in config['members']['blacklist']:
        	self.blacklist = True

        	demerit = config['members']['blacklist'][player_tag]
        	if type(demerit) is Demerit:
		        self.reason = 'Blacklisted'
        		self.notes = demerit.notes
