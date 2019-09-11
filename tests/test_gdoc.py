import googleapiclient.discovery
import pytest
import requests_mock

from crtools import load_config_file
from crtools import gdoc

__config_file__ =  '''
[google_docs]
api_key=FAKE_KEY
sheet_id=FAKE_SHEET_ID

[crtools]
debug=True
'''

class MockSheetExecute:
    dataset = []
    def __init__(self, data):
        self.dataset = data
    def execute(self):
        return self
    def get(self, arg1, arg2):
        return self.dataset

class MockSheet:
    def spreadsheets(self):
        return self
    def values(self):
        return self
    def get(self, spreadsheetId, range):
        if range == gdoc.DEMERIT_RANGE:
            return MockSheetExecute([
                ['member_name', '#AAA', 'action', 'blacklist', 'reporter', 'date', 'notes'],
                ['member_name', '#BBB', 'action', 'no-promote list', 'reporter', 'date', 'notes']
            ])
        else:
            return MockSheetExecute([
                ['member_name', '#CCC', 'start_date', '1/1/3000', 'notes']
            ])


def test_get_member_data_from_sheets_no_google_doc_config_does_nothing():
    config = load_config_file()

    config = gdoc.get_member_data_from_sheets(config)

    assert config['members']['blacklist'] == []
    assert config['members']['no_promote'] == []
    assert config['members']['vacation'] == []

def test_get_member_data_from_sheets_no_api_key_does_nothing(tmpdir, capsys):
    """ Sections and properties in INI files should never be added to
    config object if they aren't in the template """

    config_file = tmpdir.mkdir('test_get_member_data_from_sheets_no_api_key_does_nothing').join('config.ini')
    config_file.write("""
[google_docs]
api_key=FAKE_KEY

[crtools]
debug=True
""")

    config = load_config_file(config_file.realpath())

    config = gdoc.get_member_data_from_sheets(config)

    assert config['members']['blacklist'] == []
    assert config['members']['no_promote'] == []
    assert config['members']['vacation'] == []

def test_get_member_data_from_sheets_no_sheet_id_does_nothing(tmpdir, capsys):
    """ Sections and properties in INI files should never be added to
    config object if they aren't in the template """

    config_file = tmpdir.mkdir('test_get_member_data_from_sheets_no_api_key_does_nothing').join('config.ini')
    config_file.write("""
[google_docs]
sheet_id=FAKE_SHEET_ID

[crtools]
debug=True
""")

    config = load_config_file(config_file.realpath())

    config = gdoc.get_member_data_from_sheets(config)

    assert config['members']['blacklist'] == []
    assert config['members']['no_promote'] == []
    assert config['members']['vacation'] == []

def test_get_member_data_from_sheets_mock_data(tmpdir, monkeypatch):
    def mock_get_sheet(*args, **kwargs):
        return MockSheet()

    monkeypatch.setattr(gdoc, "get_sheet", mock_get_sheet)

    config_file = tmpdir.mkdir('test_get_member_data_from_sheets_no_api_key_does_nothing').join('config.ini')
    config_file.write(__config_file__)

    config = load_config_file(config_file.realpath())


    config = gdoc.get_member_data_from_sheets(config)

    assert config['members']['blacklist'] == ['#AAA']
    assert config['members']['no_promote'] == ['#BBB']
    assert config['members']['vacation'] == ['#CCC']

def test_get_member_data_from_sheets_null_sheets_object(tmpdir, monkeypatch):
    def mock_get_sheet(*args, **kwargs):
        return None

    monkeypatch.setattr(gdoc, "get_sheet", mock_get_sheet)

    config_file = tmpdir.mkdir('test_get_member_data_from_sheets_no_api_key_does_nothing').join('config.ini')
    config_file.write(__config_file__)

    config = load_config_file(config_file.realpath())

    config = gdoc.get_member_data_from_sheets(config)

    assert config['members']['blacklist'] == []
    assert config['members']['no_promote'] == []
    assert config['members']['vacation'] == []
