from convey.sample import Sample


def test_sample():
    package = dict(foo='bar')
    default = Sample()
    populated = Sample(**package)
    readable = Sample(**package, readable=True, writeable=False)
    writeable = Sample(**package, readable=False, writeable=True)
    immutable = Sample(**{**package,
                          **dict(readable=False, writeable=False)})
    assert default.readable() and default.writeable()
    assert populated.readable() and populated.writeable()
    for k,v in iter(package.items()):
        assert populated.contents[k] == v
    assert readable.readable() and not readable.writeable()
    for k, v in iter(package.items()):
        assert readable.contents[k] == v
    assert not writeable.readable() and writeable.writeable()
    for k, v in iter(package.items()):
        assert writeable.contents[k] == v
    assert not immutable.readable() and not immutable.writeable()
    for k, v in iter(package.items()):
        assert immutable.contents[k] == v
