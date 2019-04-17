import warnings
from karon import RequirementError
from karon.process import (build,
                           vickers,
                           xct)


def test_build():
    # good
    sample = build(name='foobar')
    assert sample.contents['name'] == 'foobar'
    assert sample.readable() and sample.writeable()
    # bad
    try:
        _ = build()
        assert False, "Previous command should have raised exception."
    except RequirementError:
        pass
    except:
        assert False, "Invalid build should raise RequirementError."


def test_vickers():
    # good
    sample = vickers(**{"name": "Phase II",
                        "Hv (HV)": 363})
    assert sample.contents['name'] == 'Phase II'
    assert sample.contents['Hv (HV)'] == 363
    assert sample.readable() and sample.writeable()
    # bad: missing requirement
    try:
        _ = vickers()
        assert False, "Previous command should have raised exception."
    except RequirementError:
        pass
    except:
        assert False, "Invalid build should raise RequirementError."
    # bad: missing expects
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        _ = vickers(name="Phase II")
        assert len(w) == 1, \
            "Failed to catch warning when expected argument is missing."


def test_xct():
    # good
    sample = xct(**{"name": "Zeiss",
                    "Voltage (kV)": 140,
                    "Power (W)": 10})
    assert sample.contents['name'] == 'Zeiss'
    assert sample.contents['Voltage (kV)'] == 140
    assert sample.contents['Power (W)'] == 10
    assert sample.readable() and sample.writeable()
    # bad: missing required
    try:
        _ = xct()
        assert False, "Previous command should have raised exception."
    except RequirementError:
        pass
    except:
        assert False, "Invalid build should raise RequirementError."
    # bad: missing expects
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        _ = xct(name="Zeiss")
        assert len(w) > 0, \
            "Failed to catch warning when expected argument is missing."
