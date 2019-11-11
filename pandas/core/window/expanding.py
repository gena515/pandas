from textwrap import dedent

from pandas.compat.numpy import function as nv
from pandas.util._decorators import Appender, Substitution

from pandas.core.window.common import WindowGroupByMixin, _doc_template, _shared_docs
from pandas.core.window.rolling import _Rolling_and_Expanding


class Expanding(_Rolling_and_Expanding):
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

    >>> df = pd.DataFrame({'B': [0, 1, 2, np.nan, 4]})
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

    def __init__(self, obj, min_periods=1, center=False, axis=0, **kwargs):
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
    DataFrame.expanding.aggregate
    DataFrame.rolling.aggregate
    DataFrame.aggregate
    """
    )

    _agg_examples_doc = dedent(
        """
    Examples
    --------

    >>> df = pd.DataFrame(np.random.randn(10, 3), columns=['A', 'B', 'C'])
    >>> df
              A         B         C
    0 -2.385977 -0.102758  0.438822
    1 -1.004295  0.905829 -0.954544
    2  0.735167 -0.165272 -1.619346
    3 -0.702657 -1.340923 -0.706334
    4 -0.246845  0.211596 -0.901819
    5  2.463718  3.157577 -1.380906
    6 -1.142255  2.340594 -0.039875
    7  1.396598 -1.647453  1.677227
    8 -0.543425  1.761277 -0.220481
    9 -0.640505  0.289374 -1.550670

    >>> df.ewm(alpha=0.5).mean()
              A         B         C
    0 -2.385977 -0.102758  0.438822
    1 -1.464856  0.569633 -0.490089
    2 -0.207700  0.149687 -1.135379
    3 -0.471677 -0.645305 -0.906555
    4 -0.355635 -0.203033 -0.904111
    5  1.076417  1.503943 -1.146293
    6 -0.041654  1.925562 -0.588728
    7  0.680292  0.132049  0.548693
    8  0.067236  0.948257  0.163353
    9 -0.286980  0.618493 -0.694496
    """
    )

    @Substitution(
        see_also=_agg_see_also_doc,
        examples=_agg_examples_doc,
        versionadded="",
        klass="Series/Dataframe",
        axis="",
    )
    @Appender(_shared_docs["aggregate"])
    def aggregate(self, func, *args, **kwargs):
        return super().aggregate(func, *args, **kwargs)

    agg = aggregate

    @Substitution(name="expanding")
    @Appender(_shared_docs["count"])
    def count(self, **kwargs):
        return super().count(**kwargs)

    @Substitution(name="expanding")
    @Appender(_shared_docs["apply"])
    def apply(self, func, raw=None, args=(), kwargs={}):
        return super().apply(func, raw=raw, args=args, kwargs=kwargs)

    @Substitution(name="expanding")
    @Appender(_shared_docs["sum"])
    def sum(self, *args, **kwargs):
        nv.validate_expanding_func("sum", args, kwargs)
        return super().sum(*args, **kwargs)

    @Substitution(name="expanding")
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

    @Substitution(name="expanding")
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
    >>> fmt = "{0:.6f}"  # limit the printed precision to 6 digits
    >>> print(fmt.format(scipy.stats.kurtosis(arr[:-1], bias=False)))
    -1.200000
    >>> print(fmt.format(scipy.stats.kurtosis(arr, bias=False)))
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

    @Substitution(name="expanding")
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
