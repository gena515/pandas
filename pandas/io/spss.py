from typing import Union, Sequence
from pandas.core.api import DataFrame


def read_spss(path: str,
              usecols: Union[str, Sequence[str], None] = None,
              categorical: bool = True) -> DataFrame:
    """
    Load an SPSS file from the file path, returning a DataFrame.

    .. versionadded 0.25.0

    Parameters
    ----------
    path : string
        File path
    usecols : str or list-like or None
        Return a subset of the columns. If None, return all columns.
    categorical : bool
        Convert categorical columns into pd.Categorical.

    Returns
    -------
    DataFrame
    """

    from pyreadstat import read_sav
    if usecols is not None:
        if isinstance(usecols, str):
            usecols = [usecols]
    df, _ = read_sav(path, usecols=usecols,
                     apply_value_formats=categorical)
    return df
