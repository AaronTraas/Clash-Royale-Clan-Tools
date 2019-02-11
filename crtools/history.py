#!/usr/bin/python

from datetime import datetime

"""Functions for maintaining a historical record of the clan."""

ROLE_MEMBER     = 'member'
ROLE_ELDER      = 'elder'
ROLE_COLEADER   = 'coLeader'
ROLE_LEADER     = 'leader'

def validate_role(role):
    """ Returns whether or not the role string is a valid role """
    return role in [ROLE_MEMBER, ROLE_ELDER, ROLE_COLEADER, ROLE_LEADER]

def get_role_change_status(old_role, new_role):
    """ Return 'unchanged', 'promotion', or 'demotion' based
    on the relationship between the old and new role. If the
    roles are invalid, or some other error state, returns
    False."""
    if validate_role(old_role) and validate_role(new_role):
        if old_role == new_role:
            return 'unchanged'
        if old_role == ROLE_MEMBER:
            return 'promotion'
        elif new_role == ROLE_LEADER:
            return 'promotion'
        elif old_role == ROLE_ELDER:
            if new_role == ROLE_MEMBER:
                return 'demotion'
            else:
                return 'promotion'
        elif old_role == ROLE_COLEADER or old_role == ROLE_LEADER:
            return 'demotion'

    return False

def get_member_history(members, old_history, timestamp=datetime.now()):
    if type(old_history):
        history = old_history.copy()
    else:
        history = {
            'last-update': timestamp,
            'members': {}
        }

    for member in members:
        tag = member['tag']
        new_role = member['role']
        new_role = 'coLeader' if new_role == 'co-leader' else new_role
        if tag in history['members']:
            historical_member = history['members'][tag]
            if historical_member['role'] != member['role']:
                historical_member['role'].append({
                        'event': 'role change',
                        'status': get_role_change_status(historical_member['role'], member['role']),
                        'role':  member['role'],
                        'date':  timestamp
                    })

        else:
            history['members'][tag] = {
                'join_date':    timestamp,
                'role':         member['role'],
                'events':       [{
                                    'event': 'join',
                                    'role':  member['role'],
                                    'date':  timestamp
                                }]
            }

    return history