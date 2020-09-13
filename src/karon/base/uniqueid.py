from .serialize import Serializable

import json
from collections.abc import Hashable

import logging
_logger = logging.getLogger(__name__)

try:
    from petname import generate
    from functools import partial
    generator = partial(generate, words=3)
    uuid = lambda: "-".join([generator(), "meets", generator()])
except:
    _logger.debug("Failed to load requirements for human readable UIDs.")
    from uuid import uuid4 as uuid

class UniqueID(Hashable, Serializable):
    def __init__(self, uid=None):
        """
        Unique identifier for an object. This is not intended to be
        instantiated directly, but used as a base class for objects whose
        instances should be uniquely identifiable.

        Parameters
        ==========
        :param uid: Unique identifier to use for this object. Typically this
            is not specified unless the UniqueID is being reconstructed from
            a persistent source, such as JSON package.
        :type uid: str, int, or other hashable object.
        """
        if uid is None:
            self.__uid = uuid()
        elif isinstance(uid, UniqueID):
            self.__uid = uid.uid
        else:
            self.__uid = uid

    def __hash__(self):
        return hash(self.__uid)

    def __le__(self, rhs):
        return hash(self) <= hash(rhs)

    def __ge__(self, rhs):
        return hash(self) >= hash(rhs)

    @property
    def uid(self):
        return self.__uid

    def tojson(self):
        return {
            "uid": self.uid
        }

    @classmethod
    def fromjson(cls, obj):
        return cls(obj.get("uid", None))
