from datetime import datetime
import logging

from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

DEMERIT_RANGE = 'Demerits!A2:G'
VACATION_RANGE = 'Vacation!A2:E'

def get_member_data_from_sheets(config):

    if not config['google_docs']['api_key'] or not config['google_docs']['sheet_id']:
        return config

    sheet_id = config['google_docs']['sheet_id']

    logging.info('Grabbing blacklist/vacation data from Google Sheet {}'.format(sheet_id))

    sheet = get_sheet(config['google_docs']['api_key'])

    (config['members']['blacklist'], config['members']['no_promote']) = get_demerit_data_from_sheet(sheet, sheet_id, config['members']['blacklist'], config['members']['no_promote'])
    config['members']['vacation'] = get_vacation_data_from_sheet(sheet, sheet_id, config['members']['vacation'])

    return config

def get_sheet(api_key): # pragma: no coverage
    try:
        return build('sheets', 'v4', cache_discovery=False, developerKey=api_key).spreadsheets()
    except Exception as e:
        logging.error(e)
        logging.error('Unable to connect to Google Sheets API')

def get_demerit_data_from_sheet(sheet, sheet_id, blacklist=[], no_promote_list=[]):

    try:
        values = sheet.values() \
                      .get(spreadsheetId=sheet_id, range=DEMERIT_RANGE) \
                      .execute() \
                      .get('values', [])

        current_name = current_tag = ''

        for (member_name, member_tag, action, member_status, reporter, date, notes) in values:
            if member_tag:
                current_tag = member_tag

            if member_status == 'blacklist' and current_tag not in blacklist:
                blacklist.append(current_tag)
            elif member_status == 'no-promote list' and current_tag not in no_promote_list:
                no_promote_list.append(current_tag)
    except Exception as e:
        logging.error(e)
        logging.error('Unable to get blacklist data from Google Sheets {}'.format(sheet_id))

    return (blacklist, no_promote_list)

def get_vacation_data_from_sheet(sheet, sheet_id, vacation=[]):

    try:
        values = sheet.values() \
                      .get(spreadsheetId=sheet_id, range=VACATION_RANGE) \
                      .execute() \
                      .get('values', [])

        current_name = current_tag = ''
        now = datetime.utcnow().date()

        for (member_name, member_tag, start_date, end_date, notes) in values:
            vacation_end = datetime.strptime(end_date, '%m/%d/%Y').date()
            if vacation_end >= now and member_tag not in vacation:
                vacation.append(member_tag)
    except Exception as e:
        logging.error(e)
        logging.error('Unable to get vacation data from Google Sheets {}'.format(sheet_id))

    return vacation
