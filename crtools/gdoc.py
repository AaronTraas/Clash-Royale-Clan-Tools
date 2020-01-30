from datetime import datetime
import logging

from googleapiclient.discovery import build

from crtools.models import Demerit, MemberVacation, MemberCustomRecord

logger = logging.getLogger('gdoc')

DEMERIT_RANGE = 'Demerits!A2:G'
VACATION_RANGE = 'Vacation!A2:E'
CUSTOM_RANGE = 'Custom!A2:D'

def get_member_data_from_sheets(config):
    """ If API key and Sheet ID are provided in config, use the Google Sheets API to
    grab blacklist, no-promote list, and vacation data.

    Template found here: https://docs.google.com/spreadsheets/d/1_8YKfJf-2HVZOgtuosVaGM_50kB8q7YYR3H2d8p0Wzw
    """

    if not config['google_docs']['api_key'] or not config['google_docs']['sheet_id']:
        return config

    sheet_id = config['google_docs']['sheet_id']

    logging.info('Grabbing blacklist/vacation data from Google Sheet {}'.format(sheet_id))

    sheet = get_sheet(config['google_docs']['api_key'])

    (config['members']['blacklist'], config['members']['no_promote'], config['members']['kicked'], config['members']['warned']) = get_demerit_data_from_sheet(sheet, sheet_id, config['members']['blacklist'], config['members']['no_promote'])
    config['members']['vacation'] = get_vacation_data_from_sheet(sheet, sheet_id, config['crtools']['timestamp'], config['members']['vacation'])
    config['members']['custom'] = get_custom_data_from_sheet(sheet, sheet_id)

    return config

# no coverage of this function because this is the function we're mocking to get mock
# results for unit tests
def get_sheet(api_key): # pragma: no coverage
    """ Returns authenticated Google Sheet API wrapper using API key """
    try:
        return build('sheets', 'v4', cache_discovery=False, developerKey=api_key).spreadsheets()
    except Exception as e:
        logging.error(e)
        logging.error('Unable to connect to Google Sheets API')

def get_demerit_list(sheet, sheet_id):
    try:
        values = sheet.values() \
                      .get(spreadsheetId=sheet_id, range=DEMERIT_RANGE) \
                      .execute() \
                      .get('values', [])

        demerits = []
        current_tag = ''
        for (member_name, member_tag, action, member_status, reporter, date, notes) in values:
            if member_tag:
                current_tag = member_tag.strip()

            demerits.append(Demerit(tag=current_tag, action=action, status=member_status, date=date, notes=notes))

        return demerits

    except Exception as e:
        logging.error(e)
        logging.error('Unable to get blacklist data from Google Sheets {}'.format(sheet_id))

    return []

def get_vacation_list(sheet, sheet_id, now):
    try:
        values = sheet.values() \
                      .get(spreadsheetId=sheet_id, range=VACATION_RANGE) \
                      .execute() \
                      .get('values', [])

        vacations = []
        now_date = now.date()
        for (member_name, member_tag, start_date, end_date, notes) in values:
            vacation_end = datetime.strptime(end_date, '%m/%d/%Y').date()

            if vacation_end >= now_date:
                vacations.append(MemberVacation(tag=member_tag, start_date=start_date, end_date=end_date, notes=notes))

        return vacations
    except Exception as e:
        logging.error(e)
        logging.error('Unable to get vacation data from Google Sheets {}'.format(sheet_id))

    return []

def get_custom_record_list(sheet, sheet_id):
    try:
        values = sheet.values() \
                      .get(spreadsheetId=sheet_id, range=CUSTOM_RANGE) \
                      .execute() \
                      .get('values', [])

        vacations = []
        for (member_name, member_tag, custom_role, notes) in values:
            vacations.append(MemberCustomRecord(tag=member_tag, role=custom_role, notes=notes))

        return vacations
    except Exception as e:
        logging.error(e)
        logging.error('Unable to get custom data from Google Sheets {}'.format(sheet_id))

    return []


def get_demerit_data_from_sheet(sheet, sheet_id, blacklist={}, no_promote_list={}, kicked_list={}, warned_list={}):

    demerits = get_demerit_list(sheet, sheet_id)

    if demerits:
        for demerit in demerits:
            if demerit.action == 'kicked':
                kicked_list[demerit.tag] = demerit
            elif demerit.action == 'warning':
                warned_list[demerit.tag] = demerit

            if demerit.status == 'blacklist':
                if demerit.tag in blacklist:
                    demerit.merge(blacklist[demerit.tag])
                blacklist[demerit.tag] = demerit
            elif demerit.status == 'no-promote list':
                no_promote_list[demerit.tag] = demerit

    return (blacklist, no_promote_list, kicked_list, warned_list)

def get_vacation_data_from_sheet(sheet, sheet_id, now, vacation_list={}):

    vacations = get_vacation_list(sheet, sheet_id, now)

    if vacations:
        for vacation in vacations:
            vacation_list[vacation.tag] = vacation

    return vacation_list

def get_custom_data_from_sheet(sheet, sheet_id, custom_list={}):

    custom = get_custom_record_list(sheet, sheet_id)

    if custom:
        for record in custom:
            custom_list[record.tag] = record

    return custom_list
