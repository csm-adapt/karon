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
# from karon.operational import as_opnode
from karon.io.pandas import to_dataframe

import logging
_logger = logging.getLogger()

def log(msg):
    _logger.info(msg)
    # print(msg)
    # sys.stdout.flush()

# set up working directory
os.chdir("/Users/bkappes/Dropbox (BeamTeam)/projects/NASA ULI/data/UTEP/2020-03-31")

ifiles = {
    'UTEP': 'NASAULI_EP01.xlsx'
}

output_prefix = 'build'

UID = ExcelIO.Key.to_string(('', 'UID', '', ''))
FID = ExcelIO.Key.to_string(('', 'FID', '', ''))
CONTACT = ExcelIO.Key.to_string(('', 'Contact', '', ''))
is_file_column = lambda key: re.match('^file', key.strip(), re.IGNORECASE)

def get_units(colstring):
    colindex = ExcelIO.Key.to_index(colstring)
    if pd.isna(colindex[3]):
        return None
    else:
        return colindex[3]

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
@requires(UID, FID)
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
    if is_null(sample.contents[FID]):
        sample.contents[FID] = str()
    return sample


def is_container(obj):
    """
    Checks if the object is a container, that is, an iterable,
    but not a string.

    :param obj: Object to be tested.
    :return: True if object is a container, False otherwise.
    """
    if hasattr(obj, '__iter__') and not isinstance(obj, str):
        return True
    return False


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


def get_first_non_null(node, keys):
    if not is_container(keys):
        keys = (keys,)
    # check which keys are in node.contents and are non null
    nonnull = [k for k in keys if not is_null(node.contents.get(k, None))]
    # return the first matching, non-null value
    try:
        return node.contents[nonnull[0]]
    except IndexError:
        return None


# ########## Aggregation/Propagation Functions ############### #


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
            self.key = key.strip()

        @staticmethod
        def make_hashable(arr):
            if is_container(arr):
                return tuple(Functor.make_hashable(x) for x in arr)
            else:
                return arr

        def __call__(self, node, arr):
            unique = tuple(set(Functor.make_hashable(arr)))
            unique = tuple(u for u in unique if u is not None)
            if len(unique) == 0:
                unique = None
            elif len(unique) == 1:
                unique = unique[0]
            # unique = {0: lambda x: None,
            #           1: lambda x: x[0]}.get(len(unique), lambda x: x)(unique)
            return put(self.key)(node, unique)

    return Functor(key)


def flatten(key):
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
        def flatten(arr):
            def ensure_tuple(x):
                if is_container(x):
                    return tuple(x)
                else:
                    return (x,)
            # -- end, ensure_iter() -- #
            return sum([ensure_tuple(x) for x in arr], tuple())

        def __call__(self, node, arr):
            result = tuple(x for x in Functor.flatten(arr) if x is not None)
            # check if result is a single value
            if len(result) == 1:
                return None
            # check if result is the same as arr
            try:
                if np.all(np.asarray(arr) == np.asarray(result)):
                    return None
            except:
                pass
            return put(self.key)(node, result)

    return Functor(key)


# ############### Node Functions ############### #
class ArrayOnly:
    """
    Base class to ensure calculations are performed only on Real Arrays.
    """
    def __init__(self, key):
        self.key = key

    def __call__(self, node):
        arr = node.contents.get(self.key, None)
        if is_container(arr):
            try:
                # make sure this is, or can be coerced into, an array of floats
                arr = np.asarray(arr, dtype=float)
            except:
                return None
            result = type(self).function(arr)
            if result is not None:
                node.contents[self.key] = result
            return result
        return None


class Maximum(ArrayOnly):
    function = np.nanmax

    def __init__(self, key):
        super().__init__(key)
        self.name = f"max {key}"


class Minimum(ArrayOnly):
    function = np.nanmin

    def __init__(self, key):
        super().__init__(key)
        self.name = f"min {key}"


class Mean(ArrayOnly):
    function = np.nanmean

    def __init__(self, key):
        super().__init__(key)
        self.name = f"mean {key}"


class StdDev(ArrayOnly):
    function = np.nanstd

    def __init__(self, key):
        super().__init__(key)
        self.name = f"std {key}"


class RemeltRatio:
    def __init__(self, wire_diameter=None, wire_area=None):
        """
        Remelt ratio is defined by the wire feed rate, wire area, melt area,
        and melt pool velocity:

        ..math::

            \rho = 1 - \frac{WFR A_{wire}}{A_{melt} v_{melt}}

        :param wire_diameter:
        :param wire_area:
        """
        self.name = "remelt ratio"
        self.wireArea_ = None
        self.wireFeedRateKeys_ = []
        self.meltAreaKeys_ = []
        self.meltVelocityKeys_ = []
        self.set_wire_diameter(wire_diameter)
        self.set_wire_area(wire_area)

    def set_wire_diameter(self, diameter):
        if diameter is not None:
            self.wireArea_ = np.pi*diameter**2/4
        return self

    def set_wire_area(self, area):
        if area is not None:
            self.wireArea_ = area
        return self

    def _add(self, attr, name):
        setattr(self, attr, getattr(self, attr) + [name])
        return self

    def add_wire_feed_rate_key(self, name):
        return self._add('wireFeedRateKeys_', name)

    def add_melt_area_key(self, name):
        return self._add('meltAreaKeys_', name)

    def add_melt_velocity_key(self, name):
        return self._add('meltVelocityKeys_', name)

    def __call__(self, node):
        # --> get wireFeedRate
        wireFeedRate = get_first_non_null(node, self.wireFeedRateKeys_)
        # --> get wireArea
        wireArea = self.wireArea_
        # --> get meltArea
        meltArea = get_first_non_null(node, self.meltAreaKeys_)
        # --> get meltVelocity
        meltVelocity = get_first_non_null(node, self.meltVelocityKeys_)
        if ((wireFeedRate is not None) and
                (wireArea is not None) and
                (meltArea is not None) and
                (meltVelocity is not None)):
            log(f"Remelt ratio parameters: ({wireFeedRate}, {wireArea}, "
                f"{meltArea}, {meltVelocity})")
        try:
            # result = 1 - wireFeedRate*wireArea/meltArea/meltVelocity
            numerator = np.outer(np.asarray(wireFeedRate),
                                 np.asarray(wireFeedRate)).ravel()
            denominator = np.outer(np.asarray(meltArea),
                                   np.asarray(meltVelocity)).ravel()
            result = tuple((1 - np.outer(numerator, 1/denominator)).ravel())
            if len(result) == 1:
                result = result[0]
            log(f"Remelt ratio ({node.contents['Sample Name']}): {result}")
        except TypeError:
            result = None
        else:
            node.contents[self.name] = result
        return result


# ############### </Node Functions> ############### #


def get_attributes(root, exclude=("Sample Name", "Parent Sample Name")):
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
reader = ExcelIO(default=generic)\
    .set_header(4)\
    .set_sheet_name(None)

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
                             if not (is_null(v) and k != FID)}
            # ... add a contact field based on contact
            node.contents[CONTACT] = contact
        nodes.extend(new)
    except:
        print(f"Error while reading {fname}")
        raise

log(f"{len(nodes)} nodes constructed.")

# Generate trees that connect parent nodes ("Parent Sample Node") to
# child nodes ("Sample Name"). Any node that does not have a parent
# is a root. forest is a list of all roots generated from the nodes
# read above.
log("Generating tree structures...")

forest = generate_tree(
    get_nodeid=get(UID),
    get_parent=get(FID),
    cmp=strcmp(str.strip, str.lower))(nodes)

log(f"{len(forest)} trees generated.")

# generate a set of unique attributes across all root nodes (tree)
log("Generating attribute set...")
attributes = set()
for root in forest:
    attributes = attributes.union(get_attributes(root))
# attributes = list(attributes)
log(f"{len(attributes)} identified.")

# aggregate (collect data from child nodes) then propagate (push data
# down to children).
log("Aggregating/propagating between nodes...")
for root in forest:
    for attr in attributes:
        # propagate(attr)(root)
        # aggregate(get(attr), reduce=put(attr, overwrite=False))(root)
        # propagate(attr)(root)
        # aggregate and propagate reductions
        # for reduction in (mean_reduce(attr),):
        # for reduction in (flatten(attr),
        #                   mean(attr),
        #                   std(attr),
        #                   minimum(attr),
        #                   maximum(attr),
        #                   unique(attr)):
        # for reduction in (flatten(attr),
        #                   unique(attr)):
        for reduction in (flatten(attr),):
            aggregate(get(attr), reduce=reduction)(root)
            propagate(reduction.key)(root)
        propagate(attr)(root)
log("Finished aggregating/propagating data between nodes.")

log("Cleaning up empty attributes...")
# drop any propagated null values and the lists they create
for node in nodes:
    for key, value in iter(node.contents.items()):
        if is_container(value):
            reduced = [x for x in value if x is not None]
            if len(reduced) == 0:
                reduced = ''
            elif len(node.contents[key]) == 1:
                reduced = reduced[0]
            node.contents[key] = reduced
log("Finished cleaning empty attributes.")


# ############### Post aggregation functions ############### #
# this can easily be pulled into a yaml or json formatted input file...
remelt_ratio = RemeltRatio()\
    .set_wire_diameter(4.7)\
    .add_melt_velocity_key("Summary: Robot Travel Speed (mm/s)")\
    .add_wire_feed_rate_key("Summary: Wire Feed Speed (mm/s)")\
    .add_wire_feed_rate_key("Weld Main Stage Data: Heat Wirefeed Speed (mm/s)")\
    .add_melt_velocity_key("Weld Main Stage Data: Travel Speed (mm/s)")\
    .add_wire_feed_rate_key("Weld Fill Stage Data: Heat Wirefeed Speed (mm/s)")\
    .add_wire_feed_rate_key("Weld End Stage Data: Heat Wirefeed Speed (mm/s)")\
    .add_melt_area_key("Fusion zone area (mm^2)")

log("Calculating functions...")
for node in nodes:
    # operations calculated from accumulated data
    remelt_ratio(node)
    # vector statistics
    for key, value in list(node.contents.items()):
        for function in (Maximum(key),
                         Minimum(key),
                         Mean(key),
                         StdDev(key)):
            function(node)
log("Finished calculations.")

# create a dataframe from the node data.
# df = to_dataframe(nodes)
log("Generating pandas.DataFrame from roots...")
roots_only = to_dataframe(forest)
log(f"{len(roots_only)} records stored in roots DataFrame.")
log("Generating pandas.DataFrame from all nodes...")
full = to_dataframe(nodes)
log(f"{len(full)} records created from all nodes.")

# def to_excel(dataframe, filename):
#     """
#     Orders the data for writing to an Excel worksheet. "Sampe Name",
#     "Parent Sample Name", and "Contact" are treated as special columns
#     and ordered to appear as the first three columns in the worksheet.
#     Similarly, FILE objects are reordered to appear at the end.
#
#     :param dataframe: pandas.DataFrame containing the tabulated information
#         collected in previous steps.
#     :return: None
#     """
#     columns = dataframe.columns.to_list()
#     prepend = [UID, FID, CONTACT]
#     append = [col for col in columns if is_file_column(col)]
#     columns = prepend + \
#         [obj for obj in columns
#          if (obj not in prepend and obj not in append)] + \
#         append
#     df = dataframe[columns]
#     df.columns = pd.MultiIndex.from_tuples(
#         [ExcelIO.Key.to_index(name) for name in df.columns])
#     df.to_excel(filename, index=UID, engine='openpyxl')
#     #
#     # dataframe[columns].to_excel(filename,
#     #                             index=False,
#     #                             engine='xlsxwriter')


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
    from openpyxl import Workbook
    from openpyxl.utils.dataframe import dataframe_to_rows

    columns = dataframe.columns.to_list()
    prepend = [UID, FID, CONTACT]
    append = [col for col in columns if is_file_column(col)]
    columns = prepend + \
        [obj for obj in columns
         if (obj not in prepend and obj not in append)] + \
        append
    df = dataframe[columns]
    df.columns = pd.MultiIndex.from_tuples(
        [ExcelIO.Key.to_index(name) for name in df.columns])

    wb = Workbook()
    ws = wb.active
    for row in dataframe_to_rows(df, index=False, header=True):
        for i, cell in enumerate(row):
            if is_container(cell):
                row[i] = str(cell)
            elif issubclass(type(cell), type(pd.NaT)):
                row[i] = ''
        try:
            ws.append(row)
        except:
            _logger.debug(f"row: {row}")
            raise
    wb.save(filename)
    wb.close()
    #
    # dataframe[columns].to_excel(filename,
    #                             index=False,
    #                             engine='xlsxwriter')


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
        def utep_contact():
            return pif.Person(name='Hunter C. Taylor',
                              email='hctaylor@miners.utep.edu',
                              tags='University of Texas, El Paso')
        def cmu_contact():
            return pif.Person(name='Anthony Rollett',
                              email='rollett@andrew.cmu.edu',
                              tags='Carnegie Mellon University')
        def mines_contact():
            return pif.Person(name='Craig Brice',
                              email='craigbrice@mines.edu',
                              tags='Colorado School of Mines')

        # Every PIF record is a System object
        system = pif.System()
        # create a unique identifier. This must be URL friendly.
        uid = ExcelIO.Key.replace_sep(str(row[UID]), " ")
        fid = ExcelIO.Key.replace_sep(str(row[FID]), " ")
        system.uid = url_friendly(uid)
        # name the PIF
        system.names = uid
        # record the parent sample name
        system.sub_systems = pif.System(
            uid=url_friendly(fid),
            names=uid)
        # set the contact information. By default, I set this as LMCO.
        system.contacts = {
            'UTEP': utep_contact,
            'CMU': cmu_contact,
            'Mines': mines_contact}.get(row[CONTACT], cmu_contact)()

        # Certain fields we treat as special
        special = [UID, FID, CONTACT]
        filelist = None
        for column, value in row.items():
            # special columns have already been handled.
            if column in special:
                continue
            # no need to record empty record.
            if is_null(value):
                continue
            # handle FILEs.
            if is_file_column(column):
                # add the FILE column to the list of special columns
                # so we don't add this as a property.
                special.append(column)
                # split on colon -- we don't need "FILE" in the name
                name = column[1]
                # Convert the filename (or the string-representation of
                # a list of filenames, e.g. [file1.png, file2.png]) to
                # a list of files
                value = str(value).strip("[]").strip("()").split(",")
                # create a file reference for each file and store these as
                # a list of FileReference objects.
                for path in value:
                    file = pif.FileReference(relative_path=str(path),
                                             tags=':'.join(name[1:]).strip())
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
            value = {pd.Timestamp: str,
                     tuple: list}.get(type(value), type(value))(value)
            # otherwise, construct a property value.
            try:
                pty = pif.Property(name=ExcelIO.Key.replace_sep(column, ' '),
                                   scalars=value)
            except:
                pty = pif.Property(name=ExcelIO.Key.replace_sep(column, ' '),
                                   scalars=str(value))
                # print(f"{column}: {value}")
                # raise
            # units are stored, by convention in parentheses, e.g.
            # laser speed (mm/s). This regular expression extracts the the
            # last term surrounded by parentheses.
            pty.units = get_units(column)
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


# save the results to Excel and PIF
# for rendering on Citrine.
log("Writing roots DataFrame to Excel and PIF...")
to_excel(roots_only, f"{output_prefix}-roots.xlsx")
to_pif(roots_only, f"{output_prefix}-roots.json")
log("Finished writing roots DataFrame to Excel and PIF.")

log("Writing nodes DataFrame to Excel and PIF...")
to_excel(full, f"{output_prefix}-full.xlsx")
to_pif(full, f"{output_prefix}-full.json")
log("Finished writing nodes DataFrame to Excel and PIF.")
