from datetime import datetime
from html import escape

import logging

from pyroyale import ClanMember

from crtools import leagueinfo
from crtools.scorecalc import ScoreCalculator
from crtools.models.warparticipation import WarParticipation

logger = logging.getLogger(__name__)

class ProcessedMember():
    def __init__(self, member, war_readiness=None):
        self.tag = member.tag
        self.name = escape(member.name)
        self.exp_level = member.exp_level
        self.trophies = member.trophies
        self.role = member.role
        self.last_seen = member.last_seen
        self.clan_rank = member.clan_rank
        self.previous_clan_rank = member.previous_clan_rank
        self.donations = member.donations
        self.donations_received = member.donations_received
        self.clan_chest_points = member.clan_chest_points

        self.war_readiness = war_readiness

        self.war_readiness_status = 'normal'
        if war_readiness:
            if war_readiness > 75:
                self.war_readiness_status = 'good'
            elif war_readiness < 33:
                self.war_readiness_status = 'bad'

        self.arena_league = leagueinfo.get_arena_league_from_trophies(self.trophies)

        self.score = 'int'
        self.vacation = False
        self.safe = False
        self.blacklist = False
        self.no_promote = False

