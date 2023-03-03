from datetime import datetime

import numpy as np
import pytest

from pandas import (
    DataFrame,
    Index,
    Series,
)
import pandas._testing as tm
from pandas.tests.groupby import get_groupby_method_args


@pytest.mark.parametrize(
    "obj",
    [
        tm.SubclassedDataFrame({"A": np.arange(0, 10)}),
        tm.SubclassedSeries(np.arange(0, 10), name="A"),
    ],
)
def test_groupby_preserves_subclass(obj, groupby_func):
    # GH28330 -- preserve subclass through groupby operations

    if isinstance(obj, Series) and groupby_func in {"corrwith"}:
        pytest.skip(f"Not applicable for Series and {groupby_func}")

    grouped = obj.groupby(np.arange(0, 10))

    # Groups should preserve subclass type
    assert isinstance(grouped.get_group(0), type(obj))

    args = get_groupby_method_args(groupby_func, obj)

    result1 = getattr(grouped, groupby_func)(*args)
    result2 = grouped.agg(groupby_func, *args)

    # Reduction or transformation kernels should preserve type
    slices = {"ngroup", "cumcount", "size"}
    if isinstance(obj, DataFrame) and groupby_func in slices:
        assert isinstance(result1, tm.SubclassedSeries)
    else:
        assert isinstance(result1, type(obj))

    # Confirm .agg() groupby operations return same results
    if isinstance(result1, DataFrame):
        tm.assert_frame_equal(result1, result2)
    else:
        tm.assert_series_equal(result1, result2)


def test_groupby_preserves_metadata():
    # GH-37343
    custom_df = tm.SubclassedDataFrame({"a": [1, 2, 3], "b": [1, 1, 2], "c": [7, 8, 9]})
    assert "testattr" in custom_df._metadata
    custom_df.testattr = "hello"
    for _, group_df in custom_df.groupby("c"):
        assert group_df.testattr == "hello"

    # GH-45314
    def func(group):
        assert isinstance(group, tm.SubclassedDataFrame)
        assert hasattr(group, "testattr")
        return group.testattr

    result = custom_df.groupby("c").apply(func)
    expected = tm.SubclassedSeries(["hello"] * 3, index=Index([7, 8, 9], name="c"))
    tm.assert_series_equal(result, expected)

    def func2(group):
        assert isinstance(group, tm.SubclassedSeries)
        assert hasattr(group, "testattr")
        return group.testattr

    custom_series = tm.SubclassedSeries([1, 2, 3])
    custom_series.testattr = "hello"
    result = custom_series.groupby(custom_df["c"]).apply(func2)
    tm.assert_series_equal(result, expected)
    result = custom_series.groupby(custom_df["c"]).agg(func2)
    tm.assert_series_equal(result, expected)


@pytest.mark.parametrize("obj", [DataFrame, tm.SubclassedDataFrame])
def test_groupby_resample_preserves_subclass(obj):
    # GH28330 -- preserve subclass through groupby.resample()

    df = obj(
        {
            "Buyer": "Carl Carl Carl Carl Joe Carl".split(),
            "Quantity": [18, 3, 5, 1, 9, 3],
            "Date": [
                datetime(2013, 9, 1, 13, 0),
                datetime(2013, 9, 1, 13, 5),
                datetime(2013, 10, 1, 20, 0),
                datetime(2013, 10, 3, 10, 0),
                datetime(2013, 12, 2, 12, 0),
                datetime(2013, 9, 2, 14, 0),
            ],
        }
    )
    df = df.set_index("Date")

    # Confirm groupby.resample() preserves dataframe type
    result = df.groupby("Buyer").resample("5D").sum()
    assert isinstance(result, obj)


def test_groupby_overridden_methods():
    class UnitSeries(Series):
        @property
        def _constructor(self):
            return UnitSeries

        @property
        def _constructor_expanddim(self):
            return UnitDataFrame

        def mean(self, *args, **kwargs):
            return 1

        def median(self, *args, **kwargs):
            return 2

        def std(self, *args, **kwargs):
            return 3

        def var(self, *args, **kwargs):
            return 4

        def sem(self, *args, **kwargs):
            return 5

        def prod(self, *args, **kwargs):
            return 6

        def min(self, *args, **kwargs):
            return 7

        def max(self, *args, **kwargs):
            return 8

    class UnitDataFrame(DataFrame):
        @property
        def _constructor(self):
            return UnitDataFrame

        @property
        def _constructor_expanddim(self):
            return UnitSeries

        def mean(self, *args, **kwargs):
            return 1

        def median(self, *args, **kwargs):
            return 2

        def std(self, *args, **kwargs):
            return 3

        def var(self, *args, **kwargs):
            return 4

        def sem(self, *args, **kwargs):
            return 5

        def prod(self, *args, **kwargs):
            return 6

        def min(self, *args, **kwargs):
            return 7

        def max(self, *args, **kwargs):
            return 8

    params = ["a", "b"]
    data = np.random.rand(4, 2)
    udf = UnitDataFrame(data, columns=params)
    udf["group"] = np.ones(4, dtype=int)
    udf.loc[2:, "group"] = 2

    assert all(udf.groupby("group").mean() == 1)
    assert all(udf.groupby("group").median() == 2)
    assert all(udf.groupby("group").std() == 3)
    assert all(udf.groupby("group").var() == 4)
    assert all(udf.groupby("group").sem() == 5)
    assert all(udf.groupby("group").prod() == 6)
    assert all(udf.groupby("group").min() == 7)
    assert all(udf.groupby("group").max() == 8)
