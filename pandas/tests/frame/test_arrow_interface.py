import ctypes

import pytest

from pandas._config import using_string_dtype

import pandas.util._test_decorators as td

import pandas as pd
import pandas._testing as tm

pa = pytest.importorskip("pyarrow")


@pytest.mark.xfail(using_string_dtype(), reason="TODO(infer_string)")
@td.skip_if_no("pyarrow", min_version="14.0")
def test_dataframe_arrow_interface():
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["a", "b", "c"]})

    capsule = df.__arrow_c_stream__()
    assert (
        ctypes.pythonapi.PyCapsule_IsValid(
            ctypes.py_object(capsule), b"arrow_array_stream"
        )
        == 1
    )

    table = pa.table(df)
    expected = pa.table({"a": [1, 2, 3], "b": ["a", "b", "c"]})
    assert table.equals(expected)

    schema = pa.schema([("a", pa.int8()), ("b", pa.string())])
    table = pa.table(df, schema=schema)
    expected = expected.cast(schema)
    assert table.equals(expected)


@pytest.mark.xfail(using_string_dtype(), reason="TODO(infer_string)")
@td.skip_if_no("pyarrow", min_version="15.0")
def test_dataframe_to_arrow():
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["a", "b", "c"]})

    table = pa.RecordBatchReader.from_stream(df).read_all()
    expected = pa.table({"a": [1, 2, 3], "b": ["a", "b", "c"]})
    assert table.equals(expected)

    schema = pa.schema([("a", pa.int8()), ("b", pa.string())])
    table = pa.RecordBatchReader.from_stream(df, schema=schema).read_all()
    expected = expected.cast(schema)
    assert table.equals(expected)


class ArrowArrayWrapper:
    def __init__(self, batch):
        self.array = batch

    def __arrow_c_array__(self, requested_schema=None):
        return self.array.__arrow_c_array__(requested_schema)


class ArrowStreamWrapper:
    def __init__(self, table):
        self.stream = table

    def __arrow_c_stream__(self, requested_schema=None):
        return self.stream.__arrow_c_stream__(requested_schema)


@td.skip_if_no("pyarrow", min_version="14.0")
def test_dataframe_from_arrow():
    # objects with __arrow_c_stream__
    table = pa.table({"a": [1, 2, 3], "b": ["a", "b", "c"]})

    result = pd.DataFrame.from_arrow(table)
    expected = pd.DataFrame({"a": [1, 2, 3], "b": ["a", "b", "c"]})
    tm.assert_frame_equal(result, expected)

    # not only pyarrow object are supported
    result = pd.DataFrame.from_arrow(ArrowStreamWrapper(table))
    tm.assert_frame_equal(result, expected)

    # objects with __arrow_c_array__
    batch = pa.record_batch([[1, 2, 3], ["a", "b", "c"]], names=["a", "b"])

    result = pd.DataFrame.from_arrow(table)
    tm.assert_frame_equal(result, expected)

    result = pd.DataFrame.from_arrow(ArrowArrayWrapper(batch))
    tm.assert_frame_equal(result, expected)
