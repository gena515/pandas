import numpy as np

import pandas as pd
from pandas.util import testing as tm


def test_basic():
    s = pd.Series([[0, 1, 2], np.nan, [], (3, 4)], name="foo")
    result = s.explode()
    expected = pd.Series(
        [0, 1, 2, np.nan, np.nan, 3, 4],
        index=[0, 0, 0, 1, 2, 3, 3],
        dtype=object,
        name="foo",
    )
    tm.assert_series_equal(result, expected)


def test_mixed_type():
    s = pd.Series(
        [[0, 1, 2], np.nan, None, np.array([]), pd.Series(["a", "b"])], name="foo"
    )
    result = s.explode()
    expected = pd.Series(
        [0, 1, 2, np.nan, None, np.nan, "a", "b"],
        index=[0, 0, 0, 1, 2, 3, 4, 4],
        dtype=object,
        name="foo",
    )
    tm.assert_series_equal(result, expected)


def test_empty():
    s = pd.Series()
    result = s.explode()
    expected = s.copy()
    tm.assert_series_equal(result, expected)


def test_multi_index():
    s = pd.Series(
        [[0, 1, 2], np.nan, [], (3, 4)],
        name="foo",
        index=pd.MultiIndex.from_product([list("ab"), range(2)], names=["foo", "bar"]),
    )
    result = s.explode()
    index = pd.MultiIndex.from_tuples(
        [("a", 0), ("a", 0), ("a", 0), ("a", 1), ("b", 0), ("b", 1), ("b", 1)],
        names=["foo", "bar"],
    )
    expected = pd.Series(
        [0, 1, 2, np.nan, np.nan, 3, 4], index=index, dtype=object, name="foo"
    )
    tm.assert_series_equal(result, expected)


def test_large():
    s = pd.Series([range(256)]).explode()
    result = s.explode()
    tm.assert_series_equal(result, s)


def test_invert_array():
    df = pd.DataFrame({"a": pd.date_range("20190101", periods=3, tz="UTC")})

    listify = df.apply(lambda x: x.array, axis=1)
    result = listify.explode()
    tm.assert_series_equal(result, df["a"].rename())
