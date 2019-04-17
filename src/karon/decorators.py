from karon.exceptions import RequirementError
from functools import wraps
# from uuid import uuid4 as uuid
# import petname
import warnings


# name = lambda: petname.generate(3)
# uid = lambda: str(uuid())


def expects(*keys, **defaults):
    keys = keys + tuple(defaults.keys())
    def wrapper(proc):
        @wraps(proc)
        def func(**attributes):
            kwds = dict(defaults)
            kwds.update(attributes)
            for k in keys:
                if k not in kwds:
                    warnings.warn(f"{func.__name__} expects {k}", UserWarning)
            return proc(**kwds)
        return func
    return wrapper


def requires(*keys, **defaults):
    keys = keys + tuple(defaults.keys())
    def wrapper(proc):
        @wraps(proc)
        def func(**attributes):
            kwds = dict(defaults)
            kwds.update(attributes)
            for k in keys:
                if k not in kwds:
                    raise RequirementError(f"{func.__name__} requires {k}")
            return proc(**kwds)
        return func
    return wrapper


def readwrite(proc):
    @wraps(proc)
    def func(**attributes):
        kwds = {
            'readable': True,
            'writeable': True
        }
        kwds.update(attributes)
        return proc(**kwds)
    return func


def readable(proc):
    @wraps(proc)
    def func(**attributes):
        kwds = {
            'readable': True,
            'writeable': False
        }
        kwds.update(attributes)
        return proc(**kwds)
    return func


def writeable(proc):
    @wraps(proc)
    def func(**attributes):
        kwds = {
            'readable': False,
            'writeable': True
        }
        kwds.update(attributes)
        return proc(**kwds)
    return func


def immutable(proc):
    @wraps(proc)
    def func(**attributes):
        kwds = {
            'readable': False,
            'writeable': False
        }
        kwds.update(attributes)
        return proc(**kwds)
    return func

