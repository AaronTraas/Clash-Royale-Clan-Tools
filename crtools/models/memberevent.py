from datetime import datetime

class MemberEvent():
    def __init__(self, config, event_dict):
        self.date      = datetime.fromtimestamp(event_dict['date']).strftime('%x')
        self.timestamp = event_dict['date']
        self.event     = event_dict['event']
        self.message   = {
            'join'        : config['strings']['memberEventJoinedClan'],
            'role change' : config['strings']['memberEventRoleChange'].format(event_dict['role']),
            'quit'        : config['strings']['memberEventExitClan']
        }[self.event]

