from datetime import datetime
import logging
import pickle
import os.path

from googleapiclient.discovery import build
#from google.auth.transport.requests import Request
#from google_auth_oauthlib.flow import InstalledAppFlow

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

DEMERIT_RANGE = 'Demerits!A2:G'
VACATION_RANGE = 'Vacation!A2:E'

def get_member_data_from_sheets(config):

    sheet_id = config['google_docs']['sheet_id']

    logging.info('Grabbing blacklist/vacation data from Google Sheet {}'.format(sheet_id))

    try:
        service = build('sheets', 'v4', cache_discovery=False, developerKey=config['google_docs']['api_key'])

        # Call the Sheets API
        sheet = service.spreadsheets()

        (config['members']['blacklist'], config['members']['no_promote']) = get_demerit_data_from_sheet(sheet, sheet_id, config['members']['blacklist'], config['members']['no_promote'])
        config['members']['vacation'] = get_vacation_data_from_sheet(sheet, sheet_id, config['members']['vacation'])

    except Exception as e:
        logging.error(e)
        logging.error('Unable to get data from Google Sheet {}'.format(sheet_id))


    return config

def get_demerit_data_from_sheet(sheet, sheet_id, blacklist=[], no_promote_list=[]):

    values = sheet.values() \
                  .get(spreadsheetId=sheet_id, range=DEMERIT_RANGE) \
                  .execute() \
                  .get('values', [])


    current_name = current_tag = ''
    blacklist_names = []
    no_promote_names = []

    for (member_name, member_tag, action, member_status, reporter, date, notes) in values:
        if member_tag:
            current_tag = member_tag
            current_name = member_name

        if member_status == 'blacklist':
            if current_tag not in blacklist:
                blacklist.append(current_tag)
                blacklist_names.append(current_name)
        elif member_status == 'no-promote list':
            if current_tag not in no_promote_list:
                no_promote_list.append(current_tag)
                no_promote_names.append(current_name)

    logger.debug('Blacklist: {}'.format(blacklist_names))
    logger.debug('No-promote list: {}'.format(no_promote_names))

    return (blacklist, no_promote_list)

def get_vacation_data_from_sheet(sheet, sheet_id, vacation=[]):

    values = sheet.values() \
                  .get(spreadsheetId=sheet_id, range=VACATION_RANGE) \
                  .execute() \
                  .get('values', [])

    current_name = current_tag = ''
    vacation_names = []
    now = datetime.utcnow().date()

    for (member_name, member_tag, start_date, end_date, notes) in values:
        if member_tag:
            current_tag = member_tag
            current_name = member_name

        vacation_end = datetime.strptime(end_date, '%m/%d/%Y').date()
        if vacation_end >= now:
            if current_tag not in vacation:
                vacation.append(current_tag)
                vacation_names.append(current_name)

    logger.debug('Vacation list: {}'.format(vacation_names))

    return vacation
