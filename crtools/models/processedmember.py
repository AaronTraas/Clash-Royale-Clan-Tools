from datetime import datetime
from html import escape

import logging

from pyroyale import ClanMember

from crtools import leagueinfo
from crtools.scorecalc import ScoreCalculator
from crtools.models.warparticipation import WarParticipation

logger = logging.getLogger(__name__)

class ProcessedMember(ClanMember):
    def __init__(self, member, member_history=[]):
        self.tag = member.tag
        self.name = escape(member.name)
        self.exp_level = member.exp_level
        self.trophies = member.trophies
        self.arena = member.arena
        self.role = member.role
        self.last_seen = member.last_seen
        self.clan_rank = member.clan_rank
        self.previous_clan_rank = member.previous_clan_rank
        self.donations = member.donations
        self.donations_received = member.donations_received
        self.clan_chest_points = member.clan_chest_points

        self.arena_league = leagueinfo.get_arena_league_from_name(self.arena.name)['id']

        self.score = 'int'
        self.vacation = False
        self.safe = False
        self.blacklist = False
        self.no_promote = False

        # Piggybacking on the serialization in the pyroyale API objects. We're adding to the list of properties to export
        self.openapi_types = member.openapi_types.copy()
        self.openapi_types['arena_league'] = 'string'
        self.openapi_types['arena_league_label'] = 'string'
        self.openapi_types['role_label'] = 'string'

        self.openapi_types['join_date'] = 'str'
        self.openapi_types['join_date_label'] = 'str'
        self.openapi_types['last_activity_date'] = 'str'
        self.openapi_types['last_donation_date'] = 'str'
        self.openapi_types['donations_last_week'] = 'str'
        self.openapi_types['days_inactive'] = 'str'
        self.openapi_types['last_seen'] = 'str'
        self.openapi_types['last_seen_formatted'] = 'str'
        self.openapi_types['last_seen_delta'] = 'str'
        self.openapi_types['activity_date_label'] = 'string'
        self.openapi_types['activity_status'] = 'string'

        self.openapi_types['score'] = 'int'
        self.openapi_types['status'] = 'string'
        self.openapi_types['trophies_status'] = 'string'

        self.openapi_types['new'] = 'bool'
        self.openapi_types['leadership'] = 'bool'
        self.openapi_types['vacation'] = 'bool'
        self.openapi_types['safe'] = 'bool'
        self.openapi_types['blacklist'] = 'bool'
        self.openapi_types['no_promote'] = 'bool'

        self.openapi_types['total_donations'] = 'int'
        self.openapi_types['donation_status'] = 'string'
        self.openapi_types['donations_daily'] = 'int'
        self.openapi_types['donations_last_week'] = 'int'
        self.openapi_types['donation_score'] = 'int'

        self.openapi_types['events'] = 'list'

        self.openapi_types['current_war'] = 'obj'
        self.openapi_types['warlog'] = 'list'
        self.openapi_types['war_collection_cards_average'] = 'int'
        self.openapi_types['war_collection_win_rate'] = 'int'
        self.openapi_types['war_score'] = 'int'
        self.openapi_types['war_score_average'] = 'int'
        self.openapi_types['war_win_rate'] = 'int'

