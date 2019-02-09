import json
import os
import shutil
from crtools import crtools, load_config_file

def test_write_object_to_file(tmpdir):
    config_file = tmpdir.mkdir('test_write_object_to_file').join('testfile')

    file_path = config_file.realpath()
    file_contents_text = 'hello world!'
    file_contents_object = {'foo': 'bar'}

    crtools.write_object_to_file(file_path, file_contents_text)

    with open(file_path, 'r') as myfile:
        file_out_contents = myfile.read()

    assert file_contents_text == file_out_contents

    crtools.write_object_to_file(file_path, file_contents_object)

    with open(file_path, 'r') as myfile:
        file_out_contents = myfile.read()

    assert file_contents_object == json.loads(file_out_contents)

def test_get_war_league_from_score():
    assert crtools.get_war_league_from_score(200)['name'] == 'Bronze League'
    assert crtools.get_war_league_from_score(1501)['name'] == 'Gold League'
    assert crtools.get_war_league_from_score(99999999999999)['name'] == 'Legendary League'