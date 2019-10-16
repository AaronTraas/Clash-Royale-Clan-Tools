from datetime import datetime, timedelta

from crtools import leagueinfo
from crtools.scorecalc import ScoreCalculator

def _get_war_date(war):
    """ returns the datetime this war was created. If it's an ongoing
    war, calculate based on the dates given when the war started.
    If it's a previous war fromt he warlog, we retrieve the creation
    date. What's returned is a timestamp. """
    war_date_raw = 0

    if hasattr(war, 'state') :
        if war.state == 'warDay':
            war_date_raw = datetime.strptime(war.war_end_time.split('.')[0], '%Y%m%dT%H%M%S')
            war_date_raw -= timedelta(days=2)
        elif war.state == 'collectionDay':
            war_date_raw = datetime.strptime(war.collection_end_time.split('.')[0], '%Y%m%dT%H%M%S')
            war_date_raw -= timedelta(days=1)
    else:
        war_date_raw = datetime.strptime(war.created_date.split('.')[0], '%Y%m%dT%H%M%S')
        war_date_raw -= timedelta(days=1)

    return datetime.timestamp(war_date_raw)


def _get_member_war_status_class(collection_day_battles, war_day_battles, war_date, join_date, current_war=False, war_day=False):
    """ returns CSS class(es) for a war log entry for a given member """
    if war_date < join_date:
        return 'not-in-clan'

    status = 'normal'
    if current_war:
        if collection_day_battles < 3:
            status = 'ok'
        elif war_day and war_day_battles > 0:
            status = 'good'

        if war_day == False or war_day_battles == 0:
            status += ' incomplete'
    else:
        if collection_day_battles == 0:
            status = 'na'
        elif war_day_battles == 0:
            status = 'bad'
        elif collection_day_battles < 3:
            status = 'ok'
        else:
            status = 'good'
    return status

class WarParticipation():

    def __init__(self, config, member, war):
        self.in_war = False
        self.status = 'na'
        self.score = 0
        self.battles_played = False
        self.cards_earned = 0
        self.collection_win_cards = 0
        self.collection_day_battles_played = 0
        self.collection_battle_wins = 0
        self.collection_battle_losses = 0
        self.wins = 0
        self.war_league = 'na'
        self.number_of_battles = 0

        # Bail early if this is for the current war, and there is no
        # current war
        if hasattr(war, 'state') and war.state == 'notInWar':
            return

        member_tag = member.tag
        war_date = _get_war_date(war)
        join_date = member.join_date if hasattr(member, 'join_date') else 0

        if hasattr(war, 'state') :
            self.score = 0
        elif war_date < join_date:
            # member is not in this war
            self.status = 'not-in-clan'
            return
        else:
            # member is not in this war
            self.score = ScoreCalculator(config).get_war_score(self)

        for participant in war.participants:
            if participant.tag == member_tag:
                self.in_war = True
                self.cards_earned = participant.cards_earned
                self.battles_played = participant.battles_played
                self.collection_day_battles_played = participant.collection_day_battles_played
                self.wins = participant.wins
                self.number_of_battles = participant.number_of_battles

                if hasattr(war, 'state'):
                    self.status = _get_member_war_status_class(self.collection_day_battles_played, self.battles_played, war_date, join_date, True, war.state=='warDay')
                    return;

                self.status = _get_member_war_status_class(self.collection_day_battles_played, self.battles_played, war_date, join_date)

                self.war_league = leagueinfo.get_war_league_from_war(war, config['api']['clan_id'])
                self.collection_win_cards = leagueinfo.get_collection_win_cards(self.war_league, member.arena_league)

                self.collection_battle_wins = round(self.cards_earned / self.collection_win_cards)
                self.collection_battle_losses = self.collection_day_battles_played - self.collection_battle_wins
                self.score = ScoreCalculator(config).get_war_score(self)
