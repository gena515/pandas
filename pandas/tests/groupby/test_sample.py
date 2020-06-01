from copy import copy

import numpy as np
import pytest

from pandas.compat.numpy import _np_version_under1p17

from pandas import DataFrame, Index, Series
import pandas._testing as tm


@pytest.mark.parametrize("n, frac", [(2, None), (None, 0.2)])
def test_groupby_sample_balanced_groups_shape(n, frac):
    values = [1] * 10 + [2] * 10
    df = DataFrame({"a": values, "b": values})

    result = df.groupby("a").sample(n=n, frac=frac)
    values = [1] * 2 + [2] * 2
    expected = DataFrame({"a": values, "b": values}, index=result.index)
    tm.assert_frame_equal(result, expected)

    result = df.groupby("a")["b"].sample(n=n, frac=frac)
    expected = Series(values, name="b", index=result.index)
    tm.assert_series_equal(result, expected)


def test_groupby_sample_unbalanced_groups_shape():
    values = [1] * 10 + [2] * 20
    df = DataFrame({"a": values, "b": values})

    result = df.groupby("a").sample(n=5)
    values = [1] * 5 + [2] * 5
    expected = DataFrame({"a": values, "b": values}, index=result.index)
    tm.assert_frame_equal(result, expected)

    result = df.groupby("a")["b"].sample(n=5)
    expected = Series(values, name="b", index=result.index)
    tm.assert_series_equal(result, expected)


def test_groupby_sample_index_value_spans_groups():
    values = [1] * 3 + [2] * 3
    df = DataFrame({"a": values, "b": values}, index=[1, 2, 2, 2, 2, 2])

    result = df.groupby("a").sample(n=2)
    values = [1] * 2 + [2] * 2
    expected = DataFrame({"a": values, "b": values}, index=result.index)
    tm.assert_frame_equal(result, expected)

    result = df.groupby("a")["b"].sample(n=2)
    expected = Series(values, name="b", index=result.index)
    tm.assert_series_equal(result, expected)


def test_groupby_sample_n_and_frac_raises():
    df = DataFrame({"a": [1, 2], "b": [1, 2]})
    msg = "Please enter a value for `frac` OR `n`, not both"

    with pytest.raises(ValueError, match=msg):
        df.groupby("a").sample(n=1, frac=1.0)

    with pytest.raises(ValueError, match=msg):
        df.groupby("a")["b"].sample(n=1, frac=1.0)


def test_groupby_sample_frac_gt_one_without_replacement_raises():
    df = DataFrame({"a": [1, 2], "b": [1, 2]})
    msg = "Replace has to be set to `True` when upsampling the population `frac` > 1."

    with pytest.raises(ValueError, match=msg):
        df.groupby("a").sample(frac=1.5, replace=False)

    with pytest.raises(ValueError, match=msg):
        df.groupby("a")["b"].sample(frac=1.5, replace=False)


@pytest.mark.parametrize("n", [-1, 1.5])
def test_groupby_sample_invalid_n_raises(n):
    df = DataFrame({"a": [1, 2], "b": [1, 2]})

    if n < 0:
        msg = "Please provide positive value"
    else:
        msg = "Only integers accepted as `n` values"

    with pytest.raises(ValueError, match=msg):
        df.groupby("a").sample(n=n)

    with pytest.raises(ValueError, match=msg):
        df.groupby("a")["b"].sample(n=n)


def test_groupby_sample_oversample():
    values = [1] * 10 + [2] * 10
    df = DataFrame({"a": values, "b": values})

    result = df.groupby("a").sample(frac=2.0, replace=True)
    values = [1] * 20 + [2] * 20
    expected = DataFrame({"a": values, "b": values}, index=result.index)
    tm.assert_frame_equal(result, expected)

    result = df.groupby("a")["b"].sample(frac=2.0, replace=True)
    expected = Series(values, name="b", index=result.index)
    tm.assert_series_equal(result, expected)


def test_groupby_sample_without_n_or_frac():
    values = [1] * 10 + [2] * 10
    df = DataFrame({"a": values, "b": values})

    result = df.groupby("a").sample(n=None, frac=None)
    expected = DataFrame({"a": [1, 2], "b": [1, 2]}, index=result.index)
    tm.assert_frame_equal(result, expected)

    result = df.groupby("a")["b"].sample(n=None, frac=None)
    expected = Series([1, 2], name="b", index=result.index)
    tm.assert_series_equal(result, expected)


def test_groupby_sample_with_weights():
    values = [1] * 2 + [2] * 2
    df = DataFrame({"a": values, "b": values}, index=Index([0, 1, 2, 3]))

    result = df.groupby("a").sample(n=2, replace=True, weights=[1, 0, 1, 0])
    expected = DataFrame({"a": values, "b": values}, index=Index([0, 0, 2, 2]))
    tm.assert_frame_equal(result, expected)

    result = df.groupby("a")["b"].sample(n=2, replace=True, weights=[1, 0, 1, 0])
    expected = Series(values, name="b", index=Index([0, 0, 2, 2]))
    tm.assert_series_equal(result, expected)


@pytest.mark.parametrize(
    "random_state", [0, np.array([0, 1, 2]), np.random.RandomState(0)],
)
def test_groupby_sample_using_random_state(random_state):
    df = DataFrame({"a": [1] * 50 + [2] * 50, "b": np.arange(100)})
    rs = copy(random_state)
    expected = df.groupby("a").sample(frac=0.5, random_state=rs)
    rs = random_state
    result = df.groupby("a").sample(frac=0.5, random_state=rs)
    tm.assert_frame_equal(result, expected)


@pytest.mark.skipif(_np_version_under1p17, reason="Skipping for numpy version < 1.17")
@pytest.mark.parametrize(
    "random_state", [np.random.PCG64(0), np.random.MT19937(0)],
)
def test_groupby_sample_using_bitgenerator(random_state):
    df = DataFrame({"a": [1] * 50 + [2] * 50, "b": np.arange(100)})
    rs = copy(random_state)
    expected = df.groupby("a").sample(frac=0.5, random_state=rs)
    rs = random_state
    result = df.groupby("a").sample(frac=0.5, random_state=rs)
    tm.assert_frame_equal(result, expected)
