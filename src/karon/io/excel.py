from .base import BaseIO
from .pandas import to_dataframe
import ast
import pandas as pd


class ExcelIO(BaseIO):
    """
    Reads data from (optionally multiple) worksheets in Microsoft Excel.
    """
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)


    def load(self, fobj, *args, **kwds):
        """
        Loads node data from the specified Excel workbook.

        :param filename: File to be read.
        :type filename: valid io object to pandas.read_excel.
        :param sheet_name: Sheetnames to be read. Default: all.
        :type sheet_name: str, iterable of str, or None (all, default)
        :return: Nodes read from the Excel workbook.
        :rtype: list of Nodes
        """
        def convert(obj):
            """
            Pandas `read_excel` has the `converters` option that allows the
            user to specify converters for each column. The value of this
            option must be a dictionary that maps the column name or index
            of the column to a function that accepts the cell data (as a
            string) and returns the converted value.

            If python-style lists, tuples, dictionaries, etc. are stored
            in an Excel cell, Converter calls ast.literal_eval as a conversion
            for each cell regardless of the key (column name/column index).
            """
            try:
                return ast.literal_eval(obj)
            except (ValueError, SyntaxError):
                return obj

        # Process all parameters to read_excel
        for i, key in enumerate(('sheet_name',
                                 'header',
                                 'skiprows',
                                 'skip_footer',
                                 'index_col',
                                 'names',
                                 'usecols',
                                 'parse_dates',
                                 'date_parser',
                                 'na_values',
                                 'thousands',
                                 'convert_float',
                                 'converters',
                                 'dtype',
                                 'true_values',
                                 'false_values',
                                 'engine',
                                 'squeeze')):
            try:
                kwds[key] = args[i]
            except IndexError:
                break
        # set defaults, e.g. sheet_name --> None
        kwds['sheet_name'] = kwds.get('sheet_name', None)
        # read the file
        df = pd.read_excel(fobj, **kwds)
        # convert each element to handle lists, tuples, etc.
        for sheet_name in df:
            df[sheet_name] = df[sheet_name].applymap(convert)
        # convert each entry into a node
        nodes = [self[key](**row)
                 for key in df.keys()
                 for (index, row) in df[key].iterrows()]
        # done
        return nodes

    def dump(self, fobj, *args, **kwds):
        """
        Dumps args (lists of nodes) to a file-like object.

        :param fobj: File-like object to which the nodes are written in Excel
            format.
        :type fobj: File-like object (str or file)
        :param args: Lists of nodes that are to be written to the file object.
        :type args: list of nodes
        :param kwds: Not used.
        :return: None
        """
        nodes = []
        for arg in args:
            nodes.extend(arg)
        to_dataframe(nodes).to_excel(fobj, index=False)


# def read_excel(*args, **kwds):
#     """
#     Reads data from an excel file and applies a conversion to each
#     element allowing the cells to hold lists/tuples, and dictionaries in
#     addition to scalar values.
#
#     :param args: Positional parameters for `pandas.read_excel`
#     :param kwds: Optional parameters for `pandas.read_excel`
#     :returns: pandas.DataFrame
#     """
#     def convert(obj):
#         """
#         Pandas `read_excel` has the `converters` option that allows the
#         user to specify converters for each column. The value of this
#         option must be a dictionary that maps the column name or index
#         of the column to a function that accepts the cell data (as a
#         string) and returns the converted value.
#
#         If python-style lists, tuples, dictionaries, etc. are stored
#         in an Excel cell, Converter calls ast.literal_eval as a conversion
#         for each cell regardless of the key (column name/column index).
#         """
#         try:
#             return ast.literal_eval(obj)
#         except (ValueError, SyntaxError):
#             return obj
#
#     # Process all parameters to read_excel
#     for i,key in enumerate(('io',
#                             'sheet_name',
#                             'header',
#                             'skiprows',
#                             'skip_footer',
#                             'index_col',
#                             'names',
#                             'usecols',
#                             'parse_dates',
#                             'date_parser',
#                             'na_values',
#                             'thousands',
#                             'convert_float',
#                             'converters',
#                             'dtype',
#                             'true_values',
#                             'false_values',
#                             'engine',
#                             'squeeze')):
#         try:
#             kwds[key] = args[i]
#         except IndexError:
#             break
#     # set defaults, e.g. sheet_name --> None
#     if 'sheet_name' not in kwds:
#         kwds['sheet_name'] = None
#     df = pd.read_excel(**kwds)
#     # convert each element to handle lists, tuples, etc.
#     return df.applymap(convert)
