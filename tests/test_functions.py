#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import unittest
import numpy as np
from karon.base.util import ensure_float
from karon.graph import Attribute, AttributeSet
from karon.functions import (state, mean, median, std)

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
        attrs = AttributeSet()
        attrs.add(Attribute("foo", 1))
        attrs.add(Attribute("bar", 2))
        attrs.add(Attribute("baz", 3))
        attrs.add(Attribute("goo", 4))
        attrs.add(Attribute("ber", 'a'))
        attrs.add(Attribute("goober", 3))
        # set some synonyms
        for attr in attrs.get("foo"):
            attr.add("foobar")
            attr.add("foobaz")
            attr.add("foobarbaz")
        for attr in attrs.get("bar"):
            attr.add("foobar")
            attr.add("foobarbaz")
        for attr in attrs.get("baz"):
            attr.add("foobaz")
            attr.add("foobarbaz")
        for attr in attrs.get("goo"):
            attr.add("goober")
        for attr in attrs.get("ber"):
            attr.add("goober")
        self.attrs = attrs
        # print
        # self.logger.info(f"Attributes:\n{attrs.dumps(indent=4)}")

    def tearDown(self):
        self.logger.removeHandler(self.handler)

    def test_state(self):
        def mymin(aset):
            return np.nanmin([ensure_float(x.value) for x in aset])

        def mydot(aset, bset):
            x1 = np.array([ensure_float(x.value) for x in aset])
            x2 = np.array([ensure_float(x.value) for x in bset])
            return np.nansum(np.multiply(x1, x2))

        for key, value in (("foo", 1),
                           ("bar", 2),
                           ("baz", 3),
                           ("foobar", 1),
                           ("foobaz", 1),
                           ("foobarbaz", 1),
                           ("goober", 3)):
            dest = f"min {key}"
            fmin = state(dest, aset=key)(mymin)
            attrs = fmin(self.attrs)
            values = [attr.value for attr in attrs.get(dest)]
            self.assertTrue(len(values), 1)
            self.assertEqual(values[0], value, f"min({key}) = {values[0]} != value.")
            self.assertIs(attrs, self.attrs)
        for k1, k2, value in (("foo", "bar", 2),
                           ("bar", "baz", 6),
                           ("foobarbaz", "foobarbaz", 14),
                           ("goober", "goober", 25)):
            dest = f"rsq({k1}, {k2})"
            fdot = state(dest, aset=k1, bset=k2)(mydot)
            attrs = fdot(self.attrs)
            values = [attr.value for attr in attrs.get(dest)]
            self.assertTrue(len(values), 1)
            self.assertEqual(values[0], value, f"dot({k1}, {k2}) = {values[0]} != {value}.")
            self.assertIs(attrs, self.attrs)

    def test_mean(self):
        # self.logger.info("Testing mean")
        for key, value in (("foo", 1),
                           ("bar", 2),
                           ("baz", 3),
                           ("foobar", 1.5),
                           ("foobaz", 2),
                           ("foobarbaz", 2),
                           ("goober", 3.5)):
            dest = f"mean {key}"
            attrs = mean(key)(self.attrs)
            values = [attr.value for attr in attrs.get(dest)]
            self.assertEqual(values, [value], f"mean({key}) failed.")
            self.assertIs(attrs, self.attrs)
        # barbaz
        dest = "mean barbaz"
        attrs = mean("barbaz", dest)(self.attrs)
        values = [attr.value for attr in attrs.get(dest)]
        self.assertEqual(values, [])
        self.assertIs(attrs, self.attrs)

    def test_median(self):
        # self.logger.info("Testing median")
        for key, value in (("foo", 1),
                           ("bar", 2),
                           ("baz", 3),
                           ("foobar", 1.5),
                           ("foobaz", 2),
                           ("foobarbaz", 2),
                           ("goober", 3.5)):
            dest = f"median {key}"
            attrs = median(key)(self.attrs)
            values = [attr.value for attr in attrs.get(dest)]
            self.assertEqual(values, [value], f"median({key}) failed.")
            self.assertIs(attrs, self.attrs)
        # barbaz
        dest = "median barbaz"
        attrs = median("barbaz", dest)(self.attrs)
        values = [attr.value for attr in attrs.get(dest)]
        self.assertEqual(values, [])
        self.assertIs(attrs, self.attrs)

    def test_std(self):
        # self.logger.info("Testing std")
        for key, value in (("foo", 0),
                           ("bar", 0),
                           ("baz", 0),
                           ("foobar", 0.5),
                           ("foobaz", 1),
                           ("foobarbaz", 0.816496580927726),
                           ("goober", 0.5)):
            dest = f"std {key}"
            attrs = std(key)(self.attrs)
            values = [attr.value for attr in attrs.get(dest)]
            self.assertTrue(len(values), 1)
            self.assertAlmostEqual(values[0], value,
                            f"std({key}) failed: {values[0]} != {value}.")
            self.assertIs(attrs, self.attrs)
        # barbaz
        dest = "std barbaz"
        attrs = std("barbaz", dest)(self.attrs)
        values = [attr.value for attr in attrs.get(dest)]
        self.assertEqual(values, [])
        self.assertIs(attrs, self.attrs)
