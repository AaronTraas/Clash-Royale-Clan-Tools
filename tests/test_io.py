import json

from crtools import io

def test_write_object_to_file(tmpdir):
    config_file = tmpdir.mkdir('test_write_object_to_file').join('testfile')

    file_path = config_file.realpath()
    file_contents_text = 'hello world!'
    file_contents_object = {'foo': 'bar'}

    io.write_object_to_file(file_path, file_contents_text)

    with open(file_path, 'r') as myfile:
        file_out_contents = myfile.read()

    assert file_contents_text == file_out_contents

    io.write_object_to_file(file_path, file_contents_object)

    with open(file_path, 'r') as myfile:
        file_out_contents = myfile.read()

    assert file_contents_object == json.loads(file_out_contents)

def test_get_previous_history(tmpdir):
    fake_output_dir = tmpdir.mkdir('test_get_previous_history')
    history_file = fake_output_dir.join(io.HISTORY_FILE_NAME)

    fake_history_content = '{"foo":"bar"}'
    fake_history_obj = json.loads(fake_history_content)

    history_file.write(fake_history_content)

    dir_path = fake_output_dir.realpath()

    assert io.get_previous_history(None) == None
    assert io.get_previous_history('/obviously/fake/dir') == None
    assert io.get_previous_history(dir_path) == fake_history_obj

def test_copy_static_assets(tmpdir):
    fake_tempdir = tmpdir.mkdir('test_copy_static_assets')
    logo_source = fake_tempdir.join('fake_logo')
    favicon_source = fake_tempdir.join('fake_favicon')

    logo_source.write('foo')
    favicon_source.write('bar')

    io.copy_static_assets(fake_tempdir.realpath(), logo_source.realpath(), favicon_source.realpath())

    assert fake_tempdir.join('static').check(dir=1)
    assert fake_tempdir.join('static').join('images').check(dir=1)
    assert fake_tempdir.join(io.CLAN_LOG_FILENAME).read() == 'foo'
    assert fake_tempdir.join(io.FAVICON_FILENAME).read() == 'bar'

def test_dump_debug_logs(tmpdir):
    fake_tempdir = tmpdir.mkdir('test_dump_debug_logs')
    obj = {'foo': 'bar'}
    obj_name = 'test'
    obj2 = {'baz': 'quux'}
    obj2_name = 'test2'

    io.dump_debug_logs(fake_tempdir.realpath(), {obj_name: obj, obj2_name: obj2})

    log_dir = fake_tempdir.join('log')
    out_obj = json.loads(log_dir.join(obj_name+'.json').read())
    out_obj2 = json.loads(log_dir.join(obj2_name+'.json').read())

    assert obj == out_obj
    assert obj2 == out_obj2

def test_move_temp_to_output_dir(tmpdir):
    fake_tempdir = tmpdir.mkdir('test_move_temp_to_output_dir-temp')
    fake_output_dir = tmpdir.mkdir('test_move_temp_to_output_dir-output')

    test_file_name = 'test.txt'
    test_file_contents = 'foo'
    test_subdir_name = 'bar'
    test_out_existing_filename = 'baz.txt'
    test_out_existing_dirname = 'quux'
    fake_tempdir.join(test_file_name).write(test_file_contents)
    fake_tempdir.mkdir(test_subdir_name)
    fake_output_dir.join(test_out_existing_filename).write(test_out_existing_filename)
    fake_output_dir.mkdir(test_out_existing_dirname)

    io.move_temp_to_output_dir(fake_tempdir.realpath(), fake_output_dir.realpath())

    out_file_contents = fake_output_dir.join(test_file_name).read()

    assert out_file_contents == test_file_contents
    assert fake_output_dir.join(test_subdir_name).check(dir=1)
    assert fake_output_dir.join(test_out_existing_filename).check(file=0)
    assert fake_output_dir.join(test_out_existing_dirname).check(dir=0)

def test_move_temp_to_output_dir_output_dir_doesnt_exist(tmpdir):
    fake_tempdir = tmpdir.mkdir('test_move_temp_to_output_dir_output_dir_doesnt_exist-temp')
    fake_output_dir = tmpdir.join('test_move_temp_to_output_dir_output_dir_doesnt_exist-output')

    io.move_temp_to_output_dir(fake_tempdir.realpath(), fake_output_dir.realpath())

def test_move_temp_to_output_dir_output_dir_no_write(tmpdir):
    fake_tempdir = tmpdir.mkdir('test_move_temp_to_output_dir_output_dir_no_write-temp')
    fake_output_dir = tmpdir.mkdir('test_move_temp_to_output_dir_output_dir_no_write-output')
    fake_output_dir.chmod(0)

    io.move_temp_to_output_dir(fake_tempdir.realpath(), fake_output_dir.realpath())
