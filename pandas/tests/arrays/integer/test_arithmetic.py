import operator

import numpy as np
import pytest

import pandas as pd
import pandas._testing as tm
from pandas.core.arrays import integer_array
import pandas.core.ops as ops

# Basic test for the arithmetic array ops
# -----------------------------------------------------------------------------


@pytest.mark.parametrize(
    "opname, exp",
    [("add", [1, 3, None, None, 9]), ("mul", [0, 2, None, None, 20])],
    ids=["add", "mul"],
)
def test_add_mul(dtype, opname, exp):
    a = pd.array([0, 1, None, 3, 4], dtype=dtype)
    b = pd.array([1, 2, 3, None, 5], dtype=dtype)

    # array / array
    expected = pd.array(exp, dtype=dtype)

    op = getattr(operator, opname)
    result = op(a, b)
    tm.assert_extension_array_equal(result, expected)

    op = getattr(ops, "r" + opname)
    result = op(a, b)
    tm.assert_extension_array_equal(result, expected)


def test_sub(dtype):
    a = pd.array([1, 2, 3, None, 5], dtype=dtype)
    b = pd.array([0, 1, None, 3, 4], dtype=dtype)

    result = a - b
    expected = pd.array([1, 1, None, None, 1], dtype=dtype)
    tm.assert_extension_array_equal(result, expected)


def test_div(dtype):
    # for now division gives a float numpy array
    a = pd.array([1, 2, 3, None, 5], dtype=dtype)
    b = pd.array([0, 1, None, 3, 4], dtype=dtype)

    result = a / b
    expected = np.array([np.inf, 2, np.nan, np.nan, 1.25], dtype="float64")
    tm.assert_numpy_array_equal(result, expected)


@pytest.mark.parametrize("zero, negative", [(0, False), (0.0, False), (-0.0, True)])
def test_divide_by_zero(zero, negative):
    # https://github.com/pandas-dev/pandas/issues/27398
    a = pd.array([0, 1, -1, None], dtype="Int64")
    result = a / zero
    expected = np.array([np.nan, np.inf, -np.inf, np.nan])
    if negative:
        expected *= -1
    tm.assert_numpy_array_equal(result, expected)


def test_floordiv(dtype):
    a = pd.array([1, 2, 3, None, 5], dtype=dtype)
    b = pd.array([0, 1, None, 3, 4], dtype=dtype)

    result = a // b
    # Series op sets 1//0 to np.inf, which IntegerArray does not do (yet)
    expected = pd.array([0, 2, None, None, 1], dtype=dtype)
    tm.assert_extension_array_equal(result, expected)


def test_mod(dtype):
    a = pd.array([1, 2, 3, None, 5], dtype=dtype)
    b = pd.array([0, 1, None, 3, 4], dtype=dtype)

    result = a % b
    expected = pd.array([0, 0, None, None, 1], dtype=dtype)
    tm.assert_extension_array_equal(result, expected)


def test_pow_scalar():
    a = pd.array([-1, 0, 1, None, 2], dtype="Int64")
    result = a ** 0
    expected = pd.array([1, 1, 1, 1, 1], dtype="Int64")
    tm.assert_extension_array_equal(result, expected)

    result = a ** 1
    expected = pd.array([-1, 0, 1, None, 2], dtype="Int64")
    tm.assert_extension_array_equal(result, expected)

    result = a ** pd.NA
    expected = pd.array([None, None, 1, None, None], dtype="Int64")
    tm.assert_extension_array_equal(result, expected)

    result = a ** np.nan
    expected = np.array([np.nan, np.nan, 1, np.nan, np.nan], dtype="float64")
    tm.assert_numpy_array_equal(result, expected)

    # reversed
    a = a[1:]  # Can't raise integers to negative powers.

    result = 0 ** a
    expected = pd.array([1, 0, None, 0], dtype="Int64")
    tm.assert_extension_array_equal(result, expected)

    result = 1 ** a
    expected = pd.array([1, 1, 1, 1], dtype="Int64")
    tm.assert_extension_array_equal(result, expected)

    result = pd.NA ** a
    expected = pd.array([1, None, None, None], dtype="Int64")
    tm.assert_extension_array_equal(result, expected)

    result = np.nan ** a
    expected = np.array([1, np.nan, np.nan, np.nan], dtype="float64")
    tm.assert_numpy_array_equal(result, expected)


def test_pow_array():
    a = integer_array([0, 0, 0, 1, 1, 1, None, None, None])
    b = integer_array([0, 1, None, 0, 1, None, 0, 1, None])
    result = a ** b
    expected = integer_array([1, 0, None, 1, 1, 1, 1, None, None])
    tm.assert_extension_array_equal(result, expected)


def test_rpow_one_to_na():
    # https://github.com/pandas-dev/pandas/issues/22022
    # https://github.com/pandas-dev/pandas/issues/29997
    arr = integer_array([np.nan, np.nan])
    result = np.array([1.0, 2.0]) ** arr
    expected = np.array([1.0, np.nan])
    tm.assert_numpy_array_equal(result, expected)


@pytest.mark.parametrize("other", [0, 0.5])
def test_numpy_zero_dim_ndarray(other):
    arr = integer_array([1, None, 2])
    result = arr + np.array(other)
    expected = arr + other
    tm.assert_equal(result, expected)


# Test generic charachteristics / errors
# -----------------------------------------------------------------------------


def test_error_invalid_values(data, all_arithmetic_operators):

    op = all_arithmetic_operators
    s = pd.Series(data)
    ops = getattr(s, op)

    # invalid scalars
    msg = (
        r"(:?can only perform ops with numeric values)"
        r"|(:?IntegerArray cannot perform the operation mod)"
    )
    with pytest.raises(TypeError, match=msg):
        ops("foo")
    with pytest.raises(TypeError, match=msg):
        ops(pd.Timestamp("20180101"))

    # invalid array-likes
    with pytest.raises(TypeError, match=msg):
        ops(pd.Series("foo", index=s.index))

    if op != "__rpow__":
        # TODO(extension)
        # rpow with a datetimelike coerces the integer array incorrectly
        msg = (
            "can only perform ops with numeric values|"
            "cannot perform .* with this index type: DatetimeArray|"
            "Addition/subtraction of integers and integer-arrays "
            "with DatetimeArray is no longer supported. *"
        )
        with pytest.raises(TypeError, match=msg):
            ops(pd.Series(pd.date_range("20180101", periods=len(s))))


# Various
# -----------------------------------------------------------------------------


# TODO test unsigned overflow


def test_arith_coerce_scalar(data, all_arithmetic_operators):
    op = tm.get_op_from_name(all_arithmetic_operators)
    s = pd.Series(data)
    other = 0.01

    result = op(s, other)
    expected = op(s.astype(float), other)
    # rfloordiv results in nan instead of inf
    if all_arithmetic_operators == "__rfloordiv__":
        expected[(expected == np.inf) | (expected == -np.inf)] = np.nan

    tm.assert_series_equal(result, expected)


@pytest.mark.parametrize("other", [1.0, np.array(1.0)])
def test_arithmetic_conversion(all_arithmetic_operators, other):
    # if we have a float operand we should have a float result
    # if that is equal to an integer
    op = tm.get_op_from_name(all_arithmetic_operators)

    s = pd.Series([1, 2, 3], dtype="Int64")
    result = op(s, other)
    assert result.dtype is np.dtype("float")


def test_cross_type_arithmetic():

    df = pd.DataFrame(
        {
            "A": pd.Series([1, 2, np.nan], dtype="Int64"),
            "B": pd.Series([1, np.nan, 3], dtype="UInt8"),
            "C": [1, 2, 3],
        }
    )

    result = df.A + df.C
    expected = pd.Series([2, 4, np.nan], dtype="Int64")
    tm.assert_series_equal(result, expected)

    result = (df.A + df.C) * 3 == 12
    expected = pd.Series([False, True, None], dtype="boolean")
    tm.assert_series_equal(result, expected)

    result = df.A + df.B
    expected = pd.Series([2, np.nan, np.nan], dtype="Int64")
    tm.assert_series_equal(result, expected)


@pytest.mark.parametrize("op", ["mean"])
def test_reduce_to_float(op):
    # some reduce ops always return float, even if the result
    # is a rounded number
    df = pd.DataFrame(
        {
            "A": ["a", "b", "b"],
            "B": [1, None, 3],
            "C": integer_array([1, None, 3], dtype="Int64"),
        }
    )

    # op
    result = getattr(df.C, op)()
    assert isinstance(result, float)

    # groupby
    result = getattr(df.groupby("A"), op)()

    expected = pd.DataFrame(
        {"B": np.array([1.0, 3.0]), "C": integer_array([1, 3], dtype="Int64")},
        index=pd.Index(["a", "b"], name="A"),
    )
    tm.assert_frame_equal(result, expected)
