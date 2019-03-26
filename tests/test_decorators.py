import pytest
import warnings
from convey import RequirementError
from convey.decorators import expects, requires
from convey.decorators import (readwrite,
                               readable,
                               writeable,
                               immutable)


def test_expects():
    @expects("first", "last")
    def name(**kwds):
        return kwds

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        # bad
        result = name(first="Bob")
        assert result['first'] == 'Bob', \
            "Wrapped function results were unexpected."
        assert len(w) == 1, \
            "Failed to catch warning when expected argument is missing."
        assert issubclass(w[-1].category, UserWarning)
        assert "last" in str(w[-1].message)
        # good
        result = name(first="Bob", last="Marley")
        assert result['first'] == 'Bob' and result['last'] == 'Marley', \
            "Wrapped function results were unexpected."
        assert len(w) == 1, \
            "A second warning was caught and shouldn't have been."

    # with defaults
    @expects("first", last="Marsh")
    def bar(**kwds):
        return kwds

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        # good: uses defaults
        result = bar(first="Bob")
        assert result['first'] == 'Bob' and result['last'] == 'Marsh', \
            "Wrapped function results were unexpected."
        assert len(w) == 0, \
            "Unexpected warning when default argument is missing."
        # bad: no expected specified
        result = bar(last="Cisse")
        assert result['last'] == 'Cisse'
        assert 'first' not in result, \
            "first residual from previous call to bar."
        assert len(w) == 1, \
            "Failed to catch warning when expected argument is missing."
        assert issubclass(w[-1].category, UserWarning)
        assert "first" in str(w[-1].message)
        # good
        result = bar(first="Bob", last="Marley")
        assert result['first'] == 'Bob' and result['last'] == 'Marley', \
            "Wrapped function results were unexpected."
        assert len(w) == 1, \
            "A second warning was caught and shouldn't have been."


def test_requires():
    @requires("title")
    def movie(**kwds):
        return kwds

    try:
        results = movie()
        assert results is None, \
            "Shouldn't get here. " \
            "The previous command should have raised an exception."
    except RequirementError:
        pass
    else:
        assert False, \
            "Requirement did not raise the expected error."
    results = movie(title="Dumb and Dumber")
    assert results['title'] == "Dumb and Dumber", \
        "Required function results were unexpected"

    # with defaults
    @requires("title", broadway=False)
    def musical(**kwds):
        return kwds

    # bad
    try:
        results = musical()
        assert results is None, \
            "Shouldn't get here. " \
            "The previous command should have raised an exception."
    except RequirementError:
        pass
    else:
        assert False, \
            "Requirement did not raise the expected error."
    # good, uses defaults
    title = "Rosencrantz and Gildenstern are Dead"
    results = musical(title=title)
    assert (results["title"] == title) and (not results["broadway"]), \
        "Unexpected options passed to the function."
    # good
    results = musical(title="Dumb and Dumber", broadway=True)
    assert results['title'] == "Dumb and Dumber" and results['broadway'], \
        "Required function results were unexpected"


def test_readwrite():
    @readwrite
    def foo(**kwds):
        return kwds
    result = foo()
    assert 'readable' in result, \
        "'readable' must be defined."
    assert result['readable'], \
        "'readable' must be True."
    assert 'writeable' in result, \
        "'writeable' must be defined."
    assert result['writeable'], \
        "'writeable' must be True."


def test_readable():
    @readable
    def foo(**kwds):
        return kwds
    result = foo()
    assert 'readable' in result, \
        "'readable' must be defined."
    assert result['readable'], \
        "Readable must be True."


def test_writeable():
    @writeable
    def foo(**kwds):
        return kwds
    result = foo()
    assert 'writeable' in result, \
        "'writeable' must be defined."
    assert result['writeable'], \
        "'writeable' must be True."


def test_immutable():
    @immutable
    def foo(**kwds):
        return kwds
    result = foo()
    assert 'readable' in result, \
        "'readable' must be defined."
    assert not result['readable'], \
        "'readable' must be False"
    assert 'writeable' in result, \
        "The keyword 'writeable' must be defined."
    assert not result['writeable'], \
        "'writeable' must be False."

def test_combinations():
    @requires("first", "last")
    @immutable
    def name(**kwds):
        return kwds
    # bad: first/last not specified
    try:
        result = name()
    except RequirementError:
        pass
    except:
        assert False, \
            "requires + readwrite did not return the right exception."
    # good
    result = name(first="Anna", last="Kappes")
    assert (result['first'] == 'Anna' and \
            result['last'] == 'Kappes' and \
            not result['readable'] and \
            not result['writeable']), \
        "requires + immutable attributes not set as expected."
