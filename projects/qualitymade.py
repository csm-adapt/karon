import pandas as pd
from convey.process import (build, vickers, xct)
from convey.io import read_excel as general_excel_reader
from convey.tree.build import from_parent
import re


def _get_uid(entry):
    """Returns the unique identifier for the given dictionary."""
    try:
        key = [k for k in entry.keys()
               if re.match(r'name', k, flags=re.IGNORECASE)][0]
    except IndexError:
        raise KeyError('The unique identifier field (name) was not found.')
    return entry[key]


def _sheetname_to_node_generator(sheetname):
    """Returns a mapping from the given sheet name to a node generator."""
    return {'prints': build,
            'Hardness (Vickers)': vickers,
            'CT (porosity)': xct}[sheetname]


def _normalize_tracking_xlsx_column_names(dataframe):
    """Cleans column names"""
    # drop prefix
    prefix = re.compile(r'^(SUBSYSTEM):*\s*')
    columns = [re.sub(prefix, '', col) for col in dataframe.columns]
    # lowercase keys
    for idx,col in enumerate(columns):
        if col in ('NAME', 'PARENT NAME'):
            columns[idx] = col.lower()
    # change dataframe column names
    dataframe.columns = columns


def _read_excel(filename, nodes={}):
    """
    Reads data from an excel file and maps the nodes to their names.

    :param filename: (str) Excel file containing sample information.
    :param nodes: (dict) Existing dictionary of nodes, e.g. from another
        excel file, CSV, etc.
    :return: (dict) Maps UIDs to the nodes.
    """
    # get sheet names
    xls = pd.ExcelFile(filename)
    for sheetName in xls.sheet_names:
        # read in each sheet
        df = general_excel_reader(filename, sheetName)
        # normalize the column names
        _normalize_tracking_xlsx_column_names(df)
        # read nodes into dictionary
        for entry in df.to_dict('records'):
            uid = _get_uid(entry)
            if uid in nodes:
                raise KeyError('Sample names must be unique. '
                               '{} is duplicated'.format(uid))
            else:
                nodes[uid] = _sheetname_to_node_generator(sheetName)(**entry)
    # return dictionary of nodes.
    return nodes


def filetype(filename):
    if filename.lower().endswith('xls') or filename.lower().endswith('xlsx'):
        return 'excel'
    else:
        raise ValueError(f"Filetype of {filename} could not be identified.")


def read(*filenames):
    nodes = {}
    for afilename in filenames:
        reader = {
            'excel': _read_excel
        }[filetype(afilename)]
        nodes = reader(afilename, nodes)
    # assert False, '\n'.join([f'{k}: {v.contents}' for k, v in iter(nodes.items())])
    return from_parent(nodes, key='parent name')
