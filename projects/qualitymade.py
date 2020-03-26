import os, sys
import re
import numpy as np
import pandas as pd
from karon import Sample
from karon.decorators import readwrite, requires
from karon.io import ExcelIO
from karon.tree import LRNTree
from karon.tree.build import generate_tree
from karon.tree.util import get, put
# from karon.specialized import as_opnode
from karon.io.pandas import to_dataframe

def log(msg):
    print(msg)
    sys.stdout.flush()

# set up working directory
os.chdir("/Users/bkappes/Dropbox (BeamTeam)/projects/Quality Made/data/updates/2020-03-26")

ifiles = {
    'Wolf': 'LHW-build.xlsx',
    # 'CMU': 'Characterization-CMU.xlsx',
    # 'Mines': 'Characterization-Mines.xlsx',
    # 'LM': 'Characterization-LM.xlsx'
}
output_prefix = 'qualitymade'
# output_prefix = 'characterization'
# output_prefix = 'build'

log(f"Building {output_prefix} relationships from "
    f"({', '.join(list(ifiles.values()))})")

# This is a Node generating function. The idea behind this is to
# abstract away the details of node creation and simplify the verification
# that a node contains certain fields, and has the properties expected at
# the point of creation. This could also have been done within the class
# and these checks handled through inheritance, but I think this is more
# explicit: the developer using karon does not have to inherit from an
# exponentially growing set of classes (readable, writeable, read-writeable,
# specify requirements, specify recommends, etc.) and deal with the added
# complexities of the MRO. This just seems much cleaner. It also allows the
# user to set some programmatic checks before, such as checking for null
# entries, as in this example, to set a default.
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
            return not bool(entry)

    sample = Sample(**contents)
    if is_null(sample.contents["Parent Sample Name"]):
        sample.contents["Parent Sample Name"] = str()
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
        # get(key) returns an unary function that accepts a node as an
        # argument and returns the value paired to "key".
        return get(parent_key)(node)

    def put_in_child(node):
        # placing the overwrite logic within "propagate" makes this
        # decision point more explicit and avoids hidden behavior where
        # the decision to overwrite is imposed in the library.
        permission = (overwrite or
                      not is_null(node.contents.get(child_key, None)))
        if permission:
            value = get_from_parent(node.parent)
            if value is not None:
                put(child_key)(node, value)

    def func(root):
        root.puts(put_in_child)

    # handle defaults: if child_key is not specified, assume it is the
    # same as the parent_key.
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
        root.gets(gets, callback=reduce)
    return func


def is_null(obj):
    try:
        return np.isnan(obj).any()
    except TypeError:
        return not bool(obj)
    except ValueError:
        return False


def strcmp(*transforms):
    """
    Returns a function for comparing strings after first applying
    zero or more transforms, e.g. `str.lower`.

    :param transforms: String transformations, unary function(s) that
        accept(s), and return(s), a string.
    :type transforms: unary functions, f(str) -> str
    :return: Unary function, f(str, str) -> bool
    """
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


def maximum(key):
    """
    To perform a reduction over `key`, returns a function compatible with
    the `reduce` parameter in the `aggregate` function.

    :param key: key over which the reduction is to be performed.
    :type key: str
    :return: Binary function, f(Node, array-like) -> value
    """
    class Functor(object):
        def __init__(self, key):
            self.key = f"max {key}"

        @staticmethod
        def minimum(alist):
            """
            Calculates the mean from a list of values. None values are excluded
            from the calculation. If any exception is raised, the list is
            returned.

            :param alist: Iterable of values over which the mean is to be calculated.
            :type alist: iterable
            :return: mean, or if a mean cannot be calculated, the original list.
            """
            try:
                return np.nanmax([float(x) for x in alist if (x is not None)])
            except:
                # return alist
                return None

        def __call__(self, node, arr):
            return put(self.key)(node, Functor.maximum(arr))

    return Functor(key)


def minimum(key):
    """
    To perform a reduction over `key`, returns a function compatible with
    the `reduce` parameter in the `aggregate` function.

    :param key: key over which the reduction is to be performed.
    :type key: str
    :return: Binary function, f(Node, array-like) -> value
    """
    class Functor(object):
        def __init__(self, key):
            self.key = f"min {key}"

        @staticmethod
        def minimum(alist):
            """
            Calculates the mean from a list of values. None values are excluded
            from the calculation. If any exception is raised, the list is
            returned.

            :param alist: Iterable of values over which the mean is to be calculated.
            :type alist: iterable
            :return: mean, or if a mean cannot be calculated, the original list.
            """
            try:
                return np.nanmin([float(x) for x in alist if (x is not None)])
            except:
                # return alist
                return None

        def __call__(self, node, arr):
            return put(self.key)(node, Functor.minimum(arr))

    return Functor(key)


def mean(key):
    """
    To perform a reduction over `key`, returns a function compatible with
    the `reduce` parameter in the `aggregate` function.

    :param key: key over which the reduction is to be performed.
    :type key: str
    :return: Binary function, f(Node, array-like) -> value
    """
    class Functor(object):
        def __init__(self, key):
            self.key = f"mean {key}"

        @staticmethod
        def mean(alist):
            """
            Calculates the mean from a list of values. None values are excluded
            from the calculation. If any exception is raised, the list is
            returned.

            :param alist: Iterable of values over which the mean is to be calculated.
            :type alist: iterable
            :return: mean, or if a mean cannot be calculated, the original list.
            """
            try:
                return np.nanmean([float(x) for x in alist if (x is not None)])
            except:
                # return alist
                return None

        def __call__(self, node, arr):
            return put(self.key)(node, Functor.mean(arr))

    return Functor(key)


def std(key):
    """
    To perform a reduction over `key`, returns a function compatible with
    the `reduce` parameter in the `aggregate` function.

    :param key: key over which the reduction is to be performed.
    :type key: str
    :return: Binary function, f(Node, array-like) -> value
    """
    class Functor(object):
        def __init__(self, key):
            self.key = f"stddev {key}"

        @staticmethod
        def std(alist):
            """
            Calculates the mean from a list of values. None values are excluded
            from the calculation. If any exception is raised, the list is
            returned.

            :param alist: Iterable of values over which the mean is to be calculated.
            :type alist: iterable
            :return: mean, or if a mean cannot be calculated, the original list.
            """
            try:
                return np.nanstd([float(x) for x in alist if (x is not None)])
            except:
                # return alist
                return None

        def __call__(self, node, arr):
            return put(self.key)(node, Functor.std(arr))

    return Functor(key)


def unique(key):
    """
    To perform a reduction over `key`, returns a function compatible with
    the `reduce` parameter in the `aggregate` function.

    :param key: key over which the reduction is to be performed.
    :type key: str
    :return: Binary function, f(Node, array-like) -> value
    """
    class Functor(object):
        def __init__(self, key):
            self.key = key

        @staticmethod
        def make_hashable(arr):
            if isinstance(arr, str):
                return arr
            try:
                return tuple(Functor.make_hashable(x) for x in arr)
            except TypeError:
                return arr

        def __call__(self, node, arr):
            unique = tuple(set(Functor.make_hashable(arr)))
            unique = tuple(u for u in unique if u is not None)
            unique = {0: lambda x: None,
                      1: lambda x: x[0]}.get(len(unique), lambda x: x)(unique)
            return put(self.key)(node, unique)

    return Functor(key)


def get_attributes(root, exclude={"Sample Name", "Parent Sample Name"}):
    """
    Returns a list of unique attributes accessible from the tree
    originating at `root`. This excludes "Sample Name" and
    "Parent Sample Name" from the list of attributes.

    :param root: Root node of the tree.
    :type root: Node
    :param exclude: Set of attributes to exclude from the list. Default:
        "Sample Name" and "Parent Sample Name".
    :type exclude: set
    :return: All unique attributes.
    :rtype: list
    """
    attr = []
    for node in LRNTree(root):
        attr.extend(node.contents.keys())
    attr = set(attr) - set(exclude)
    return list(attr)


# Creates a reader that stores records according to the Node generating
# function "generic" (readwrite, requires "Sample Name" and
# "Parent Sample Name"
reader = ExcelIO(default=generic)

log("Generated reader.")

# Constructs a master list of nodes, read from a dictionary of files
# (ifiles) whose key:value pairs are (who supplied the file):(file name)
log("Constructing nodes...")
nodes = []
for contact, fname in iter(ifiles.items()):
    try:
        # reads a list of "new" nodes from file "fname"
        new = reader.load(fname)
        # for every node...
        for node in new:
            # ... remove empty fields
            node.contents = {k: v for k, v in node.contents.items()
                             if not (is_null(v) and k != "Parent Sample Name")}
            # ... add a contact field based on contact
            node.contents['Contact'] = contact
        nodes.extend(new)
    except:
        print(f"Error while reading {fname}")
        raise

log(f"{len(nodes)} nodes constructed.")

# Generate trees that connect parent nodes ("Parent Sample Node") to
# child nodes ("Sample Name"). Any node that does not have a parent
# is a root. lineage is a list of all roots generated from the nodes
# read above.
log("Generating tree structures...")

lineage = generate_tree(
    get_nodeid=get('Sample Name'),
    get_parent=get('Parent Sample Name'),
    cmp=strcmp(str.strip))(nodes)

log(f"{len(lineage)} trees generated.")

# generate a set of unique attributes across all root nodes (tree)
log("Generating attribute set...")
attributes = set()
for root in lineage:
    attributes = attributes.union(get_attributes(root))
# attributes = list(attributes)
log(f"{len(attributes)} identified.")

# aggregate (collect data from child nodes) then propagate (push data
# down to children).
log("Aggregating/propagating between nodes...")
for root in lineage:
    for attr in attributes:
        # propagate(attr)(root)
        # aggregate(get(attr), reduce=put(attr, overwrite=False))(root)
        # propagate(attr)(root)
        # aggregate and propagate reductions
        # for reduction in (mean_reduce(attr),):
        for reduction in (unique(attr),
                          mean(attr),
                          std(attr),
                          minimum(attr),
                          maximum(attr)):
            aggregate(get(attr), reduce=reduction)(root)
            propagate(reduction.key)(root)
        propagate(attr)(root)
log("Finished aggregating/propagating data between nodes.")

log("Cleaning up empty attributes...")
# drop any propagated null values and the lists they create
for node in nodes:
    for key, value in iter(node.contents.items()):
        if isinstance(value, list):
            node.contents[key] = [x for x in value if x is not None]
            if len(node.contents[key]) == 0:
                node.contents[key] = ''
            elif len(node.contents[key]) == 1:
                node.contents[key] = node.contents[key][0]
log("Finished cleaning empty attributes.")

# create a dataframe from the node data.
# df = to_dataframe(nodes)
log("Generating pandas.DataFrame from roots...")
roots_only = to_dataframe(lineage)
log(f"{len(roots_only)} records stored in roots DataFrame.")
log("Generating pandas.DataFrame from all nodes...")
full = to_dataframe(nodes)
log(f"{len(full)} records created from all nodes.")

def to_excel(dataframe, filename):
    """
    Orders the data for writing to an Excel worksheet. "Sampe Name",
    "Parent Sample Name", and "Contact" are treated as special columns
    and ordered to appear as the first three columns in the worksheet.
    Similarly, FILE objects are reordered to appear at the end.

    :param dataframe: pandas.DataFrame containing the tabulated information
        collected in previous steps.
    :return: None
    """
    columns = list(dataframe.columns)
    prepend = ["Sample Name", "Parent Sample Name", "Contact"]
    append = [col for col in columns if re.match(r'^\s*FILE:', col)]
    columns = prepend + \
              [obj for obj in columns
               if (obj not in prepend and obj not in append)] + \
              append

    dataframe[columns].to_excel(filename,
                                index=False,
                                engine='xlsxwriter')


def to_pif(dataframe, filename):
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
        def url_friendly(name):
            return re.sub(r"\W", "_", name)
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

        # Every PIF record is a System object
        system = pif.System()
        # create a unique identifier. This must be URL friendly.
        system.uid = url_friendly(str(row['Sample Name']))
        # name the PIF
        system.names = str(row['Sample Name'])
        # record the parent sample name
        system.sub_systems = pif.System(
            uid=url_friendly(str(row['Parent Sample Name'])),
            names = str(row['Sample Name']))
        # set the contact information. By default, I set this as LMCO.
        system.contacts = {
            'Wolf': wolf_contact,
            'CMU': cmu_contact,
            'Mines': mines_contact,
            'LM': lmco_contact}.get(row['Contact'], lmco_contact)()

        # Certain fields we treat as special
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
                # add the FILE column to the list of special columns
                # so we don't add this as a property.
                special.append(column)
                # split on colon -- we don't need "FILE" in the name
                split = column.split(':')
                # Convert the filename (or the string-representation of
                # a list of filenames, e.g. [file1.png, file2.png]) to
                # a list of files
                value = str(value).strip("[]").split(",")
                # create a file reference for each file and store these as
                # a list of FileReference objects.
                for path in value:
                    file = pif.FileReference(relative_path=str(path),
                                             tags=':'.join(split[1:]).strip())
                    try:
                        filelist.append(file)
                    except AttributeError:
                        filelist = [file]
        # create a special property that holds all the files
        pty = pif.Property(name="Files",
                           files=filelist)
        try:
            system.properties.append(pty)
        except AttributeError:
            # if this is the first property, append to a None value will
            # fail. Handle this edge case.
            system.properties = [pty]
        # everything else is a property
        for column, value in row.items():
            # special columns have already been handled.
            if column in special:
                continue
            # ignore this value if empty
            if is_null(value):
                continue
            # scalar can only contain lists, dict, string, or Number
            value = {
                        pd.Timestamp: str,
                        tuple: list
                    }.get(type(value), type(value))(value)
            # otherwise, construct a property value.
            try:
                pty = pif.Property(name=column,
                                   scalars=value)
            except:
                pty = pif.Property(name=column,
                                   scalars=str(value))
                # print(f"{column}: {value}")
                # raise
            # units are stored, by convention in parentheses, e.g.
            # laser speed (mm/s). This regular expression extracts the the
            # last term surrounded by parentheses.
            try:
                pty.units = re.search('.*\(([^)]+)\)\s*$', column).group(1)
            except AttributeError:
                # no units were found...
                pass
            try:
                # add the property
                system.properties.append(pty)
            except AttributeError:
                # if this is the first property, append to a None value will
                # fail. Handle this edge case.
                system.properties = [pty]
        # done
        return system

    dataframe = dataframe.fillna('')
    records = [to_system(row) for i, row in dataframe.iterrows()]

    with open(filename, 'w') as ofs:
        pif.dump(records, ofs)


# save the results to Excel (in the QM Excel metadata format) and PIF
# for rendering on Citrine.
log("Writing roots DataFrame to Excel and PIF...")
to_excel(roots_only, f"{output_prefix}-roots.xlsx")
to_pif(roots_only, f"{output_prefix}-roots.json")
log("Finished writing roots DataFrame to Excel and PIF.")

log("Writing nodes DataFrame to Excel and PIF...")
to_excel(full, f"{output_prefix}-full.xlsx")
to_pif(full, f"{output_prefix}-full.json")
log("Finished writing nodes DataFrame to Excel and PIF.")
