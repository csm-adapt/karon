#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import unittest
import numpy as np
from karon.graph import Attributes
from karon.functions import (mean,
                             median,
                             std)

import logging
# _logger = logging.getLogger(__name__)

__author__ = "Branden Kappes"
__copyright__ = "KMMD, LLC."
__license__ = "mit"


class TestFunctions(unittest.TestCase):
    def setUp(self):
        self.handler = logging.StreamHandler(sys.stdout)
        self.logger = logging.getLogger("unittestLogger")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(self.handler)
        # construct a known set of attributes
        attrs = Attributes()
        attrs["foo"] = 1
        attrs["bar"] = 2
        attrs["baz"] = 3
        attrs.add_synonym("foo", "foobar")
        attrs.add_synonym("bar", "foobar")
        attrs.add_synonym("foo", "foobaz")
        attrs.add_synonym("baz", "foobaz")
        attrs.add_synonym("foo", "foobarbaz")
        attrs.add_synonym("bar", "foobarbaz")
        attrs.add_synonym("baz", "foobarbaz")
        self.attrs = attrs
        # print
        msg = "\n".join(["    " + str(k) + ": " + str(v)
                        for k,v in self.attrs.items()])
        self.logger.info(f"Attributes:\n{msg}")

    def tearDown(self):
        self.logger.removeHandler(self.handler)

    def test_mean(self):
        self.logger.info("Testing mean")
        for key, value in (("foo", 1),
                           ("bar", 2),
                           ("baz", 3),
                           ("foobar", 1.5),
                           ("foobaz", 2),
                           ("foobarbaz", 2)):
            dest = f"mean {key}"
            rval = mean(key)(self.attrs)
            self.assertEqual(rval[dest], [value], f"mean({key}) failed.")
            self.assertIsNot(rval, self.attrs)
        # barbaz
        rval = mean("barbaz")(self.attrs)
        self.assertEqual(rval["barbaz"], [])
        self.assertIs(rval, self.attrs)

    def test_median(self):
        self.logger.info("Testing median")
        for key, value in (("foo", 1),
                           ("bar", 2),
                           ("baz", 3),
                           ("foobar", 1.5),
                           ("foobaz", 2),
                           ("foobarbaz", 2)):
            dest = f"median {key}"
            rval = median(key)(self.attrs)
            self.assertEqual(rval[dest], [value], f"median({key}) failed.")
            self.assertIsNot(rval, self.attrs)
        # barbaz
        rval = median("barbaz")(self.attrs)
        self.assertEqual(rval["barbaz"], [])
        self.assertIs(rval, self.attrs)

    def test_std(self):
        self.logger.info("Testing std")
        for key, value in (("foo", 0),
                           ("bar", 0),
                           ("baz", 0),
                           ("foobar", 0.5),
                           ("foobaz", 1),
                           ("foobarbaz", 0.816496580927726)):
            dest = f"std {key}"
            rval = std(key)(self.attrs)
            self.assertAlmostEqual(rval[dest], [value],
                                   f"std({key}) failed.")
            self.assertIsNot(rval, self.attrs)
        # barbaz
        rval = std("barbaz")(self.attrs)
        self.assertEqual(rval["barbaz"], [])
        self.assertIs(rval, self.attrs)
