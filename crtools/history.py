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

def validate_history(history):
    """ Returns True if and only if the history object is
    validly formatted """
    return type(history) == dict \
        and 'last_update' in history \
        and 'members' in history \
        and type(history['members']) == dict

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


def get_member_history(members, old_history=None, date=datetime.now()):
    """ Generates user history. Takes as inputs the list of members
    from the API, as well as optionally the old history, and a date
    object for synchronization and testing.

    If the old history does not exist, it creates a new one, and sets
    the timestamp value for each user join event to zero, essentially
    positing that the member joined prior to recorded history.

    There are 3 types of events recorded for each members:
    - join
    - quit
    - role change (promotion or demotion)

    The API does not give us whether or not the user has been kicked
    or voluntarily quit. We can only observe the absence of the member.
    """

    timestamp = datetime.timestamp(date)

    # basically, validate that old history is formatted properly
    if validate_history(old_history):
        history = old_history.copy()
        history['last_update'] = timestamp
    else:
        history = {
            'last_update': timestamp,
            'members': {}
        }
        timestamp = 0;

    for member in members:
        tag = member['tag']
        new_role = member['role']
        new_role = 'coLeader' if new_role == 'co-leader' else new_role
        if tag in history['members']:
            historical_member = history['members'][tag]
            if historical_member['role'] != member['role']:
                historical_member['events'].append({
                        'event': 'role change',
                        'type':  get_role_change_status(historical_member['role'], member['role']),
                        'role':  member['role'],
                        'date':  timestamp
                    })
                historical_member['role'] = member['role']
        else:
            history['members'][tag] = {
                'join_date':    timestamp,
                'role':         member['role'],
                'events':       [{
                                    'event': 'join',
                                    'type':  'new',
                                    'role':  member['role'],
                                    'date':  timestamp
                                }]
            }

    return history

