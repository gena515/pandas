import pytest

import numpy as np
from datetime import timedelta

import pandas as pd
import pandas.util.testing as tm
from pandas import (timedelta_range, date_range, Series, Timedelta,
                    TimedeltaIndex, Index, DataFrame,
                    Int64Index)
from pandas.util.testing import (assert_almost_equal, assert_series_equal,
                                 assert_index_equal)

from ..datetimelike import DatetimeLike

randn = np.random.randn


class TestTimedeltaIndex(DatetimeLike):
    _holder = TimedeltaIndex
    _multiprocess_can_split_ = True

    def setup_method(self, method):
        self.indices = dict(index=tm.makeTimedeltaIndex(10))
        self.setup_indices()

    def create_index(self):
        return pd.to_timedelta(range(5), unit='d') + pd.offsets.Hour(1)

    def test_numeric_compat(self):
        # Dummy method to override super's version; this test is now done
        # in test_arithmetic.py
        pass

    def test_shift(self):
        # test shift for TimedeltaIndex
        # err8083

        drange = self.create_index()
        result = drange.shift(1)
        expected = TimedeltaIndex(['1 days 01:00:00', '2 days 01:00:00',
                                   '3 days 01:00:00',
                                   '4 days 01:00:00', '5 days 01:00:00'],
                                  freq='D')
        tm.assert_index_equal(result, expected)

        result = drange.shift(3, freq='2D 1s')
        expected = TimedeltaIndex(['6 days 01:00:03', '7 days 01:00:03',
                                   '8 days 01:00:03', '9 days 01:00:03',
                                   '10 days 01:00:03'], freq='D')
        tm.assert_index_equal(result, expected)

    def test_pickle_compat_construction(self):
        pass

    def test_fillna_timedelta(self):
        # GH 11343
        idx = pd.TimedeltaIndex(['1 day', pd.NaT, '3 day'])

        exp = pd.TimedeltaIndex(['1 day', '2 day', '3 day'])
        tm.assert_index_equal(idx.fillna(pd.Timedelta('2 day')), exp)

        exp = pd.TimedeltaIndex(['1 day', '3 hour', '3 day'])
        idx.fillna(pd.Timedelta('3 hour'))

        exp = pd.Index(
            [pd.Timedelta('1 day'), 'x', pd.Timedelta('3 day')], dtype=object)
        tm.assert_index_equal(idx.fillna('x'), exp)

    def test_difference_freq(self):
        # GH14323: Difference of TimedeltaIndex should not preserve frequency

        index = timedelta_range("0 days", "5 days", freq="D")

        other = timedelta_range("1 days", "4 days", freq="D")
        expected = TimedeltaIndex(["0 days", "5 days"], freq=None)
        idx_diff = index.difference(other)
        tm.assert_index_equal(idx_diff, expected)
        tm.assert_attr_equal('freq', idx_diff, expected)

        other = timedelta_range("2 days", "5 days", freq="D")
        idx_diff = index.difference(other)
        expected = TimedeltaIndex(["0 days", "1 days"], freq=None)
        tm.assert_index_equal(idx_diff, expected)
        tm.assert_attr_equal('freq', idx_diff, expected)

    def test_isin(self):

        index = tm.makeTimedeltaIndex(4)
        result = index.isin(index)
        assert result.all()

        result = index.isin(list(index))
        assert result.all()

        assert_almost_equal(index.isin([index[2], 5]),
                            np.array([False, False, True, False]))

    def test_factorize(self):
        idx1 = TimedeltaIndex(['1 day', '1 day', '2 day', '2 day', '3 day',
                               '3 day'])

        exp_arr = np.array([0, 0, 1, 1, 2, 2], dtype=np.intp)
        exp_idx = TimedeltaIndex(['1 day', '2 day', '3 day'])

        arr, idx = idx1.factorize()
        tm.assert_numpy_array_equal(arr, exp_arr)
        tm.assert_index_equal(idx, exp_idx)

        arr, idx = idx1.factorize(sort=True)
        tm.assert_numpy_array_equal(arr, exp_arr)
        tm.assert_index_equal(idx, exp_idx)

        # freq must be preserved
        idx3 = timedelta_range('1 day', periods=4, freq='s')
        exp_arr = np.array([0, 1, 2, 3], dtype=np.intp)
        arr, idx = idx3.factorize()
        tm.assert_numpy_array_equal(arr, exp_arr)
        tm.assert_index_equal(idx, idx3)

    def test_join_self(self):

        index = timedelta_range('1 day', periods=10)
        kinds = 'outer', 'inner', 'left', 'right'
        for kind in kinds:
            joined = index.join(index, how=kind)
            tm.assert_index_equal(index, joined)

    def test_does_not_convert_mixed_integer(self):
        df = tm.makeCustomDataframe(10, 10,
                                    data_gen_f=lambda *args, **kwargs: randn(),
                                    r_idx_type='i', c_idx_type='td')
        str(df)

        cols = df.columns.join(df.index, how='outer')
        joined = cols.join(df.columns)
        assert cols.dtype == np.dtype('O')
        assert cols.dtype == joined.dtype
        tm.assert_index_equal(cols, joined)

    def test_sort_values(self):

        idx = TimedeltaIndex(['4d', '1d', '2d'])

        ordered = idx.sort_values()
        assert ordered.is_monotonic

        ordered = idx.sort_values(ascending=False)
        assert ordered[::-1].is_monotonic

        ordered, dexer = idx.sort_values(return_indexer=True)
        assert ordered.is_monotonic

        tm.assert_numpy_array_equal(dexer, np.array([1, 2, 0]),
                                    check_dtype=False)

        ordered, dexer = idx.sort_values(return_indexer=True, ascending=False)
        assert ordered[::-1].is_monotonic

        tm.assert_numpy_array_equal(dexer, np.array([0, 2, 1]),
                                    check_dtype=False)

    def test_get_duplicates(self):
        idx = TimedeltaIndex(['1 day', '2 day', '2 day', '3 day', '3day',
                              '4day'])

        result = idx.get_duplicates()
        ex = TimedeltaIndex(['2 day', '3day'])
        tm.assert_index_equal(result, ex)

    def test_argmin_argmax(self):
        idx = TimedeltaIndex(['1 day 00:00:05', '1 day 00:00:01',
                              '1 day 00:00:02'])
        assert idx.argmin() == 1
        assert idx.argmax() == 0

    def test_misc_coverage(self):

        rng = timedelta_range('1 day', periods=5)
        result = rng.groupby(rng.days)
        assert isinstance(list(result.values())[0][0], Timedelta)

        idx = TimedeltaIndex(['3d', '1d', '2d'])
        assert not idx.equals(list(idx))

        non_td = Index(list('abc'))
        assert not idx.equals(list(non_td))

    def test_map(self):

        rng = timedelta_range('1 day', periods=10)

        f = lambda x: x.days
        result = rng.map(f)
        exp = Int64Index([f(x) for x in rng])
        tm.assert_index_equal(result, exp)

    def test_comparisons_nat(self):

        tdidx1 = pd.TimedeltaIndex(['1 day', pd.NaT, '1 day 00:00:01', pd.NaT,
                                    '1 day 00:00:01', '5 day 00:00:03'])
        tdidx2 = pd.TimedeltaIndex(['2 day', '2 day', pd.NaT, pd.NaT,
                                    '1 day 00:00:02', '5 days 00:00:03'])
        tdarr = np.array([np.timedelta64(2, 'D'),
                          np.timedelta64(2, 'D'), np.timedelta64('nat'),
                          np.timedelta64('nat'),
                          np.timedelta64(1, 'D') + np.timedelta64(2, 's'),
                          np.timedelta64(5, 'D') + np.timedelta64(3, 's')])

        cases = [(tdidx1, tdidx2), (tdidx1, tdarr)]

        # Check pd.NaT is handles as the same as np.nan
        for idx1, idx2 in cases:

            result = idx1 < idx2
            expected = np.array([True, False, False, False, True, False])
            tm.assert_numpy_array_equal(result, expected)

            result = idx2 > idx1
            expected = np.array([True, False, False, False, True, False])
            tm.assert_numpy_array_equal(result, expected)

            result = idx1 <= idx2
            expected = np.array([True, False, False, False, True, True])
            tm.assert_numpy_array_equal(result, expected)

            result = idx2 >= idx1
            expected = np.array([True, False, False, False, True, True])
            tm.assert_numpy_array_equal(result, expected)

            result = idx1 == idx2
            expected = np.array([False, False, False, False, False, True])
            tm.assert_numpy_array_equal(result, expected)

            result = idx1 != idx2
            expected = np.array([True, True, True, True, True, False])
            tm.assert_numpy_array_equal(result, expected)

    def test_comparisons_coverage(self):
        rng = timedelta_range('1 days', periods=10)

        result = rng < rng[3]
        exp = np.array([True, True, True] + [False] * 7)
        tm.assert_numpy_array_equal(result, exp)

        # raise TypeError for now
        pytest.raises(TypeError, rng.__lt__, rng[3].value)

        result = rng == list(rng)
        exp = rng == rng
        tm.assert_numpy_array_equal(result, exp)

    def test_total_seconds(self):
        # GH 10939
        # test index
        rng = timedelta_range('1 days, 10:11:12.100123456', periods=2,
                              freq='s')
        expt = [1 * 86400 + 10 * 3600 + 11 * 60 + 12 + 100123456. / 1e9,
                1 * 86400 + 10 * 3600 + 11 * 60 + 13 + 100123456. / 1e9]
        tm.assert_almost_equal(rng.total_seconds(), Index(expt))

        # test Series
        s = Series(rng)
        s_expt = Series(expt, index=[0, 1])
        tm.assert_series_equal(s.dt.total_seconds(), s_expt)

        # with nat
        s[1] = np.nan
        s_expt = Series([1 * 86400 + 10 * 3600 + 11 * 60 +
                         12 + 100123456. / 1e9, np.nan], index=[0, 1])
        tm.assert_series_equal(s.dt.total_seconds(), s_expt)

        # with both nat
        s = Series([np.nan, np.nan], dtype='timedelta64[ns]')
        tm.assert_series_equal(s.dt.total_seconds(),
                               Series([np.nan, np.nan], index=[0, 1]))

    def test_pass_TimedeltaIndex_to_index(self):

        rng = timedelta_range('1 days', '10 days')
        idx = Index(rng, dtype=object)

        expected = Index(rng.to_pytimedelta(), dtype=object)

        tm.assert_numpy_array_equal(idx.values, expected.values)

    def test_pickle(self):

        rng = timedelta_range('1 days', periods=10)
        rng_p = tm.round_trip_pickle(rng)
        tm.assert_index_equal(rng, rng_p)

    def test_hash_error(self):
        index = timedelta_range('1 days', periods=10)
        with tm.assert_raises_regex(TypeError, "unhashable type: %r" %
                                    type(index).__name__):
            hash(index)

    def test_append_join_nondatetimeindex(self):
        rng = timedelta_range('1 days', periods=10)
        idx = Index(['a', 'b', 'c', 'd'])

        result = rng.append(idx)
        assert isinstance(result[0], Timedelta)

        # it works
        rng.join(idx, how='outer')

    def test_append_numpy_bug_1681(self):

        td = timedelta_range('1 days', '10 days', freq='2D')
        a = DataFrame()
        c = DataFrame({'A': 'foo', 'B': td}, index=td)
        str(c)

        result = a.append(c)
        assert (result['B'] == td).all()

    def test_fields(self):
        rng = timedelta_range('1 days, 10:11:12.100123456', periods=2,
                              freq='s')
        tm.assert_index_equal(rng.days, Index([1, 1], dtype='int64'))
        tm.assert_index_equal(
            rng.seconds,
            Index([10 * 3600 + 11 * 60 + 12, 10 * 3600 + 11 * 60 + 13],
                  dtype='int64'))
        tm.assert_index_equal(
            rng.microseconds,
            Index([100 * 1000 + 123, 100 * 1000 + 123], dtype='int64'))
        tm.assert_index_equal(rng.nanoseconds,
                              Index([456, 456], dtype='int64'))

        pytest.raises(AttributeError, lambda: rng.hours)
        pytest.raises(AttributeError, lambda: rng.minutes)
        pytest.raises(AttributeError, lambda: rng.milliseconds)

        # with nat
        s = Series(rng)
        s[1] = np.nan

        tm.assert_series_equal(s.dt.days, Series([1, np.nan], index=[0, 1]))
        tm.assert_series_equal(s.dt.seconds, Series(
            [10 * 3600 + 11 * 60 + 12, np.nan], index=[0, 1]))

        # preserve name (GH15589)
        rng.name = 'name'
        assert rng.days.name == 'name'

    def test_freq_conversion(self):

        # doc example

        # series
        td = Series(date_range('20130101', periods=4)) - \
            Series(date_range('20121201', periods=4))
        td[2] += timedelta(minutes=5, seconds=3)
        td[3] = np.nan

        result = td / np.timedelta64(1, 'D')
        expected = Series([31, 31, (31 * 86400 + 5 * 60 + 3) / 86400.0, np.nan
                           ])
        assert_series_equal(result, expected)

        result = td.astype('timedelta64[D]')
        expected = Series([31, 31, 31, np.nan])
        assert_series_equal(result, expected)

        result = td / np.timedelta64(1, 's')
        expected = Series([31 * 86400, 31 * 86400, 31 * 86400 + 5 * 60 + 3,
                           np.nan])
        assert_series_equal(result, expected)

        result = td.astype('timedelta64[s]')
        assert_series_equal(result, expected)

        # tdi
        td = TimedeltaIndex(td)

        result = td / np.timedelta64(1, 'D')
        expected = Index([31, 31, (31 * 86400 + 5 * 60 + 3) / 86400.0, np.nan])
        assert_index_equal(result, expected)

        result = td.astype('timedelta64[D]')
        expected = Index([31, 31, 31, np.nan])
        assert_index_equal(result, expected)

        result = td / np.timedelta64(1, 's')
        expected = Index([31 * 86400, 31 * 86400, 31 * 86400 + 5 * 60 + 3,
                          np.nan])
        assert_index_equal(result, expected)

        result = td.astype('timedelta64[s]')
        assert_index_equal(result, expected)


class TestTimeSeries(object):
    _multiprocess_can_split_ = True

    def test_series_box_timedelta(self):
        rng = timedelta_range('1 day 1 s', periods=5, freq='h')
        s = Series(rng)
        assert isinstance(s[1], Timedelta)
        assert isinstance(s.iat[2], Timedelta)


class TestTimedeltaIndexVectorizedTimedelta(object):

    def test_nat_converters(self):

        def testit(unit, transform):
            # array
            result = pd.to_timedelta(np.arange(5), unit=unit)
            expected = TimedeltaIndex([np.timedelta64(i, transform(unit))
                                       for i in np.arange(5).tolist()])
            tm.assert_index_equal(result, expected)

            # scalar
            result = pd.to_timedelta(2, unit=unit)
            expected = Timedelta(np.timedelta64(2, transform(unit)).astype(
                'timedelta64[ns]'))
            assert result == expected

        # validate all units
        # GH 6855
        for unit in ['Y', 'M', 'W', 'D', 'y', 'w', 'd']:
            testit(unit, lambda x: x.upper())
        for unit in ['days', 'day', 'Day', 'Days']:
            testit(unit, lambda x: 'D')
        for unit in ['h', 'm', 's', 'ms', 'us', 'ns', 'H', 'S', 'MS', 'US',
                     'NS']:
            testit(unit, lambda x: x.lower())

        # offsets

        # m
        testit('T', lambda x: 'm')

        # ms
        testit('L', lambda x: 'ms')

    def test_timedelta_hash_equality(self):
        # GH 11129
        tds = timedelta_range('1 second', periods=20)
        assert all(hash(td) == hash(td.to_pytimedelta()) for td in tds)
