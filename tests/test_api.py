from crtools import api

def test_debug(capsys):
    api_obj = api.ClashRoyaleAPI('', '', True)

    # name de-mangling for private method
    api_obj._ClashRoyaleAPI__debug('foo')

    captured = capsys.readouterr()
    assert captured.out.strip() == '[ClashRoyaleAPI]: foo'
