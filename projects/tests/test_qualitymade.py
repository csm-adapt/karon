import pytest
from convey.tree import NLRTree
from ..qualitymade import read


@pytest.fixture
def data():
    return {
        'filename': '../../tests/data/tracking.xlsx',
        'names': [
            "G181030a",
            "G181030b",
            "G181030c",
            "G181030d",
            "G181030e",
            "G181030f",
            "G181030g",
            "G181030h",
            "G181030i",
            "M181210a",
            "MH181210a",
            "MH181210g"
        ],
        "NLR trees": [
            ("G181030a", "MH181210a"),
            ("G181030b",),
            ("G181030c",),
            ("G181030d",),
            ("G181030e",),
            ("G181030f",),
            ("G181030g", "M181210a", "MH181210g"),
            ("G181030h",),
            ("G181030i",)
        ]
    }


def test_read(data):
    dfix = data
    roots = read(dfix['filename'])
    # check order of nodes
    names = []
    trees = []
    for root in roots:
        names.extend([node.contents['name'] for node in NLRTree(root)])
        trees.append(tuple(n.contents['name'] for n in NLRTree(root)))
    # START HERE: CHECK THE STRUCTURE OF THESE NODES
    for aname in names:
        assert aname in dfix['names'], \
            f"{aname} missing from expected node names."
    for aname in dfix['names']:
        assert aname in names, \
            f"{aname} missing from names read from file."
    for atree in trees:
        assert atree in dfix['NLR trees'], \
            f"{atree} missing from expected trees."
    for atree in dfix['NLR trees']:
        assert atree in trees, \
            f"{atree} missing from trees constructed from file."
    # assert False, \
    #     '\n' + str(dfix) + \
    #     '\n' + str(roots) + \
    #     '\n'.join(names)
