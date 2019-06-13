"""
Provide basic components for groupby. These defintiions
hold the whitelist of methods that are exposed on the
SeriesGroupBy and the DataFrameGroupBy objects.
"""
from typing import TYPE_CHECKING, FrozenSet, Iterator, Type, Union

from pandas.core.dtypes.common import is_list_like, is_scalar

if TYPE_CHECKING:
    from pandas import DataFrame, Series
    from .groupby import GroupBy


class GroupByMixin:
    """
    Provide the groupby facilities to the mixed object.
    """

    @staticmethod
    def _dispatch(name, *args, **kwargs):
        """
        Dispatch to apply.
        """

        def outer(self, *args, **kwargs):
            def f(x):
                x = self._shallow_copy(x, groupby=self._groupby)
                return getattr(x, name)(*args, **kwargs)
            return self._groupby.apply(f)
        outer.__name__ = name
        return outer

    def _gotitem(self, key, ndim, subset=None):
        """
        Sub-classes to define. Return a sliced object.

        Parameters
        ----------
        key : string / list of selections
        ndim : 1,2
            requested ndim of result
        subset : object, default None
            subset to act on
        """
        # create a new object to prevent aliasing
        if subset is None:
            subset = self.obj

        # we need to make a shallow copy of ourselves
        # with the same groupby
        kwargs = {attr: getattr(self, attr) for attr in self._attributes}

        # Try to select from a DataFrame, falling back to a Series
        try:
            groupby = self._groupby[key]
        except IndexError:
            groupby = self._groupby

        self = self.__class__(subset,
                              groupby=groupby,
                              parent=self,
                              **kwargs)
        self._reset_cache()
        if subset.ndim == 2:
            if is_scalar(key) and key in subset or is_list_like(key):
                self._selection = key
        return self


# special case to prevent duplicate plots when catching exceptions when
# forwarding methods from NDFrames
plotting_methods = frozenset(['plot', 'hist'])

common_apply_whitelist = frozenset([
    'quantile', 'fillna', 'mad', 'take',
    'idxmax', 'idxmin', 'tshift',
    'skew', 'corr', 'cov', 'diff'
]) | plotting_methods

series_apply_whitelist = ((common_apply_whitelist |
                           {'nlargest', 'nsmallest',
                            'is_monotonic_increasing',
                            'is_monotonic_decreasing'})
                          ) | frozenset(['dtype', 'unique'])

dataframe_apply_whitelist = ((common_apply_whitelist |
                              frozenset(['dtypes', 'corrwith'])))

cython_transforms = frozenset(['cumprod', 'cumsum', 'shift',
                               'cummin', 'cummax'])

cython_cast_blacklist = frozenset(['rank', 'count', 'size', 'idxmin',
                                   'idxmax'])


def whitelist_method_generator(base: 'Type[GroupBy]',
                               klass: 'Union[Type[DataFrame], Type[Series]]',
                               whitelist: FrozenSet[str],
                               ) -> Iterator[str]:
    """
    Yields all GroupBy member defs for DataFrame/Series names in whitelist.

    Parameters
    ----------
    base : Groupby class
        base class
    klass : DataFrame or Series class
        class where members are defined.
    whitelist : frozenset
        Set of names of klass methods to be constructed

    Returns
    -------
    The generator yields a sequence of strings, each suitable for exec'ing,
    that define implementations of the named methods for DataFrameGroupBy
    or SeriesGroupBy.

    Since we don't want to override methods explicitly defined in the
    base class, any such name is skipped.
    """
    property_wrapper_template = \
        """@property
def %(name)s(self) :
    \"""%(doc)s\"""
    return self.__getattr__('%(name)s')"""

    for name in whitelist:
        # don't override anything that was explicitly defined
        # in the base class
        if hasattr(base, name):
            continue
        # ugly, but we need the name string itself in the method.
        f = getattr(klass, name)
        doc = f.__doc__
        doc = doc if type(doc) == str else ''
        wrapper_template = property_wrapper_template
        params = {'name': name, 'doc': doc}
        yield wrapper_template % params
