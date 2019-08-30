from crtools import discord, load_config_file
from datetime import datetime, timedelta
import logging

__config_file__ = '''
[discord]
webhook_default=https://fakewebhook
webhook_war_nag=https://fakewebhook
nag_collection_battle=True
nag_war_battle=True
nag_war_battle_hours_left=24
nag_collection_battle_hours_left=24
'''

__config_file_no_nag__ = '''
[discord]
webhook_default=https://fakewebhook
nag_collection_battle=False
nag_war_battle=False
'''

__config_file_no_threshold__ = '''
[discord]
webhook_default=https://fakewebhook
webhook_war_nag=https://fakewebhook
nag_collection_battle=True
nag_war_battle=True
nag_war_battle_hours_left=0
nag_collection_battle_hours_left=0
'''

def test_trigger_webhooks_no_url_returns_false(tmpdir):
    config_file = tmpdir.mkdir('test_trigger_webhooks_no_url_returns_false').join('testfile')
    config_file.write('')
    config = load_config_file(config_file.realpath())

    result = discord.trigger_webhooks(config, None, None)

    assert result == False

def test_trigger_webhooks_no_nag_returns_false(tmpdir):
    config_file = tmpdir.mkdir('test_trigger_webhooks_no_nag_returns_false').join('testfile')
    config_file.write(__config_file_no_nag__)
    config = load_config_file(config_file.realpath())

    assert discord.trigger_webhooks(config, {'state': 'collectionDay'}, None) == True
    assert discord.trigger_webhooks(config, {'state': 'warDay'}, None) == True

def test_send_war_nag_not_in_war_returns_false(tmpdir):
    config_file = tmpdir.mkdir('test_send_war_nag_not_in_war_returns_false').join('testfile')
    config_file.write(__config_file__)
    config = load_config_file(config_file.realpath())

    assert discord.send_war_nag(config, {'state': 'notInWar'}, None) == True

def test_send_war_nag_collection_no_members_returns_true(tmpdir):

    config_file = tmpdir.mkdir('test_send_war_nag_collection_no_members_returns_true').join('testfile')
    config_file.write(__config_file__)
    config = load_config_file(config_file.realpath())

    fake_current_war = {
    	'state': 'collectionDay',
    	'collection_end_time': datetime.utcnow().strftime("%Y%m%dT%H%M%S.xxxx"),
    	'participants': []
    }

    assert discord.send_war_nag(config, fake_current_war, []) == True

def test_send_war_nag_war_no_members_returns_true(tmpdir):
    config_file = tmpdir.mkdir('test_send_war_nag_war_no_members_returns_true').join('testfile')
    config_file.write(__config_file__)
    config = load_config_file(config_file.realpath())

    fake_current_war = {
    	'state': 'warDay',
    	'war_end_time': datetime.utcnow().strftime("%Y%m%dT%H%M%S.xxxx"),
    	'participants': []
    }

    assert discord.send_war_nag(config, fake_current_war, []) == True

def test_send_war_nag_threshold_not_met_returns_true(tmpdir):

    config_file = tmpdir.mkdir('test_send_war_nag_threshold_not_met_returns_true').join('testfile')
    config_file.write(__config_file_no_threshold__)
    config = load_config_file(config_file.realpath())

    fake_current_war = {
    	'state': 'collectionDay',
    	'collection_end_time': datetime.utcnow().strftime("%Y%m%dT%H%M%S.xxxx"),
    	'participants': []
    }

    assert discord.send_war_nag(config, fake_current_war, []) == True

def test_send_war_nag_participants_completed_returns_false_because_url_invalid(tmpdir):

    config_file = tmpdir.mkdir('test_send_war_nag_threshold_not_met_returns_true').join('testfile')
    config_file.write(__config_file__)
    config = load_config_file(config_file.realpath())

    fake_current_war = {
    	'state': 'collectionDay',
    	'collection_end_time': datetime.utcnow().strftime("%Y%m%dT%H%M%S.xxxx"),
    	'participants': [
    		{
    			'name': 'AAA',
    			'tag': '#AAA',
    			'battles_played': 1,
    			'number_of_battles': 3
    		},
    		{
    			'name': 'BBB',
    			'tag': '#BBB',
    			'battles_played': 1,
    			'number_of_battles': 3
    		}
    	]
    }

    fake_members = [{'tag': '#AAA'}]

    assert discord.send_war_nag(config, fake_current_war, fake_members) == False
