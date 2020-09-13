# General utility functions


def ensure_iterable(x):
    """
    Ensure that the parameter is an iterable, but not a string. (A string
    is an iterable object, but is often a single concept--such as word--
    rather than a container, per se.).

    Parameters
    ==========
    :param x: Object whose iterability is to be ensured.
    :type x: Object

    :returns: The object itself, if an iterable and not a string, or the
        object wrapped in a list.
    :rtype: Iterable.
    """
    if hasattr(x, '__iter__') and not isinstance(x, str):
        return x
    return [x]


def ensure_float(x):
    """
    Ensure that the value is a float.

    Parameters
    ==========
    :param x: Object to be ensured a float.
    :type x: Object that may, or may not, be convertable to a float.

    :returns: `x` cast as a float. If not castable to float, return NaN.
    :rtype: float
    """
    try:
        return float(x)
    except ValueError:
        return float('NaN')
