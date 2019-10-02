from datetime import datetime, timedelta

import pyroyale
from crtools.models import warparticipation

def test_get_member_war_status_class():
    assert warparticipation._get_member_war_status_class(0, 0, 0, 1) == 'not-in-clan'
    assert warparticipation._get_member_war_status_class(0, 0, 0, 0) == 'na'
    assert warparticipation._get_member_war_status_class(3, 0, 0, 0) == 'bad'
    assert warparticipation._get_member_war_status_class(2, 1, 0, 0) == 'ok'
    assert warparticipation._get_member_war_status_class(3, 1, 0, 0) == 'good'
    assert warparticipation._get_member_war_status_class(3, 0, 0, 0, True) == 'normal incomplete'
    assert warparticipation._get_member_war_status_class(2, 0, 0, 0, True) == 'ok incomplete'
    assert warparticipation._get_member_war_status_class(2, 0, 0, 0, True, True) == 'ok incomplete'
    assert warparticipation._get_member_war_status_class(2, 1, 0, 0, True, True) == 'ok'
    assert warparticipation._get_member_war_status_class(3, 1, 0, 0, True, True) == 'good'

def test_get_war_date():
    raw_date_string = '20190213T000000.000Z'
    test_date = datetime.strptime(raw_date_string.split('.')[0], '%Y%m%dT%H%M%S')

    assert warparticipation._get_war_date(pyroyale.War(created_date=raw_date_string)) == datetime.timestamp(test_date - timedelta(days=1))

    assert warparticipation._get_war_date(pyroyale.WarCurrent(state='warDay', war_end_time=raw_date_string)) == datetime.timestamp(test_date - timedelta(days=2))

    assert warparticipation._get_war_date(pyroyale.WarCurrent(state='collectionDay', collection_end_time=raw_date_string)) == datetime.timestamp(test_date - timedelta(days=1))
