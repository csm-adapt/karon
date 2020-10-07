#
# State functions.
#

from .base.util import ensure_float
from .graph import Attribute, AttributeSet
import numpy as np
from functools import update_wrapper

import logging
_logger = logging.getLogger(__name__)


class StateFunction:
    def __init__(self, dest, func, *keys, **remap):
        """
        The general form of the constructor for a StateFunction
        is the name of the destination key, an executable function,
        and a list of keys necessary to execute the function.

        Examples are given for unary and binary functions. `state` is a
        wrapper provided for generating a state function object from
        a function of zero-or-more `AttributeSet`s.

        Parameters
        ==========
        :param dest: Destination key name.
        :type dest: str
        :param func: Function that takes no positional parameters, but
            named parameters corresponding to the input keys, possibly
            remapped to make them valid parameter names.
        :type func: Callable.
        :param keys: Attribute names that must be present in the
            AttributeSet for the function to execute.
        :type remap: Dictionary of function variable names to key names, i.e.
            {"functionA": "attribute A", ...}. All parameters to the function
            must be specified in the remap dictionary. No default parameters
            are allowed.
        :param remap: dict

        Examples
        ========

        :python:```
        # calculate the mean of an AttributeSet
        class mean(StateFunction):
            def __init__(self, key, dest=None):
                dest = f"mean({key})" if dest is None else dest
                func = lambda a: np.nanmean([ensure_float(x.value) for x in a])
                super().__init__(dest, func, key, a=key)

        mean_foo = mean("foo")

        # calculate the mean of an AttributeSet
        mean_foo(aset)

        # calculate the inner (dot) product of two `AttributeSet`s
        class dot(StateFunction):
            @staticmethod
            def func(lhs, rhs):
                x1 = [ensure_float(x) for x in lhs]
                x2 = [ensure_float(x) for x in rhs]
                return np.nansum(np.multiply(x1, x2))

            def __init__(self, k1, k2, dest=None):
                dest = f"dot({k1}, {k2})" if dest is None else dest
                super().__init__(dest, dot.func, key, a=key)
        ```
        """
        self._keys = keys
        self._dest = dest
        self._func = func
        # set the remap dictionary.
        self._remap = remap.copy()

    def __call__(self, attrs : AttributeSet):
        params = {k:attrs.get(self._remap[k]) for k in self._remap}
        missing = [self._remap[k] for k,v in params.items() if len(v) == 0]
        if len(missing) > 0:
            _logger.info(f"{type(self)} missing arguments: {missing}.")
            return attrs
        attrs.add(Attribute(names=self._dest, value=self._func(**params)))
        return attrs

# ####################### Register Functions ######################## #
def state(dest, **kwds):
    """
    Create a state function out of a function that takes zero or more
    `AttributeSet`s.

    Example
    =======
    :python:```
    def mymin(aset):
        return np.nanmin([ensure_float(x.value) for x in aset])

    # create a state function that calculates the minimum of all
    # Attributes in an AttributeSet that have a name "hello world".
    state_min = state("min(hello world)", aset="hello world")(mymin)

    def dot(aset, bset):
        x1 = [ensure_float(x.value) for x in aset]
        x2 = [ensure_float(x.value) for x in bset]
        return np.nansum(np.multiply(x1, x2))

    state_dot = state("dot(foo, bar)", aset="foo", bset="bar")(dot)
    ```
    """
    def outer(func):
        class Inner(StateFunction):
            def __init__(self):
                keys = list(kwds.values())
                super().__init__(dest, func, *keys, **kwds)
                update_wrapper(self, func) # to get name and docstring from func
        return Inner()
    return outer


# ######################### Unary Functions ######################### #

class mean(StateFunction):
    def __init__(self, key, dest=None):
        """
        Calculates the mean of a set of values. Any `Attribute.value` that
        cannot be converted to a float is ignored silently.

        Example
        =======
        :python:```
        # Calculate the mean of the values in the `AttributeSet aset`.
        mean("foo")(aset)
        ```
        """
        dest = f"mean {key}" if dest is None else dest
        _logger.debug(f"Mean({key}) --> {dest}")
        super().__init__(dest,
                    lambda a: np.nanmean([ensure_float(x.value) for x in a]),
                    key,
                    a=key)


class median(StateFunction):
    def __init__(self, key, dest=None):
        """
        Calculates the median of a set of values. Any `Attribute.value` that
        cannot be converted to a float is ignored silently.

        Example
        =======
        :python:```
        # Calculate the median of the values in the `AttributeSet aset`.
        median("foo")(aset)
        ```
        """
        dest = f"median {key}" if dest is None else dest
        _logger.debug(f"Median({key}) --> {dest}")
        super().__init__(dest,
                    lambda a: np.nanmedian([ensure_float(x.value) for x in a]),
                    key,
                    a=key)


class std(StateFunction):
    def __init__(self, key, dest=None):
        """
        Calculates the standard deviation  of a set of values. Any
        `Attribute.value` that cannot be converted to a float is ignored
        silently.

        Example
        =======
        :python:```
        # Calculate the std of the values in the `AttributeSet aset`.
        std("foo")(aset)
        ```
        """
        dest = f"std {key}" if dest is None else dest
        _logger.debug(f"Std({key}) --> {dest}")
        super().__init__(dest,
                    lambda a: np.nanstd([ensure_float(x.value) for x in a]),
                    key,
                    a=key)
