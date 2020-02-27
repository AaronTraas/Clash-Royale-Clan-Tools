from datetime import datetime
import logging

from crtools.models import Demerit, ProcessedMember, WarParticipation
from crtools import history
from crtools.scorecalc import ScoreCalculator

logger = logging.getLogger(__name__)

class MemberFactory:
    def __init__(self, config, clan, member_history, current_war, warlog=[], days_from_donation_reset=0):
        self.config = config
        self.clan = clan
        self.current_war = current_war
        self.warlog = warlog
        self.member_history = member_history
        self.days_from_donation_reset = days_from_donation_reset
        self.now = config['crtools']['timestamp']
        self.history_start_timestamp = member_history['history_start']
        self.max_days_from_join = (self.now - datetime.fromtimestamp(self.history_start_timestamp)).days


    def get_processed_member(self, member, war_readiness=None):
        processed_member = ProcessedMember(member, war_readiness)

        self.enrich_member_with_history(processed_member, self.member_history['members'][processed_member.tag])
        self.calc_special_status(processed_member)
        self.calc_derived_member_stats(processed_member)

        return processed_member

    def enrich_member_with_history(self, member, historical_member):
        days_from_donation_reset = self.days_from_donation_reset

        member.join_date = historical_member['join_date']
        member.last_activity_date = historical_member['last_activity_date']
        member.last_donation_date = historical_member['last_donation_date']
        member.donations_last_week = historical_member['donations_last_week']
        member.days_inactive = (self.now - datetime.fromtimestamp(member.last_activity_date)).days
        member.days_inactive = member.days_inactive if member.days_inactive >= 0 else 0

        if member.last_seen:
            last_seen = datetime.strptime(member.last_seen.split('.')[0], '%Y%m%dT%H%M%S')
        else:
            last_seen = config['crtools']['timestamp']

        member.last_seen_formatted = last_seen.strftime('%c')

        last_seen_delta = self.now - last_seen
        member.last_seen_delta = ''
        if last_seen_delta.days >= 1:
            member.last_seen_delta = '{} {}, '.format(last_seen_delta.days, self.config['strings']['labelDays'])
        hours = round(last_seen_delta.seconds/3600)
        if hours < 1:
            member.last_seen_delta += '{} {}'.format(round(last_seen_delta.seconds/60), self.config['strings']['labelMinutes'])
        else:
            member.last_seen_delta += '{} {}'.format(hours, self.config['strings']['labelHours'])

        if member.join_date == 0:
            member.join_date_label = self.config['strings']['labelBeforeHistory']
        else:
            member.join_date_label = datetime.fromtimestamp(member.join_date).strftime('%x')
        member.activity_date_label = datetime.fromtimestamp(member.last_activity_date).strftime('%x')

        join_datetime = datetime.fromtimestamp(member.join_date)
        member.days_from_join = (self.now - join_datetime).days
        if member.days_from_join <= 10:
            member.new = True
            logger.debug('New member {}'.format(member.name))
        else:
            member.new = False
        if member.days_from_join > self.max_days_from_join:
            member.days_from_join = self.max_days_from_join + 1

        if member.days_from_join > 560:
            member.time_in_clan = "{} {}".format(round(member.days_from_join/365), self.config['strings']['labelYears'])
        elif member.days_from_join > 60:
            member.time_in_clan = "{} {}".format(round(member.days_from_join/30), self.config['strings']['labelMonths'])
        else:
            member.time_in_clan = "{} {}".format(member.days_from_join, self.config['strings']['labelDays'])
        if member.days_from_join > self.max_days_from_join:
            member.time_in_clan = "> " + member.time_in_clan

        if days_from_donation_reset > member.days_from_join:
            days_from_donation_reset = member.days_from_join

        if member.days_inactive > 7:
            member.donations_last_week = 0

        member.total_donations = member.donations + member.donations_last_week
        if member.days_from_join > days_from_donation_reset + 7:
            days_from_donation_reset += 7
        else:
            days_from_donation_reset = member.days_from_join

        if(days_from_donation_reset > 0):
            member.donations_daily = round(member.total_donations / days_from_donation_reset)
        else:
            member.donations_daily = member.total_donations

        member.events = history.process_member_events(self.config, historical_member['events'])

    def calc_special_status(self, member):
        # get special statuses.
        # vacation = member is on vacation. Don't reccomend demote or kick, dont show score
        # safe = member marked as safe. Don't reccomend demote or kick
        # blacklist = member on blacklist. Recommend kick immediately.
        member.vacation = False
        if member.tag in self.config['members']['vacation']:
            member.vacation = self.config['members']['vacation'][member.tag]

        member.safe = member.tag in self.config['members']['safe']
        member.no_promote = member.tag in self.config['members']['no_promote']
        member.blacklist = member.tag in self.config['members']['blacklist']
        member.notes = ''

        if member.tag in self.config['members']['no_promote']:
            demerit = self.config['members']['no_promote'][member.tag]
            if type(demerit) is Demerit:
                member.notes = demerit.notes

        if member.tag in self.config['members']['blacklist']:
            demerit = self.config['members']['blacklist'][member.tag]
            if type(demerit) is Demerit:
                member.notes = demerit.notes

        # Automatically add inactive 'safe' members to vacation
        if member.safe and (member.days_inactive >= self.config['activity']['threshold_warn']):
            member.vacation = True

    def calc_derived_member_stats(self, member):
        member.current_war = WarParticipation(self.config, member, self.current_war)
        member.warlog = []
        for war in self.warlog.items:
            member.warlog.append(WarParticipation(self.config, member, war))

        score_calc = ScoreCalculator(self.config)

        member.donation_score = score_calc.get_member_donations_score(member)

        # calculate score based on war participation
        member.war_score = 0
        for war in member.warlog:
            member.war_score += war.score

        # get member score
        member.score = member.war_score + member.donation_score

        # members on the safe list can't have a score below zero
        if member.safe and member.score < 0:
            member.score = 0

        # calculate the number of daily donations, and the donation status
        # based on threshold set in config
        member.donation_status = self.calc_donation_status(member.donation_score, member.donations_daily, self.days_from_donation_reset)

        member.status = self.calc_member_status(member.score, member.no_promote)

        member.activity_status = self.calc_activity_status(member.days_inactive)

        member.role_label = self.get_role_label(member.tag, member.role, member.days_inactive, member.activity_status, member.vacation, member.blacklist, member.no_promote)

        if member.trophies >= self.clan.required_trophies:
            member.trophies_status = 'normal'
        else:
            member.trophies_status = 'ok'

        member.arena_league_label = self.config['strings']['league-' + member.arena_league['id']]

        # Figure out whether member is on the leadership team by role
        member.leadership = member.role == 'leader' or member.role == 'coLeader'

        self.calc_recent_war_stats(member)

    def get_role_label(self, member_tag, member_role, days_inactive, activity_status, vacation, blacklisted, no_promote):
        """ Format roles in sane way """

        if member_tag in self.config['members']['custom']:
            return self.config['members']['custom'][member_tag].role

        if blacklisted:
            return self.config['strings']['roleBlacklisted']

        if vacation:
            if not hasattr(vacation, 'end_date') or vacation.end_date == 0:
                return self.config['strings']['roleVacation']
            else:
                return self.config['strings']['roleVacationUntil'].format(vacation.end_date)

        if activity_status in ['bad', 'ok']:
            return self.config['strings']['roleInactive'].format(days=days_inactive)

        if no_promote:
            return self.config['strings']['roleNoPromote']

        return {
            'leader'   : self.config['strings']['roleLeader'],
            'coLeader' : self.config['strings']['roleCoLeader'],
            'elder'    : self.config['strings']['roleElder'],
            'member'   : self.config['strings']['roleMember'],
        }[member_role]

    def calc_recent_war_stats(self, member):
        war_wins = 0
        war_battles = 0
        collection_wins = 0
        collection_cards = 0
        for war in member.warlog:
            if hasattr(war, 'wins'):
                war_wins += war.wins
                war_battles += war.number_of_battles
            if hasattr(war, 'collection_battle_wins'):
                collection_wins += war.collection_battle_wins
            if hasattr(war, 'collection_win_cards'):
                collection_cards += war.collection_win_cards

        if war_battles > 0:
            member.war_win_rate = round((war_wins/war_battles) * 100)
        else:
            member.war_win_rate = 0

        member.war_battles = war_battles
        member.war_collection_win_rate = round(((collection_wins / 10) / 3) * 100)
        member.war_collection_cards_average = round(collection_cards / 10)
        member.war_score_average = round(member.war_score / 10)

    def calc_donation_status(self, donation_score, donations_daily, days_from_donation_reset):
        """ calculate the number of daily donations, and the donation status
        based on threshold set in config """
        if donation_score >= self.config['score']['max_donations_bonus']:
            return 'good'

        if days_from_donation_reset >= 1:
            if donations_daily == 0:
                return 'bad'

            if donations_daily < self.config['score']['min_donations_daily']:
                return 'ok'

        return 'normal'

    def calc_member_status(self, member_score, no_promote):
        # either 'good', 'ok', 'bad', or 'normal'
        if member_score < 0:
            return 'bad'

        if member_score >= self.config['score']['threshold_promote'] and not no_promote:
            return 'good'

        if member_score < self.config['score']['threshold_warn']:
            return 'ok'

        return 'normal'

    def calc_activity_status(self, days_inactive):
        if days_inactive <= 0:
            return 'good'

        if days_inactive <= 2:
            return 'na'

        if days_inactive >= self.config['activity']['threshold_kick']:
            return 'bad'

        if days_inactive >= self.config['activity']['threshold_warn']:
            return 'ok'

        return 'normal'


