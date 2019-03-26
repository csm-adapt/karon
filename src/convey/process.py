from convey import Sample
from convey.decorators import requires, expects
from convey.decorators import (readwrite)


@requires("name")
@readwrite
def build(**attributes):
    return Sample(**attributes)


@requires("name")
@expects("Hv (HV)")
@readwrite
def vickers(**attributes):
    return Sample(**attributes)


@requires("name")
@expects("Voltage (kV)", "Power (W)")
@readwrite
def xct(**attributes):
    return Sample(**attributes)