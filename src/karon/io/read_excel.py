import ast
import pandas as pd


def read_excel(*args, **kwds):
    """
    Reads data from an excel file and applies a conversion to each
    element allowing the

    :param args: Positional parameters for `pandas.read_excel`
    :param kwds: Optional parameters for `pandas.read_excel`
    :returns: pandas.DataFrame
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

    df = pd.read_excel(*args, **kwds)
    # convert each element to handle lists, tuples, etc.
    return df.applymap(convert)
