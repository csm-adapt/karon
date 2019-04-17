import re
import pandas as pd
import numpy as np
from karon import Sample
from karon.decorators import readwrite, requires
from karon.io import read_excel
from karon.tree.build import from_parent
from karon.tree import NLRTree


@readwrite
@requires("name", "parent name")
def generic(**contents):
    return Sample(**contents)


@readwrite
@requires("name", "parent name")
def build(**contents):
    return Sample(**contents)


@readwrite
@requires("name", "parent name")
def mechanical(**contents):
    return Sample(**contents)


@readwrite
@requires("name", "parent name")
def porosity(**contents):
    return Sample(**contents)


class Example(object):
    _uid_key: str
    _parent_key: str

    def __init__(self, uid: str, parent: str):
        """
        Create an example object for reading and processing an structured
        data object into a hierarchical data object.

        :param uid: Key (column name) that uniquely identifies a sample.
        :type uid: str
        :param parent: Key (column name) that identifies from which sample
            a child node descends.
        :type parent: str
        """
        self._uid_key = uid
        self._parent_key = parent
        self._filenames = []
        self._nodes = {}
        self.roots = []

    def get_uid(self, entry):
        """Returns the unique identifier for the given dictionary."""
        try:
            key = [k for k in entry.keys()
                   if re.match(self._uid_key, k, flags=re.IGNORECASE)][0]
        except IndexError:
            raise KeyError(f'The unique identifier field ({self._uid_key})'
                           f'was not found.')
        return entry[key]

    @staticmethod
    def node_generator_from_sheetname(sheetname):
        return {
            'build': build,
            'mechanical': mechanical,
            'porosity': porosity
        }.get(sheetname, generic)

    def excel_reader(self, filename):
        """
        Reads data from an excel file and maps the nodes to their names.

        :param filename: (str) Excel file containing sample information.
        :return: (dict) Maps UIDs to the nodes.
        """
        nodes = {}
        # get sheet names
        xls = pd.ExcelFile(filename)
        for sheetName in xls.sheet_names:
            # read in each sheet
            df = read_excel(filename, sheetName)
            # read nodes into dictionary
            for entry in df.to_dict('records'):
                uid = self.get_uid(entry)
                if uid in nodes:
                    raise KeyError('Sample names must be unique. '
                                   '{} is duplicated'.format(uid))
                else:
                    nodes[uid] = Example.node_generator_from_sheetname(
                        sheetName)(**entry)
            # return dictionary of nodes.
        return nodes

    @staticmethod
    def filetype(filename):
        """
        Guess the file type from the file name.

        :param filename: Name of the file to be read.
        :type filename: str
        :return: Keyword/phrase to describe the file type.
        :rtype: str
        """
        if (filename.lower().endswith('xls') or
                filename.lower().endswith('xlsx')):
            return 'excel'
        else:
            raise ValueError(f"Filetype of {filename} could not be identified.")

    def read(self, *filenames):
        """
        Reads the list of filenames. They types are inferred using
        the filetype function.

        :param filenames: Filenames to be read.
        :type filenames: tuple of str
        :return: None. (Updates the list of nodes.)
        """
        for afilename in filenames:
            # get reader
            reader = {
                'excel': self.excel_reader
            }[Example.filetype(afilename)]
            # read this file
            nodes = reader(afilename)
            # save that this file was read
            self._filenames.append(afilename)
            # look for duplicate nodes
            intersection = set(
                self._nodes.keys()).intersection(set(nodes.keys()))
            if len(intersection) != 0:
                raise KeyError(f'At least one duplicate entry ({intersection}) '
                               f'found while reading {filenames}')
            else:
                self._nodes.update(nodes)
        self.build_trees()

    def build_trees(self):
        """
        Build trees based on Excel structure.

        :return: None. (Updates list of roots in this instance.)
        """
        self.roots = from_parent(self._nodes, key=self._parent_key)

    def get_all_keys(self):
        self.build_trees()
        keys = set()
        for root in self.roots:
            for node in NLRTree(root):
                keys = keys.union(set(node.contents.keys()))
        return tuple(keys)

    def propagate(self, *keys, overwrite: bool = False):
        """
        Passes information down to the child nodes, if they are writeable.

        :param key: The properties/features to be passed down to the children.
            If no key is given inherit all keys.
        :type key: str
        :param overwrite: Should the value being pushed to the children
            overwrite an existing entry? Default: False.
        :type overwrite: bool
        :param callback: Unary function generator that takes
        :return: None
        """
        def get_from(root, key):
            def func(node):
                nodeval = node.contents.get(key, '')
                if nodeval in ('', None) or overwrite:
                    node.contents[key] = rootval
                return

            rootval = root.contents.get(key, '')
            return func

        # propagate all keys, if no key is given
        if len(keys) == 0 or keys[0] is None:
            keys = self.get_all_keys()
        # pass
        # run through all keys
        for akey in keys:
            for root in self.roots:
                for node in NLRTree(root):
                    push = get_from(node, akey)
                    for sub in NLRTree(node):
                        sub.puts(func=push)

    @staticmethod
    def mean(key):
        def func(node, vec):
            vec = [x for x in vec if x is not None]
            try:
                if len(vec) > 0:
                    node.contents[key] = np.mean(vec)
            except TypeError:
                pass
        return func

    @staticmethod
    def store(key):
        def func(node, vec):
            node.contents[key] = vec
        return func

    @staticmethod
    def fetch(key):
        def func(node):
            return node.contents.get(key, None)
        return func

    def aggregate(self, *keys, reduce=None):
        """
        Applies a reduction operation to each node. The aggregation is
        done from the root node downward so that the attributes for the
        descendant nodes are not populated until after the predecessor
        nodes.

        :param keys: Feature to reduce and combine into the each parent node.
            If none are given, then reduce on all keys.
        :type key: tuple(str)
        :param reduce: Function generator used to reduce the collected
            results. This generator takes a single parameter, a string,
            that indicates where the result should be stored. The default
            is a function that simply stores the vector-result of the
            aggregation. See examples.
        :type reduce: unary function
        :return: None.
        """
        # handle the default values for aggregate
        reduce = {
            None: Example.store,
            'store': Example.store}.get(reduce, reduce)
        # reduce on all keys, if no key is given
        if len(keys) == 0 or keys[0] is None:
            keys = self.get_all_keys()
        # reduce on keys twice: once to populate each node from its
        # descendents, and once again to populate antecedents from
        # descendents that were populated in the first iteration.
        for iteration in range(2):
            for key in keys:
                for root in self.roots:
                    # perform reduction
                    for node in NLRTree(root):
                        # if node contains a value, do not replace with
                        # the reduced value.
                        if key in node.contents:
                            continue
                        else:
                            node.gets(func=Example.fetch(key),
                                      callback=reduce(key))
