import requests_mock
import os

from crtools import fankit

def test_get_fankit_exists(tmpdir):
    tempdir_root = tmpdir.mkdir('test_get_fankit_exists')
    fake_tempdir = tempdir_root.mkdir('tempdir')
    fake_output_dir = tempdir_root.mkdir('output_dir')
    fake_output_dir.mkdir(fankit.FANKIT_DIR_NAME)

    fankit.get_fankit(fake_tempdir.realpath(), fake_output_dir.realpath())

    assert fake_tempdir.join(fankit.FANKIT_DIR_NAME).check(dir=1)

def test_get_fankit_download(tmpdir, requests_mock):
    test_fankit_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fankit.zip')

    with open(test_fankit_path, mode='rb') as file:
        test_fankit_content = file.read()

    redirect_headers = {
        'Location': fankit.FANKIT_URL
    }
    requests_mock.get(fankit.FANKIT_URL, headers=redirect_headers, content=test_fankit_content, status_code=200)

    tempdir_root = tmpdir.mkdir('test_get_fankit_download')
    fake_tempdir = tempdir_root.mkdir('tempdir')
    fake_output_dir = tempdir_root.mkdir('output_dir')

    fankit.get_fankit(fake_tempdir.realpath(), fake_output_dir.realpath())

    assert fake_tempdir.join(fankit.FANKIT_DIR_NAME).check(dir=1)

def test_get_fankit_download_no_redirect(tmpdir, requests_mock, capsys):
    requests_mock.get(fankit.FANKIT_URL, status_code=200)

    tempdir_root = tmpdir.mkdir('test_get_fankit_download')
    fake_tempdir = tempdir_root.mkdir('tempdir')
    fake_output_dir = tempdir_root.mkdir('output_dir')

    fankit.get_fankit(fake_tempdir.realpath(), fake_output_dir.realpath())

    #assert False
    assert fake_tempdir.join(fankit.FANKIT_DIR_NAME).check(dir=0)

def test_get_fankit_download_fail(tmpdir, requests_mock, capsys):
    requests_mock.get('mock://foo', status_code=500)

    tempdir_root = tmpdir.mkdir('test_get_fankit_download')
    fake_tempdir = tempdir_root.mkdir('tempdir')
    fake_output_dir = tempdir_root.mkdir('output_dir')

    fankit.get_fankit(fake_tempdir.realpath(), fake_output_dir.realpath())

    assert fake_tempdir.join(fankit.FANKIT_DIR_NAME).check(dir=0)
