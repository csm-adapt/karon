import os
import re
import numpy as np
from karon import Sample
from karon.decorators import readwrite, requires
from karon.io import ExcelIO
from karon.tree import LRNTree
from karon.tree.build import generate_tree
from karon.tree.util import get, put
from karon.specialized import as_opnode
from karon.io.pandas import to_dataframe

# set up working directory
os.chdir("/Users/bkappes/Desktop/workspace/quality made")

ifiles = {
    'Wolf': 'LHW build.xlsx',
    'CMU': 'Characterization-CMU.xlsx',
    'Mines': 'Characterization-Mines.xlsx'
}

@readwrite
@requires("Sample Name", "Parent Sample Name")
def generic(**contents):
    def is_null(entry):
        try:
            if np.isnan(entry):
                return True
        except TypeError:
            pass
        finally:
            return bool(entry)

    sample = Sample(**contents)
    if is_null(sample.contents["Parent Sample Name"]):
        sample.contents["Parent Sample Name"] = ''
    return sample

# example usage

def propagate(parent_key, child_key=None, overwrite=False):
    """
    Creates an agent that propagates specific keys from parent to child
    through the tree.

    :param parent_key: Key from Node.contents that holds the value to be
        propagated to the child.
    :type parent_key: str
    :param child_key: Key in the child to place the result. By default, is
        the same as parent_key.
    :type child_key: str
    :param overwrite: Whether to overwrite values already present in the
        children. Default: False.
    :return: Unary function, signature: f(tree-like)
    """
    def get_from_parent(node):
        return get(parent_key)(node)

    def put_in_child(node):
        if overwrite or (child_key not in node.contents):
            value = get_from_parent(node.parent)
            if value is not None:
                put(child_key)(node, value)

    def func(root):
        root = as_opnode(root)
        root.puts(put_in_child)

    if child_key is None:
        child_key = parent_key

    return func


def aggregate(gets, reduce=None):
    """
    Creates an agent that aggregates and, optionally, performs a reduction
    on values collected from descendant nodes in a tree.

    :param gets: Function to extract the feature/features that are to
        be aggregated.
    :type gets: unary function, signature: f(Node)
    :param reduce: Function that accepts the list of results returned from
        this aggregation and applies a transform. While this need not return
        a scalar, an archetype for this function is to perform a reduction,
        such as a mean.
    :type reduce: unary function, signature: f(list-like)
    :return: Unary function, signature: f(tree-like)
    """
    def func(root):
        root = as_opnode(root)
        root.gets(gets, callback=reduce)
    return func


def mean(alist):
    try:
        return np.mean([x for x in alist if (x is not None)])
    except:
        return alist


def is_null(obj):
    try:
        return np.isnan(obj).any()
    except TypeError:
        return not bool(obj)
    except ValueError:
        return False


def strcmp(*transforms):
    def func(lhs, rhs):
        if is_null(lhs) or is_null(rhs):
            return False
        l = str(lhs)
        r = str(rhs)
        for t in transforms:
            l = t(l)
            r = t(r)
        return (l == r)
    return func


def mean_reduce(key):
    class Functor(object):
        def __init__(self, key):
            self.key = f"mean {key}"

        def __call__(self, node, arr):
            return put(self.key)(node, mean(arr))

    return Functor(key)


def get_attributes(root):
    attr = []
    for node in LRNTree(root):
        attr.extend(node.contents.keys())
    attr = set(attr) - {"Sample Name", "Parent Sample Name"}
    return list(attr)


reader = ExcelIO(default=generic)
nodes = []
for contact, fname in iter(ifiles.items()):
    try:
        new = reader.load(fname)
        for node in new:
            node.contents['Contact'] = contact
        nodes.extend(new)
    except:
        print(f"Error while reading {fname}")
        raise

lineage = generate_tree(
    get_nodeid=get('sample name'),
    get_parent=get('parent sample name'),
    cmp=strcmp(str.lower, str.strip))(nodes)

for root in lineage:
    for attr in get_attributes(root):
        # aggregate a list
        aggregate(get(attr))(root)
        propagate(attr)(root)
        # aggregate and propagate reductions
        for reduction in (mean_reduce(attr),):
            aggregate(get(attr), reduce=reduction)(root)
            propagate(reduction.key)(root)

df = to_dataframe(nodes)

def to_excel(dataframe):
    """
    Orders the data for writing to an Excel worksheet. "Sampe Name",
    "Parent Sample Name", and "Contact" are treated as special columns
    and ordered to appear as the first three columns in the worksheet.

    :param dataframe: pandas.DataFrame containing the tabulated information
        collected in previous steps.
    :return: None
    """
    columns = list(dataframe.columns)
    ordered = ["Sample Name", "Parent Sample Name", "Contact"]
    columns = ordered + [obj for obj in columns if obj not in ordered]

    dataframe[columns].to_excel('qualitymade.xlsx', index=False)


def to_pif(dataframe):
    """
    Constructs a PIF-formatted data file appropriately formatted for import
    into the citrination platform.

    Several columns are treated as special:

        Sample Name --> uid
        Parent Sample Name --> subsystem.uid
        Contact --> contacts

    :param df: pandas.DataFrame containing the tabulated information
        collected from previous steps.
    :return: None
    """
    from pypif import pif

    def to_system(row):
        def wolf_contact():
            return pif.Person(name='JP H. Paul',
                              email='Jonathan_Paul@LincolnElectric.com',
                              tags='Lincoln Electric (Wolf Robotics)')
        def cmu_contact():
            return pif.Person(name='Anthony Rollett',
                              email='rollett@andrew.cmu.edu',
                              tags='Carnegie Mellon University')
        def mines_contact():
            return pif.Person(name='Branden Kappes',
                              email='bkappes@mines.edu',
                              tags='Colorado School of Mines')
        def lmco_contact():
            return pif.Person(name='Edward A. Pierson',
                              email='edward.a.pierson@lmco.com',
                              tags='Lockheed Martin Corporation')

        system = pif.System()
        system.uid = str(row['Sample Name'])
        system.sub_systems = pif.System(uid=str(row['Parent Sample Name']))
        system.contacts = {
            'Wolf': wolf_contact,
            'CMU': cmu_contact,
            'Mines': mines_contact}.get(row['Contact'], lmco_contact)()

        special = ['Sample Name', 'Parent Sample Name', 'Contact']
        filelist = None
        for column, value in row.items():
            # special columns have already been handled.
            if column in special:
                continue
            # no need to record empty record.
            if is_null(value):
                continue
            # handle FILEs.
            if column.startswith('FILE'):
                special.append(column)
                split = column.split(':')
                value = value if isinstance(value, (list, tuple)) else [value]
                for path in value:
                    file = pif.FileReference(relative_path=str(path),
                                             tags=':'.join(split[1:]).strip())
                    try:
                        filelist.append(file)
                    except AttributeError:
                        filelist = [file]
        # everything else is a property
        for column, value in row.items():
            # special columns have already been handled.
            if column in special:
                continue
            # ignore this value if empty
            if is_null(value):
                continue
            # otherwise, construct a property value.
            pty = pif.Property(name=column,
                               scalars=value,
                               files=filelist)
            try:
                pty.units = re.search('.*\(([^)]+)\)', column).group(1)
            except AttributeError:
                pass
            try:
                system.properties.append(pty)
            except AttributeError:
                system.properties = [pty]
        # done
        return system

    dataframe = dataframe.fillna('')
    records = [to_system(row) for i, row in dataframe.iterrows()]

    with open('qualitymade.json', 'w') as ofs:
        pif.dump(records, ofs)


to_excel(df)
to_pif(df)
