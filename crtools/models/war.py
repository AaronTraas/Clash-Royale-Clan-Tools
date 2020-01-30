from datetime import datetime
import logging
import math

from pyroyale import WarCurrent

class ProcessedCurrentWar:

    cards = 0
    state_label = ''
    collection_end_time_label = ''
    end_label = ''

    def __init__(self, current_war, config):
        self.state = current_war.state
        self.war_end_time = current_war.war_end_time
        self.collection_end_time = current_war.collection_end_time
        self.clan = current_war.clan
        self.participants = current_war.participants
        self.clans = current_war.clans

        self.cards = 0
        self.state_label = ''
        self.collection_end_time_label = ''
        self.end_label = ''

        self.process(config)

    def process(self, config):
        if self.state == 'notInWar':
            self.state_label = config['strings']['LabelNotInWar']
            return

        self.cards = 0;
        for member in self.participants:
            self.cards += member.cards_earned

        now = config['crtools']['timestamp']
        if self.state == 'collectionDay':
            self.state_label = config['strings']['labelStateCollectionDay']

            collection_end_time = datetime.strptime(self.collection_end_time.split('.')[0], '%Y%m%dT%H%M%S')
            collection_end_time_delta = math.floor((collection_end_time - now).seconds / 3600)
            self.collection_end_time_label = config['strings']['labelCollectionEndTime'].format(collection_end_time_delta)
            self.end_label = config['strings']['labelEndTime'].format(collection_end_time_delta)
        else:
            self.state_label = config['strings']['labelStateWarDay']

            end_time = datetime.strptime(self.war_end_time.split('.')[0], '%Y%m%dT%H%M%S')
            end_time_delta = math.floor((end_time - now).seconds / 3600)
            self.collection_end_time_label = config['strings']['labelCollectionComplete']
            self.end_label = config['strings']['labelCollectionEndTime'].format(end_time_delta)

            # calculate battles remaining for each clan
            for clan in self.clans:
                clan.battles_remaining = clan.participants - clan.battles_played
                if clan.battles_remaining < 0:
                    clan.battles_remaining = 0; # pragma: no coverage

            # sort clans by who's winning
            self.clans = sorted(self.clans, key=lambda k: (k.wins, k.crowns), reverse=True)

