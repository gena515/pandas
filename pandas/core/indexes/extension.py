"""
Shared methods for Index subclasses backed by ExtensionArray.
"""
from typing import List

import numpy as np

from pandas.util._decorators import Appender, cache_readonly

from pandas.core.dtypes.common import is_dtype_equal
from pandas.core.dtypes.generic import ABCSeries

from pandas.core.arrays import ExtensionArray
from pandas.core.ops import get_op_result_name

from .base import Index, _index_shared_docs


def inherit_from_data(name: str, delegate, cache: bool = False):
    """
    Make an alias for a method of the underlying ExtensionArray.

    Parameters
    ----------
    name : str
        Name of an attribute the class should inherit from its EA parent.
    delegate : class
    cache : bool, default False
        Whether to convert wrapped properties into cache_readonly

    Returns
    -------
    attribute, method, property, or cache_readonly
    """

    attr = getattr(delegate, name)

    if isinstance(attr, property):
        if cache:
            method = cache_readonly(attr.fget)

        else:

            def fget(self):
                return getattr(self._data, name)

            def fset(self, value):
                setattr(self._data, name, value)

            fget.__name__ = name
            fget.__doc__ = attr.__doc__

            method = property(fget, fset)

    elif not callable(attr):
        # just a normal attribute, no wrapping
        method = attr

    else:

        def method(self, *args, **kwargs):
            result = attr(self._data, *args, **kwargs)
            return result

        method.__name__ = name
        method.__doc__ = attr.__doc__
    return method


def inherit_names(names: List[str], delegate, cache: bool = False):
    """
    Class decorator to pin attributes from an ExtensionArray to a Index subclass.

    Parameters
    ----------
    names : List[str]
    delegate : class
    cache : bool, default False
    """

    def wrapper(cls):
        for name in names:
            meth = inherit_from_data(name, delegate, cache=cache)
            setattr(cls, name, meth)

        return cls

    return wrapper


def make_wrapped_comparison_op(opname):
    """
    Create a comparison method that dispatches to ``._data``.
    """

    def wrapper(self, other):
        if isinstance(other, ABCSeries):
            # the arrays defer to Series for comparison ops but the indexes
            #  don't, so we have to unwrap here.
            other = other._values

        other = _maybe_unwrap_index(other)

        op = getattr(self._data, opname)
        return op(other)

    wrapper.__name__ = opname
    return wrapper


def make_wrapped_arith_op(opname):
    def method(self, other):
        meth = getattr(self._data, opname)
        result = meth(_maybe_unwrap_index(other))
        return _wrap_arithmetic_op(self, other, result)

    method.__name__ = opname
    return method


def _wrap_arithmetic_op(self, other, result):
    if result is NotImplemented:
        return NotImplemented

    if isinstance(result, tuple):
        # divmod, rdivmod
        assert len(result) == 2
        return (
            _wrap_arithmetic_op(self, other, result[0]),
            _wrap_arithmetic_op(self, other, result[1]),
        )

    if not isinstance(result, Index):
        # Index.__new__ will choose appropriate subclass for dtype
        result = Index(result)

    res_name = get_op_result_name(self, other)
    result.name = res_name
    return result


def _maybe_unwrap_index(obj):
    """
    If operating against another Index object, we need to unwrap the underlying
    data before deferring to the DatetimeArray/TimedeltaArray/PeriodArray
    implementation, otherwise we will incorrectly return NotImplemented.

    Parameters
    ----------
    obj : object

    Returns
    -------
    unwrapped object
    """
    if isinstance(obj, Index):
        return obj._data
    return obj


class ExtensionIndex(Index):
    _data: ExtensionArray

    def __getitem__(self, key):
        result = self._data[key]
        if isinstance(result, type(self._data)):
            return type(self)(result, name=self.name)

        # Includes cases where we get a 2D ndarray back for MPL compat
        return result

    def __iter__(self):
        return self._data.__iter__()

    @property
    def _ndarray_values(self) -> np.ndarray:
        return self._data._ndarray_values

    @Appender(_index_shared_docs["astype"])
    def astype(self, dtype, copy=True):
        if is_dtype_equal(self.dtype, dtype) and copy is False:
            # Ensure that self.astype(self.dtype) is self
            return self

        new_values = self._data.astype(dtype, copy=copy)

        # pass copy=False because any copying will be done in the
        #  _data.astype call above
        return Index(new_values, dtype=new_values.dtype, name=self.name, copy=False)

    def dropna(self, how="any"):
        if how not in ("any", "all"):
            raise ValueError(f"invalid how option: {how}")

        if self.hasnans:
            return self._shallow_copy(self._data[~self._isnan])
        return self._shallow_copy()

    def _get_unique_index(self, dropna=False):
        if self.is_unique and not dropna:
            return self

        result = self._data.unique()
        if dropna and self.hasnans:
            result = result[~result.isna()]
        return self._shallow_copy(result)

    def unique(self, level=None):
        if level is not None:
            self._validate_index_level(level)

        result = self._data.unique()
        return self._shallow_copy(result)
