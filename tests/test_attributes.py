#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import unittest
from karon.graph import Attributes

import logging
# _logger = logging.getLogger(__name__)

__author__ = "Branden Kappes"
__copyright__ = "KMMD, LLC."
__license__ = "mit"


class TestAttributes(unittest.TestCase):
    def setUp(self):
        self.handler = logging.StreamHandler(sys.stdout)
        self.logger = logging.getLogger("unittestLogger")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(self.handler)
        # create Attributes
        self.attrs = Attributes(foo=1, bar=2, baz=3)
        # add foobar to foo and to bar.
        self.attrs.add_synonym("foo", "foobar")
        self.attrs.add_synonym("bar", "foobar")
        # get a list of keys
        self.keynames = [k.name for k in self.attrs]
        # print
        msg = "\n".join(["    " + str(k) + ": " + str(v)
                        for k,v in self.attrs.items()])
        self.logger.info(f"Attributes:\n{msg}")
        self.logger.info(f"Key names: {self.keynames}")

    def tearDown(self):
        self.logger.removeHandler(self.handler)

    def test_alternate_names(self):
        self.logger.info("Testing access through alternate names.")
        attrs = self.attrs
        # access by alternate names
        # get the entries with foobar
        keys = attrs.get_key("foobar")
        self.assertEqual(len(keys), 2)
        # get the entries with foo
        keys = attrs.get_key("foo")
        self.assertEqual(len(keys), 1)
        # get the entries with bar
        keys = attrs.get_key("bar")
        self.assertEqual(len(keys), 1)
        # get the entries with baz
        keys = attrs.get_key("baz")
        self.assertEqual(len(keys), 1)
        # check values found from alternate names
        self.assertEqual(attrs["foo"], [1], msg="Accessing 'foo' failed.")
        self.assertEqual(attrs["bar"], [2], msg="Accessing 'bar' failed.")
        self.assertEqual(attrs["baz"], [3], msg="Accessing 'baz' failed.")
        self.assertEqual(sorted(attrs["foobar"]), [1, 2],
                         msg="Accessing 'foobar' failed.")

    def test_keynames(self):
        self.logger.info("Testing access through UID.")
        for k in self.keynames:
            self.assertTrue(k in self.attrs, msg=f"Failed to find '{k}'")


if __name__ == "__main__":
    unittest.main()
