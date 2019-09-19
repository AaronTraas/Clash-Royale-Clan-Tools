from datetime import datetime
from html import escape

import logging

from pyroyale import ClanMember
from crtools import history

logger = logging.getLogger(__name__)

class ProcessedClanMember(ClanMember):
    def __init__(self, member, config, clan, current_war, member_history=history.get_member_history([]), days_from_donation_reset=0, now=datetime.utcnow()):
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

        self.enrich_member_with_history(config, member_history['members'][self.tag], days_from_donation_reset, now)
        self.calc_special_status(config)
        #self.calc_derived_member_stats(config, clan, warlog, current_war, days_from_donation_reset)

    def enrich_member_with_history(self, config, historical_member, days_from_donation_reset=0, now=datetime.utcnow()):
        self.join_date = historical_member['join_date']
        self.last_activity_date = historical_member['last_activity_date']
        self.last_donation_date = historical_member['last_donation_date']
        self.donations_last_week = historical_member['donations_last_week']
        self.days_inactive = (now - datetime.fromtimestamp(self.last_activity_date)).days
        self.days_inactive = self.days_inactive if self.days_inactive >= 0 else 0

        last_seen = datetime.strptime(self.last_seen.split('.')[0], '%Y%m%dT%H%M%S')
        self.last_seen_formatted = last_seen.strftime('%c')

        last_seen_delta = now - last_seen
        self.last_seen_delta = ''
        if last_seen_delta.days >= 1:
            self.last_seen_delta = '{} {}, '.format(last_seen_delta.days, config['strings']['labelDays'])
        hours = round(last_seen_delta.seconds/3600)
        if hours < 1:
            self.last_seen_delta += '{} {}'.format(round(last_seen_delta.seconds/60), config['strings']['labelMinutes'])
        else:
            self.last_seen_delta += '{} {}'.format(hours, config['strings']['labelHours'])


        if self.join_date == 0:
            self.join_date_label = config['strings']['labelBeforeHistory']
        else:
            self.join_date_label = datetime.fromtimestamp(self.join_date).strftime('%x')
        self.activity_date_label = datetime.fromtimestamp(self.last_activity_date).strftime('%x')

        join_datetime = datetime.fromtimestamp(self.join_date)
        days_from_join = (now - join_datetime).days
        if days_from_join <= 10:
            self.new = True
            logger.debug('New member {}'.format(self.name))
        else:
            self.new = False

        if days_from_donation_reset > days_from_join:
            days_from_donation_reset = days_from_join

        if self.days_inactive > 7:
            self.donations_last_week = 0

        self.total_donations = self.donations
        if days_from_join > days_from_donation_reset + 7:
            days_from_donation_reset += 7
            self.total_donations += self.donations_last_week

        if(days_from_donation_reset > 0):
            self.donations_daily = round(self.total_donations / days_from_donation_reset)
        else:
            self.donations_daily = self.total_donations

        self.events = history.process_member_events(config, historical_member['events'])

    def calc_special_status(self, config):
        # get special statuses.
        # vacation = member is on vacation. Don't reccomend demote or kick, dont show score
        # safe = member marked as safe. Don't reccomend demote or kick
        # blacklist = member on blacklist. Recommend kick immediately.
        self.vacation = self.tag in config['members']['vacation']
        self.safe = self.tag in config['members']['safe']
        self.no_promote = self.tag in config['members']['no_promote']
        self.blacklist = self.tag in config['members']['blacklist']

        # Automatically add inactive 'safe' members to vacation
        if self.safe and (self.days_inactive >= config['activity']['threshold_warn']):
            self.vacation = True

    def calc_derived_member_stats(self, config, clan, warlog, current_war, days_from_donation_reset):
        # get member warlog and add it to the record
        self.current_war = member_war(config, current_war)
        self.warlog = member_warlog(config, warlog)

        self.donation_score = donations_score(config, self)

        # calculate score based on war participation
        self.war_score = 0
        for war in self.warlog:
            self.war_score += war.score

        # get member score
        self.score = self.war_score + self.donation_score

        # calculate the number of daily donations, and the donation status
        # based on threshold set in config
        self.donation_status = calc_donation_status(config, self.donation_score, self.donationsDaily, days_from_donation_reset)

        self.status = calc_member_status(config, self.score, self.no_promote)

        self.activity_status = calc_activity_status(config, self.days_inactive)

        self.role_label = get_role_label(config, self.role, self.days_inactive, self.activity_status, self.vacation, self.blacklist, self.no_promote)

        if self.trophies >= clan['required_trophies']:
            self.trophies_status = 'normal'
        else:
            self.trophies_status = 'ok'

        self.arena_league = leagueinfo.get_arena_league_from_name(self.arena.name)['id']
        self.arena_league_label = config['strings']['league-' + self.arena_league]

        # Figure out whether member is on the leadership team by role
        self.leadership = self.role == 'leader' or self.role == 'coLeader'

        self.calc_recent_war_stats()

    def calc_recent_war_stats(self):
        war_wins = 0
        war_battles = 0
        collection_wins = 0
        collection_cards = 0
        for war in member.warlog:
            if 'wins' in war:
                war_wins += war['wins']
                war_battles += war['number_of_battles']
            if 'collectionBattleWins' in war:
                collection_wins += war['collectionBattleWins']
            if 'collectionWinCards' in war:
                collection_cards += war['collectionWinCards']

        if war_battles > 0:
            self.war_win_rate = round((war_wins/war_battles) * 100)
        else:
            self.war_win_rate = 0

        self.war_collection_win_rate = round(((collection_wins / 10) / 3) * 100)
        self.war_collection_cards_average = round(collection_cards / 10)
        self.war_score_average = round(self.war_score / 10)
