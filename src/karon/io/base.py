from ..tree import Node
# import pandas as pd


class BaseIO(dict):
    """
    Base class to provide a common API to access node data from files,
    databases, etc.

    Readers ingest data from a source--a file, database, string, etc.--and
    generates nodes from that data. The actual generation is handled by a
    generator function, for example,

    .. code-block :: python

        @readwrite
        @requires("foo")
        @expects("bar")
        def makeFooBar(**contents):
            return Node(**contents)

        reader = MyReader(foobar=makeFooBar)

    A default generator can be specified using the ``set_default`` method.

    .. note::
        It is up to the derived class to provide the necessary context
        for these entries. For example, populating the map with a string
        derived from a filename as the key and the generator function as
        the value.
    """
    def __init__(self, *args, **kwds):
        if 'default' in kwds:
            default = kwds['default']
            del kwds['default']
        else:
            default = None
        super().__init__(*args, **kwds)
        self._default = default
        self._nodes = []

    def __getitem__(self, item):
        return self.get(item, self.get_default())

    def set_default(self, value):
        self._default = value

    def get_default(self):
        return self._default

    @property
    def nodes(self):
        return self._nodes

    def load(self, fobj, *args, **kwds):
        raise NotImplementedError('Derived classes must implement `load` '
                                  'to read contents from a file.')

    def dump(self, fobj, *args, **kwds):
        raise NotImplementedError('Derived classes must implement `dump` '
                                  'to write contents to a file.')
