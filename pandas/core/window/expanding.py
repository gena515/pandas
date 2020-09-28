from textwrap import dedent
from typing import Callable, Dict, Optional

import numpy as np

from pandas._typing import FrameOrSeries
from pandas.compat.numpy import function as nv
from pandas.util._decorators import Appender, Substitution, doc

import pandas.core.common as com
from pandas.core.indexes.api import MultiIndex
from pandas.core.window.common import WindowGroupByMixin, _doc_template, _shared_docs
from pandas.core.window.indexers import ExpandingIndexer, GroupbyIndexer
from pandas.core.window.rolling import RollingAndExpandingMixin


class Expanding(RollingAndExpandingMixin):
    """
    Provide expanding transformations.

    Parameters
    ----------
    min_periods : int, default 1
        Minimum number of observations in window required to have a value
        (otherwise result is NA).
    center : bool, default False
        Set the labels at the center of the window.
    axis : int or str, default 0

    Returns
    -------
    a Window sub-classed for the particular operation

    See Also
    --------
    rolling : Provides rolling window calculations.
    ewm : Provides exponential weighted functions.

    Notes
    -----
    By default, the result is set to the right edge of the window. This can be
    changed to the center of the window by setting ``center=True``.

    Examples
    --------
    >>> df = pd.DataFrame({"B": [0, 1, 2, np.nan, 4]})
    >>> df
         B
    0  0.0
    1  1.0
    2  2.0
    3  NaN
    4  4.0

    >>> df.expanding(2).sum()
         B
    0  NaN
    1  1.0
    2  3.0
    3  3.0
    4  7.0
    """

    _attributes = ["min_periods", "center", "axis"]

    def __init__(self, obj, min_periods=1, center=None, axis=0, **kwargs):
        super().__init__(obj=obj, min_periods=min_periods, center=center, axis=axis)

    @property
    def _constructor(self):
        return Expanding

    def _get_window(self, other=None, **kwargs):
        """
        Get the window length over which to perform some operation.

        Parameters
        ----------
        other : object, default None
            The other object that is involved in the operation.
            Such an object is involved for operations like covariance.

        Returns
        -------
        window : int
            The window length.
        """
        axis = self.obj._get_axis(self.axis)
        length = len(axis) + (other is not None) * len(axis)

        other = self.min_periods or -1
        return max(length, other)

    _agg_see_also_doc = dedent(
        """
    See Also
    --------
    pandas.DataFrame.aggregate : Similar DataFrame method.
    pandas.Series.aggregate : Similar Series method.
    """
    )

    _agg_examples_doc = dedent(
        """
    Examples
    --------
    >>> df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6], "C": [7, 8, 9]})
    >>> df
       A  B  C
    0  1  4  7
    1  2  5  8
    2  3  6  9

    >>> df.ewm(alpha=0.5).mean()
              A         B         C
    0  1.000000  4.000000  7.000000
    1  1.666667  4.666667  7.666667
    2  2.428571  5.428571  8.428571
    """
    )

    @doc(
        _shared_docs["aggregate"],
        see_also=_agg_see_also_doc,
        examples=_agg_examples_doc,
        klass="Series/Dataframe",
        axis="",
    )
    def aggregate(self, func, *args, **kwargs):
        return super().aggregate(func, *args, **kwargs)

    agg = aggregate

    @Substitution(name="expanding")
    @Appender(_shared_docs["count"])
    def count(self, **kwargs):
        return super().count(**kwargs)

    @Substitution(name="expanding")
    @Appender(_shared_docs["apply"])
    def apply(
        self,
        func,
        raw: bool = False,
        engine: Optional[str] = None,
        engine_kwargs: Optional[Dict[str, bool]] = None,
        args=None,
        kwargs=None,
    ):
        return super().apply(
            func,
            raw=raw,
            engine=engine,
            engine_kwargs=engine_kwargs,
            args=args,
            kwargs=kwargs,
        )

    @Substitution(name="expanding")
    @Appender(_shared_docs["sum"])
    def sum(self, *args, **kwargs):
        nv.validate_expanding_func("sum", args, kwargs)
        return super().sum(*args, **kwargs)

    @Substitution(name="expanding", func_name="max")
    @Appender(_doc_template)
    @Appender(_shared_docs["max"])
    def max(self, *args, **kwargs):
        nv.validate_expanding_func("max", args, kwargs)
        return super().max(*args, **kwargs)

    @Substitution(name="expanding")
    @Appender(_shared_docs["min"])
    def min(self, *args, **kwargs):
        nv.validate_expanding_func("min", args, kwargs)
        return super().min(*args, **kwargs)

    @Substitution(name="expanding")
    @Appender(_shared_docs["mean"])
    def mean(self, *args, **kwargs):
        nv.validate_expanding_func("mean", args, kwargs)
        return super().mean(*args, **kwargs)

    @Substitution(name="expanding")
    @Appender(_shared_docs["median"])
    def median(self, **kwargs):
        return super().median(**kwargs)

    @Substitution(name="expanding", versionadded="")
    @Appender(_shared_docs["std"])
    def std(self, ddof=1, *args, **kwargs):
        nv.validate_expanding_func("std", args, kwargs)
        return super().std(ddof=ddof, **kwargs)

    @Substitution(name="expanding", versionadded="")
    @Appender(_shared_docs["var"])
    def var(self, ddof=1, *args, **kwargs):
        nv.validate_expanding_func("var", args, kwargs)
        return super().var(ddof=ddof, **kwargs)

    @Substitution(name="expanding", func_name="skew")
    @Appender(_doc_template)
    @Appender(_shared_docs["skew"])
    def skew(self, **kwargs):
        return super().skew(**kwargs)

    _agg_doc = dedent(
        """
    Examples
    --------

    The example below will show an expanding calculation with a window size of
    four matching the equivalent function call using `scipy.stats`.

    >>> arr = [1, 2, 3, 4, 999]
    >>> import scipy.stats
    >>> print(f"{scipy.stats.kurtosis(arr[:-1], bias=False):.6f}")
    -1.200000
    >>> print(f"{scipy.stats.kurtosis(arr, bias=False):.6f}")
    4.999874
    >>> s = pd.Series(arr)
    >>> s.expanding(4).kurt()
    0         NaN
    1         NaN
    2         NaN
    3   -1.200000
    4    4.999874
    dtype: float64
    """
    )

    @Appender(_agg_doc)
    @Substitution(name="expanding")
    @Appender(_shared_docs["kurt"])
    def kurt(self, **kwargs):
        return super().kurt(**kwargs)

    @Substitution(name="expanding")
    @Appender(_shared_docs["quantile"])
    def quantile(self, quantile, interpolation="linear", **kwargs):
        return super().quantile(
            quantile=quantile, interpolation=interpolation, **kwargs
        )

    @Substitution(name="expanding", func_name="cov")
    @Appender(_doc_template)
    @Appender(_shared_docs["cov"])
    def cov(self, other=None, pairwise=None, ddof=1, **kwargs):
        return super().cov(other=other, pairwise=pairwise, ddof=ddof, **kwargs)

    @Substitution(name="expanding")
    @Appender(_shared_docs["corr"])
    def corr(self, other=None, pairwise=None, **kwargs):
        return super().corr(other=other, pairwise=pairwise, **kwargs)


class ExpandingGroupby(WindowGroupByMixin, Expanding):
    """
    Provide a expanding groupby implementation.
    """

    @property
    def _constructor(self):
        return Expanding

    def _apply(
        self,
        func: Callable,
        center: bool,
        require_min_periods: int = 0,
        floor: int = 1,
        is_weighted: bool = False,
        name: Optional[str] = None,
        use_numba_cache: bool = False,
        **kwargs,
    ):
        result = Expanding._apply(
            self,
            func,
            center,
            require_min_periods,
            floor,
            is_weighted,
            name,
            use_numba_cache,
            **kwargs,
        )
        # Cannot use _wrap_outputs because we calculate the result all at once
        # Compose MultiIndex result from grouping levels then rolling level
        # Aggregate the MultiIndex data as tuples then the level names
        grouped_object_index = self.obj.index
        grouped_index_name = [*grouped_object_index.names]
        groupby_keys = [grouping.name for grouping in self._groupby.grouper._groupings]
        result_index_names = groupby_keys + grouped_index_name

        result_index_data = []
        for key, values in self._groupby.grouper.indices.items():
            for value in values:
                data = [
                    *com.maybe_make_list(key),
                    *com.maybe_make_list(grouped_object_index[value]),
                ]
                result_index_data.append(tuple(data))

        result_index = MultiIndex.from_tuples(
            result_index_data, names=result_index_names
        )
        result.index = result_index
        return result

    def _create_data(self, obj: FrameOrSeries) -> FrameOrSeries:
        """
        Split data into blocks & return conformed data.
        """
        # Ensure the object we're rolling over is monotonically sorted relative
        # to the groups
        # GH 36197
        if not obj.empty:
            groupby_order = np.concatenate(
                list(self._groupby.grouper.indices.values())
            ).astype(np.int64)
            obj = obj.take(groupby_order)
        return super()._create_data(obj)

    def _get_window_indexer(self, window: int) -> GroupbyIndexer:
        """
        Return an indexer class that will compute the window start and end bounds

        Parameters
        ----------
        window : int
            window size for FixedWindowIndexer (unused)

        Returns
        -------
        GroupbyIndexer
        """
        window_indexer = GroupbyIndexer(
            groupby_indicies=self._groupby.indices,
            window_indexer=ExpandingIndexer,
        )
        return window_indexer

    def _get_cython_func_type(self, func: str) -> Callable:
        """
        Return the cython function type.

        RollingGroupby needs to always use "variable" algorithms since processing
        the data in group order may not be monotonic with the data which
        "fixed" algorithms assume
        """
        return self._get_roll_func(f"{func}_variable")
