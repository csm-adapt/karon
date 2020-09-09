#
# State functions.
#

from .graph import Attributes
from copy import deepcopy
from functools import wraps
from abc import ABC, abstractmethod
import numpy as np

import logging
_logger = logging.getLogger(__name__)


class StateFunction(ABC):
    def __init__(self, dest, func, *keys):
        self._keys = keys
        self._dest = dest
        self._func = func

    @abstractmethod
    def __call__(self, attr : Attributes) -> Attributes:
        return {k:attr[k] for k in self._keys}


# ######################### Unary Functions ######################### #

class UnaryFunction(StateFunction):
    def __init__(self, dest, func, key):
        super().__init__(dest, func, key)

    def __call__(self, attr : Attributes) -> Attributes:
        key = self._keys[0]
        dst = self._dest
        values = super().__call__(attr)[key]
        _logger.debug(f"UnaryFunction(key, values) = ({key}, {values})")
        if len(values) == 0:
            return attr
        else:
            rval = deepcopy(attr)
            rval[dst] = self._func(values)
            return rval


class mean(UnaryFunction):
    def __init__(self, key, dest=None):
        dest = f"mean {key}" if dest is None else dest
        _logger.debug(f"Calculating the mean of {key} --> {dest}")
        super().__init__(dest, np.mean, key)


class median(UnaryFunction):
    def __init__(self, key, dest=None):
        dest = f"median {key}" if dest is None else dest
        _logger.debug(f"Calculating the median of {key} --> {dest}")
        super().__init__(dest, np.median, key)


class std(UnaryFunction):
    def __init__(self, key, dest=None):
        dest = f"std {key}" if dest is None else dest
        _logger.debug(f"Calculating the std of {key} --> {dest}")
        super().__init__(dest, np.std, key)
