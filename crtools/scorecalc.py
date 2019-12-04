
class ScoreCalculator:
    def __init__(self, config):
        self.config = config

    def get_member_donations_score(self, member):
        """ Calculate the score for a given member's daily donations. """

        donation_score = member.donations_daily - self.config['score']['min_donations_daily']

        donation_score = donation_score if donation_score <= self.config['score']['max_donations_bonus'] else self.config['score']['max_donations_bonus']

        if member.total_donations == 0:
            donation_score += self.config['score']['donations_zero']

        if member.days_from_join <= self.config['score']['new_member_grace_period_days'] and donation_score <= 0:
            donation_score = 0

        return donation_score

    def get_war_score(self, war):
        """ Tally the score for a given war """

        if war.status == 'not-in-clan':
            return 0;

        if hasattr(war, 'in_war') and not war.in_war:
            return self.config['score']['war_non_participation']

        war_score = 0
        war_score += war.collection_battle_wins * self.config['score']['collect_battle_won']
        war_score += war.collection_battle_losses * self.config['score']['collect_battle_lost']
        war_score += war.collection_day_battles_played * self.config['score']['collect_battle_played']
        war_score += (3-war.collection_day_battles_played) * self.config['score']['collect_battle_incomplete']

        if war.battles_played < 1:
            war_score += self.config['score']['war_battle_incomplete']
            return war_score

        war_score += self.config['score']['war_battle_played'] if war.battles_played > 0 else 0
        war_score += war.wins * self.config['score']['war_battle_won']
        war_score += (war.battles_played - war.wins) * self.config['score']['war_battle_lost']

        return war_score

