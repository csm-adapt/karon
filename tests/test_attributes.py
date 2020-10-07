#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import sqlite3
import unittest
from karon.graph import Attribute, AttributeSet

import logging
# _logger = logging.getLogger(__name__)

__author__ = "Branden Kappes"
__copyright__ = "KMMD, LLC."
__license__ = "mit"


def execute(conn, *cmds):
    return conn.execute(" ".join(cmds) + ";")


class TestAttribute(unittest.TestCase):
    def setUp(self):
        self.sqlconn = conn = sqlite3.connect("data/test.db")
        # check for necessary tables
        tables = [table[0].lower() for table in
            execute(conn,
                "SELECT name",
                "FROM sqlite_master",
                "WHERE type='table'")]
        # Create the "uid" table, if it doesn't exist
        if "uid" not in tables:
            execute(conn,
                "CREATE TABLE uid",
                "(ID CHAR(50) PRIMARY KEY NOT NULL,",
                "DATE CHAR(19) NOT NULL)")

    def tearDown(self):
        self.sqlconn.commit()
        self.sqlconn.close()

    def check_uid_unique(self, attr):
        conn = self.sqlconn
        uids = list(execute(conn,
            f"SELECT ID FROM uid WHERE ID LIKE '{attr.uid}'"))
        self.assertEqual(uids, [])
        execute(conn,
            "INSERT INTO uid",
            f"(ID, DATE) VALUES ('{attr.uid}', datetime('now'))")

    def test_creation(self):
        # empty constructor
        attr = Attribute()
        self.assertEqual(attr.names, set())
        self.assertIs(attr.value, None)
        self.check_uid_unique(attr)
        # constructor from value
        attr = Attribute(value=1.234)
        self.assertEqual(attr.value, 1.234)
        self.assertEqual(attr.names, set())
        self.check_uid_unique(attr)
        # constructor with name
        attr = Attribute("foo")
        self.assertEqual(attr.names, {"foo"})
        self.assertIs(attr.value, None)
        self.check_uid_unique(attr)
        # constructor with names
        attr = Attribute(["foo", "bar"])
        self.assertEqual(attr.names, {"foo", "bar"})
        self.assertIs(attr.value, None)
        self.check_uid_unique(attr)
        # constructor with value and name
        attr = Attribute("foo", 1.234)
        self.assertEqual(attr.names, {"foo"})
        self.assertEqual(attr.value, 1.234)
        self.check_uid_unique(attr)
        # constructor with value and names
        attr = Attribute(names=["foo", "bar"], value=1.234)
        self.assertEqual(attr.names, {"foo", "bar"})
        self.assertEqual(attr.value, 1.234)
        self.check_uid_unique(attr)
        # constructor with dictionary
        attr = Attribute({"names": "foo", "value": 1.234})
        self.assertEqual(attr.names, {"foo"})
        self.assertEqual(attr.value, 1.234)
        self.check_uid_unique(attr)
        # constructor with Attribute
        attr2 = Attribute(attr)
        self.assertEqual(attr2.names, {"foo"})
        self.assertEqual(attr2.value, 1.234)
        self.assertNotEqual(attr2.uid, attr.uid)
        self.assertIsNot(attr2, attr)
        # constructor with uid
        attr = Attribute(names=["foo", "bar"], value=1.234, uid="foo-bar")
        self.assertEqual(attr.names, {"foo", "bar"})
        self.assertIs(attr.value, 1.234)
        self.assertEqual(attr.uid, "foo-bar")

    def test_json_serialization(self):
        attr = Attribute(names=["foo", "bar"], value=1.234, uid="foo-bar")
        dupl = Attribute.loads(attr.dumps())
        self.assertEqual(attr, dupl)
        self.assertIsNot(attr, dupl)


class TestAttributeSet(unittest.TestCase):
    def setUp(self):
        self.sqlconn = conn = sqlite3.connect("data/test.db")
        # check for necessary tables
        tables = [table[0].lower() for table in
            execute(conn,
                "SELECT name",
                "FROM sqlite_master",
                "WHERE type='table'")]
        # Create the "uid" table, if it doesn't exist
        if "uid" not in tables:
            execute(conn,
                "CREATE TABLE uid",
                "(ID CHAR(50) PRIMARY KEY NOT NULL,",
                "DATE CHAR(19) NOT NULL)")

    def tearDown(self):
        self.sqlconn.commit()
        self.sqlconn.close()

    def check_uid_unique(self, attr):
        conn = self.sqlconn
        uids = list(execute(conn,
            f"SELECT ID FROM uid WHERE ID LIKE '{attr.uid}'"))
        self.assertEqual(uids, [])
        execute(conn,
            "INSERT INTO uid",
            f"(ID, DATE) VALUES ('{attr.uid}', datetime('now'))")

    def test_creation(self):
        # empty
        aset = AttributeSet()
        self.assertEqual(len(aset), 0)
        # create from list of names
        names = ["foo", "bar", "baz"]
        aset = AttributeSet(names)
        self.assertEqual(len(aset), 3)
        for attr in aset:
            name = attr.pop()
            self.assertEqual(len(attr), 0)
            self.assertIn(name, names)
            names = [n for n in names if n != name]
            self.check_uid_unique(attr)
        # create from tuple of names
        names = ("foo", "bar", "baz")
        aset = AttributeSet(names)
        self.assertEqual(len(aset), 3)
        for attr in aset:
            name = attr.pop()
            self.assertEqual(len(attr), 0)
            self.assertIn(name, names)
            names = tuple(n for n in names if n != name)
            self.check_uid_unique(attr)
        # create from list of dicts
        attrs = [
            {"names": "foo", "value": 1.234},
            {"names": "bar", "value": 1.234},
            {"names": "baz", "value": 1.234}
        ]
        names = [a["names"] for a in attrs]
        aset = AttributeSet(attrs)
        self.assertEqual(len(aset), 3)
        for attr in aset:
            name = attr.pop()
            self.assertEqual(len(attr), 0)
            self.assertEqual(attr.value, 1.234)
            self.assertIn(name, names)
            attr.add(name)
            self.check_uid_unique(attr)
        # create from dict
            attrs = {
                "foo": 1.234,
                "bar": 5.678,
                "baz": 9.012
            }
            names = attrs
            aset = AttributeSet(attrs)
            self.assertEqual(len(aset), 3)
            for attr in aset:
                name = attr.pop()
                self.assertEqual(len(attr), 0)
                self.assertEqual(attr.value, attrs[name])
                self.assertIn(name, names)
                attr.add(name)
                self.check_uid_unique(attr)
        # create from AttributeSet
        aset2 = AttributeSet(aset)
        for attr in aset2:
            self.assertIn(attr, aset)

    def test_json_serialization(self):
        attrs = [
            {"names": "foo", "value": 1.234},
            {"names": "bar", "value": 5.678},
            {"names": "baz", "value": 9.012}
        ]
        aset = AttributeSet(attrs)
        dupl = AttributeSet.loads(aset.dumps())
        self.assertEqual(aset, dupl)
        self.assertIsNot(aset, dupl)

    def test_union(self):
        attrs = [
            {"names": "foo", "value": 1.234},
            {"names": "bar", "value": 5.678},
            {"names": "baz", "value": 9.012}
        ]
        expected = AttributeSet(attrs)
        aset = AttributeSet([e for e in expected][:2])
        bset = AttributeSet([e for e in expected][2:])
        cset = aset.union(bset)
        self.assertEqual(expected, cset, msg=f"\n{expected.dumps(indent=4)} !=\n{cset.dumps(indent=4)}")
        self.assertIsNot(expected, cset)


if __name__ == "__main__":
    unittest.main()
