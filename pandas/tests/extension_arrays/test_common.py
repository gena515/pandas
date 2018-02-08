import numpy as np

import pandas.util.testing as tm
from pandas.core.arrays import ExtensionArray


class DummyArray(ExtensionArray):

    def __init__(self, data):
        self.data = data

    def __array__(self, dtype):
        return self.data


def test_astype():
    arr = DummyArray(np.array([1, 2, 3]))
    expected = np.array([1, 2, 3], dtype=object)

    result = arr.astype(object)
    tm.assert_numpy_array_equal(result, expected)

    result = arr.astype('object')
    tm.assert_numpy_array_equal(result, expected)


def test_astype_raises():
    arr = DummyArray(np.array([1, 2, 3]))

    xpr = ("DummyArray can only be coerced to 'object' dtype, not "
           "'<class 'int'>'")

    with tm.assert_raises_regex(ValueError, xpr):
        arr.astype(int)
