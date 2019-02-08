import json
import os
import shutil
import tempfile
from crtools import crtools

def test_write_object_to_file():
    tempdir = tempfile.mkdtemp('crtools_test_test_write_object_to_file')

    file_path = os.path.join(tempdir, 'testfile.tmp')
    file_contents_text = 'hello world!'
    file_contents_object = {'foo': 'bar'}

    try:
    	# Try text
        crtools.write_object_to_file(file_path, file_contents_text)

        with open(file_path, 'r') as myfile:
            file_out_contents = myfile.read()

        assert file_contents_text == file_out_contents

        crtools.write_object_to_file(file_path, file_contents_object)

        with open(file_path, 'r') as myfile:
            file_out_contents = myfile.read()

        assert file_contents_object == json.loads(file_out_contents)

        # Try object
    finally:
        shutil.rmtree(tempdir)
