import pytest
import numpy as np
import pandas as pd
from karon.tree import NLRTree
from ..example import Example


@pytest.fixture
def structured():
    return {
        'filename': '../../tests/data/example.xlsx',
        'aggregate': 'data/example-aggregate.xlsx',
        'propagate': 'data/example-propagate.xlsx',
        'names': [
            "e4f6efde-abdb-4a02-a25a-3c3859857aee",
            "e8a80a70-18cc-44b9-8668-4f479918f13a",
            "398a8f61-9707-45d8-802d-84bd11179a56",
            "e0276301-425d-4d14-9bb4-05c6e3414772",
            "2983b9dd-227a-4136-83c6-473e2deac44d",
            "85bf6cf2-22ac-49e8-862d-f192781f73a3",
            "5b91f720-6a2f-456b-a14f-bb961d1f80dd",
            "94073a4f-cd2f-46dc-95c0-37d60b32e9ad",
            "7bc7c8e8-dcc6-4317-8518-d600f26573ed",
            "e0b7b18c-d025-4beb-856a-7a0f054c9ea2",
            "c1e2c204-62f3-4ed6-9226-35747a43fb9c",
            "b397eac8-87a0-47c4-b5ab-f9514bf50bfa",
            "5022fa10-98d1-4dc0-b35e-4e800ab3cce6",
            "d9e2da61-80dc-9521-2c6b-9e31c4999d81",
            "3036de92-0d52-4f51-a0c0-422f5ad3d8db",
            "d887d4d2-d9ab-4673-8d69-d0daf8af8551",
            "11fe2186-ba63-4b69-8735-25fee5cda5d4",
            "3a50216b-50b3-4212-b7fe-4bd96605556f",
            "c37290e2-1f8e-8820-8ef5-9adc49859d44",
            "e6b3b1c3-ad38-4fc1-82cf-7e301a4aba90",
            "e224bfca-f917-40de-ad6d-12b70e21b456",
            "f29ebef4-7f77-4048-a1e3-2af0ca3f046f"
        ],
        "NLR trees": [
            ("e4f6efde-abdb-4a02-a25a-3c3859857aee",
             "5022fa10-98d1-4dc0-b35e-4e800ab3cce6",
             "d9e2da61-80dc-9521-2c6b-9e31c4999d81",
             "3036de92-0d52-4f51-a0c0-422f5ad3d8db",
             "d887d4d2-d9ab-4673-8d69-d0daf8af8551"),
            ("e8a80a70-18cc-44b9-8668-4f479918f13a",
             "f29ebef4-7f77-4048-a1e3-2af0ca3f046f",
             "11fe2186-ba63-4b69-8735-25fee5cda5d4",
             "3a50216b-50b3-4212-b7fe-4bd96605556f",
             "c37290e2-1f8e-8820-8ef5-9adc49859d44",
             "e6b3b1c3-ad38-4fc1-82cf-7e301a4aba90"),
            ("398a8f61-9707-45d8-802d-84bd11179a56",
             "e224bfca-f917-40de-ad6d-12b70e21b456",
             "7bc7c8e8-dcc6-4317-8518-d600f26573ed",
             "e0b7b18c-d025-4beb-856a-7a0f054c9ea2",
             "c1e2c204-62f3-4ed6-9226-35747a43fb9c",
             "b397eac8-87a0-47c4-b5ab-f9514bf50bfa"),
            ("e0276301-425d-4d14-9bb4-05c6e3414772",
             "2983b9dd-227a-4136-83c6-473e2deac44d",
             "85bf6cf2-22ac-49e8-862d-f192781f73a3",
             "5b91f720-6a2f-456b-a14f-bb961d1f80dd",
             "94073a4f-cd2f-46dc-95c0-37d60b32e9ad"),
        ]
    }


@pytest.fixture
def condensed():
    rval = Example("name", "parent name")
    rval.read("./data/example-node-properties.xlsx")
    return rval


def as_dictionary(root, uid_key):
    return {n.contents[uid_key]: n.contents for n in NLRTree(root)}


def equal(A, B):
    def equal_general(lhs, rhs):
        try:
            lhsNan = ((lhs in (None, '')) or np.isnan(lhs))
        except:
            lhsNan = False
        try:
            rhsNan = ((rhs in (None, '')) or np.isnan(rhs))
        except:
            rhsNan = False
        if lhsNan and rhsNan:
            return True
        try:
            return np.isclose(float(A), float(B))
        except:
            return A == B

    def equal_examples(lhs, rhs):
        left = {node.contents['name']: node.contents
                for root in lhs.roots for node in NLRTree(root)}
        right = {node.contents['name']: node.contents
                 for root in rhs.roots for node in NLRTree(root)}
        # ensure both examples have an equivalent set of keys
        keys = tuple(
            set([k for lmap in left.values() for k in lmap.keys()])
                .union(
                [k for rmap in right.values() for k in rmap.keys()]))
        for contents in left.values():
            for k in keys:
                contents[k] = contents.get(k, None)
        for contents in right.values():
            for k in keys:
                contents[k] = contents.get(k, None)
        return equal(left, right)

    def equal_iter(lhs, rhs):
        if len(lhs) != len(rhs):
            return False
        return all([equal(x, y) for x,y in zip(lhs, rhs)])

    def equal_dict(lhs, rhs):
        # same set of keys?
        # These are equal only if both are empty, that is, they are the same.
        if set(lhs.keys()) != set(rhs.keys()):
            return False
        try:
            return all([equal(lhs[k], rhs[k]) for k in lhs.keys()])
        except Exception as e:
            return False

    # Examples
    if isinstance(A, Example):
        if isinstance(B, Example):
            return equal_examples(A, B)
        else:
            return False
    # iterables (not strings)
    if isinstance(A, (list, tuple)):
        if isinstance(B, (list, tuple)):
            return equal_iter(A, B)
        else:
            return False
    # dictionaries
    if isinstance(A, dict):
        if isinstance(B, dict):
            return equal_dict(A, B)
        else:
            return False
    # anything else
    else:
        return equal_general(A, B)


def test_equal(structured):
    filename = structured['filename']
    samples = Example('name', 'parent name')
    samples.read(filename)
    # check general
    assert equal(1.234, 1.234000001)
    assert not equal(1.234, 1.324)
    assert equal(None, None)
    assert equal(float('nan'), float('nan'))
    assert equal(None, float('nan'))
    # check lists
    assert equal(list(range(4)), list(range(4)))
    assert not equal(list(range(4)), list(range(5)))
    # check dict
    lhs = {
        'a': 1,
        'b': 2,
        'c': 3
    }
    rhs = {
        'a': 1,
        'b': 2,
        'c': 3
    }
    assert equal(lhs, rhs)
    lhs['c'] = {
        'A': 100,
        'B': 200,
        'C': 300
    }
    assert not equal(lhs, rhs)
    rhs['c'] = {
        'A': 100,
        'B': 200,
        'C': 300
    }
    assert equal(lhs, rhs)
    # samples
    assert equal(samples, samples)


def test_Example():
    example = Example("name", "parent name")
    assert example._uid_key == "name"
    assert example._parent_key == "parent name"
    assert example._filenames == []
    assert example._nodes == {}
    assert example.roots == []


def test_filetype():
    assert Example.filetype("foo.xls") == "excel"
    assert Example.filetype("foo.XLS") == "excel"
    assert Example.filetype("foo.xlsx") == "excel"
    assert Example.filetype("foo.XLSX") == "excel"


def test_read(structured):
    example = Example('name', 'parent name')
    filename = structured['filename']
    nodes = structured['names']
    trees = structured['NLR trees']
    example.read(filename)
    # check filename was stored properly
    diff = set(example._filenames) - set([filename])
    assert len(diff) == 0, \
        "Filename(s) were not stored as expected."
    # check that all samples were read properly
    diff = set(example._nodes.keys()) - set(nodes)
    assert len(diff) == 0, \
        f"Samples not ready as expected: {diff}"
    # check that the expected structure was recovered
    names = [tuple(node.contents['name'] for node in NLRTree(root))
             for root in example.roots]
    diff = set(names) - set(trees)
    assert len(diff) == 0, \
        f"Expected structure was not recovered: {diff}"


def strdict(d, level=0):
    def truncated_obj(obj):
        el = str(obj)
        if len(el) > 15:
            el = el[:6] + '...' + el[-6:]
        return el
    rval = ''
    for k,v in iter(d.items()):
        rval += level*'  ' + str(k) + ': '
        if isinstance(v, dict):
            rval += '\n' + strdict(v, level=level+1)
        else:
            try:
                if isinstance(v, str):
                    raise Exception()
                el = [truncated_obj(x) for x in v]
                el = str(el)
            except:
                el = truncated_obj(v)
            rval += el + '\n'
    return rval


def joindicts(a, b):
    keys = set(a.keys()).union(b.keys())
    rval = {}
    for k in keys:
        aval = a.get(k, None)
        bval = b.get(k, None)
        if (isinstance(aval, dict) and
            isinstance(bval, dict)):
            val = joindicts(aval, bval)
        else:
            val = (aval, bval)
        rval[k] = val
    return rval


def write(filename, example, sheetname='Sheet1'):
    rval = {}
    # get a complete set of keys
    keys = set()
    for root in example.roots:
        asdict = as_dictionary(root, 'name')
        for entry in asdict.values():
            keys = keys.union(entry.keys())
    for root in example.roots:
        asdict = as_dictionary(root, 'name')
        # populate each cell. Empty string if N/A
        for entry in asdict.values():
            for key in keys:
                v = entry.get(key, '')
                rval[key] = rval.get(key, []) + [v]
    df = pd.DataFrame(rval)
    df.set_index('name', inplace=True)
    df.sort_index(inplace=True)
    df.to_excel(filename, sheetname)


def save_and_check(actual, expected):
    matches = equal(expected, actual)
    if not matches:
        amap = {node.contents['name']: node.contents
                for root in actual.roots for node in NLRTree(root)}
        emap = {node.contents['name']: node.contents
                for root in expected.roots for node in NLRTree(root)}
        names = tuple(
            set(amap.keys()).union(emap.keys()))
        keys = tuple(
            set(k for m in amap.values() for k in m.keys())
                .union([k for m in emap.values() for k in m.keys()]))
        msg = '\n'.join(map(str, [(name, key,
                amap.get(name, {}).get(key, None),
                emap.get(name, {}).get(key, None))
               for name in names for key in keys
               if not equal(amap.get(name, {}).get(key, None),
                            emap.get(name, {}).get(key, None))]))
        fname = '/Users/bkappes/Desktop/compare.xlsx'
        writer = pd.ExcelWriter(fname)
        write(writer, expected, 'expected')
        write(writer, actual, 'actual')
        writer.save()
        # assert matches, f'Difference saved to "{fname}"'
        assert matches, msg


def test_propagate(structured):
    filename = structured['filename']
    expected = Example('name', 'parent name')
    expected.read(structured['propagate'])
    actual = Example('name', 'parent name')
    actual.read(filename)
    actual.propagate()
    save_and_check(actual, expected)


def test_aggregate(structured):
    filename = structured['filename']
    expected = Example('name', 'parent name')
    expected.read(structured['aggregate'])
    actual = Example('name', 'parent name')
    actual.read(filename)
    actual.aggregate(reduce=Example.mean)
    save_and_check(actual, expected)


# def test_aggregate_and_reduce(condensed, structured):
#     filename = structured['filename']
#     expected = condensed
#     # # test inherit-reduce
#     # actual = Example("name", "parent name")
#     # actual.read(filename)
#     # actual.propagate()
#     # actual.aggregate(reduce=Example.mean)
#     # save_and_check(actual, expected)
#     #assert equal(expected, actual), msg
#     # test reduce-inherit
#     actual = Example("name", "parent name")
#     actual.read(filename)
#     actual.aggregate(reduce=Example.mean)
#     actual.propagate()
#     save_and_check(actual, expected)
#     # assert equal(expected, actual), \
#     #     "Reduce-Inherit does not match expected results."
#     # # test inherit-reduce-inherit
#     # actual = Example("name", "parent name")
#     # actual.read(filename)
#     # actual.propagate()
#     # actual.aggregate(reduce=Example.mean)
#     # actual.propagate()
#     # save_and_check(actual, expected)
#     # # assert equal(expected, actual), \
#     # #     "Inherit-Reduce-Inherit does not match expected results."
