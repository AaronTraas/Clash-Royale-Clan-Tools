#!/usr/bin/python

from datetime import datetime
import copy

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

def cleanup_member_history(member, history, timestamp):
    """ make sure member history entry has all the necessary fields.
    This is here to make upgrades smooth """
    now = timestamp
    if now == 0:
        now = datetime.timestamp(datetime.now())
    if 'join_date' not in history:
        history['join_date'] = timestamp
    if 'last_activity_date' not in history:
        history['last_activity_date'] = now
    if 'last_donation_date' not in history:
        history['last_donation_date'] = timestamp
    if 'role' not in history:
        history['role'] = member['role']
    if 'status' not in history:
        history['status'] = 'present'
    if 'donations' not in history:
        history['donations'] = member['donations']
    if 'donations_last_week' not in history:
        history['donations_last_week'] = 0
    if 'events' not in history:
        history['events'] = [{
                                'event': 'join',
                                'type':  'new',
                                'role':  member['role'],
                                'date':  timestamp
                            }]
    return history

def create_new_member(member, timestamp):
    return cleanup_member_history(member, {}, timestamp)

def member_rejoin(historical_member, member, timestamp):
    updated_member = copy.deepcopy(historical_member)
    updated_member['events'].append({
        'event': 'join',
        'type':  're-join',
        'role':  member['role'],
        'date':  timestamp
    })
    updated_member['role'] = member['role']
    updated_member['status'] = 'present'
    updated_member['last_activity_date'] = timestamp

    return updated_member

def member_role_change(historical_member, member, timestamp):
    updated_member = copy.deepcopy(historical_member)
    updated_member['events'].append({
            'event': 'role change',
            'type':  get_role_change_status(updated_member['role'], member['role']),
            'role':  member['role'],
            'date':  timestamp
        })
    updated_member['role'] = member['role']

    return updated_member

def member_quit(historical_member, timestamp):
    # member can't quit if he isn't there.
    if historical_member['status'] == 'absent':
        return historical_member

    updated_member = copy.deepcopy(historical_member)

    updated_member['events'].append({
        'event': 'quit',
        'type':  'left',
        'role':  updated_member['role'],
        'date':  timestamp
    })
    updated_member['status'] = 'absent'

    return updated_member

def get_member_history(members, old_history=None, current_war=None, date=datetime.now()):
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
        history = copy.deepcopy(old_history)
        history['last_update'] = timestamp
    else:
        history = {
            'last_update': timestamp,
            'members': {}
        }
        # if history is new, we want all members to have a join
        # date of 0, implying that they've joined before recorded
        # history
        timestamp = 0;

    war_participants = []
    if current_war and current_war['state'] != 'notInWar':
        for participant in current_war['participants']:
            war_participants.append(participant['tag'])

    member_tags = []
    for member in members:
        tag = member['tag']
        member['role'] = 'coLeader' if member['role'] == 'co-leader' else member['role']
        member_tags.append(tag)
        if tag not in history['members']:
            # No history of this member, therefore they are new.
            # Create record for user.
            history['members'][tag] = create_new_member(member, timestamp)
        else:
            historical_member = cleanup_member_history(member, history['members'][tag], timestamp)
            if historical_member['status'] == 'absent':
                # If member exists, but is absent in history, the
                # member has re-joined
                history['members'][tag] = member_rejoin(historical_member, member, timestamp)
            elif historical_member['role'] != member['role']:
                # Member's role has changed
                history['members'][tag] = member_role_change(historical_member, member, timestamp)
            if member['donations'] < historical_member['donations']:
                historical_member['donations_last_week'] = historical_member['donations']
                historical_member['donations'] = member['donations']
            if member['donations'] > historical_member['donations']:
                historical_member['donations'] = member['donations']
                historical_member['last_donation_date'] = timestamp
                historical_member['last_activity_date'] = timestamp
            if tag in war_participants:
                historical_member['last_activity_date'] = timestamp

    # Look for missing members. If they're missing, they quit
    for tag, member in history['members'].copy().items():
        if tag not in member_tags:
            history['members'][tag] = member_quit(member, timestamp)

    return history

