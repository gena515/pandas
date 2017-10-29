""" generic datetimelike tests """

import pytest

import pandas as pd
from .common import Base
import pandas.util.testing as tm
from pandas import Timestamp, Timedelta, NaT

class DatetimeLike(Base):

    def test_shift_identity(self):

        idx = self.create_index()
        tm.assert_index_equal(idx, idx.shift(0))

    def test_str(self):

        # test the string repr
        idx = self.create_index()
        idx.name = 'foo'
        assert not "length=%s" % len(idx) in str(idx)
        assert "'foo'" in str(idx)
        assert idx.__class__.__name__ in str(idx)

        if hasattr(idx, 'tz'):
            if idx.tz is not None:
                assert idx.tz in str(idx)
        if hasattr(idx, 'freq'):
            assert "freq='%s'" % idx.freqstr in str(idx)

    def test_view(self, indices):
        super(DatetimeLike, self).test_view(indices)

        i = self.create_index()

        i_view = i.view('i8')
        result = self._holder(i)
        tm.assert_index_equal(result, i)

        i_view = i.view(self._holder)
        result = self._holder(i)
        tm.assert_index_equal(result, i_view)


class TestDatetimeLikeIndexArithmetic(object):
    # GH17991 checking for overflows and NaT masking on arithmetic ops

    # TODO: Fill out the matrix of allowed arithmetic operations:
    #   - __rsub__, __radd__
    #   - ops with scalars boxed in Index/Series/DataFrame
    #   - ops with scalars:
    #              NaT, Timestamp.min/max, Timedelta.min/max
    #              datetime, timedelta, date(?),
    #              relativedelta,
    #              np.datetime64, np.timedelta64,
    #              DateOffset,
    #              Period
    #   - timezone-aware variants
    #   - PeriodIndex
    #   - consistency with .map(...) ?

    def test_timedeltaindex_add_timestamp_nat_masking(self):
        tdinat = pd.to_timedelta(['24658 days 11:15:00', 'NaT'])

        # tsneg.value < 0, tspos.value > 0
        tsneg = Timestamp('1950-01-01')
        tspos = Timestamp('1980-01-01')

        res1 = tdinat + tsneg
        assert res1[1] is NaT
        res2 = tdinat + tspos
        assert res2[1] is NaT

    def test_timedeltaindex_sub_timestamp_nat_masking(self):
        tdinat = pd.to_timedelta(['24658 days 11:15:00', 'NaT'])

        # tsneg.value < 0, tspos.value > 0
        tsneg = Timestamp('1950-01-01')
        tspos = Timestamp('1980-01-01')

        res1 = tdinat - tsneg
        assert res1[1] is NaT
        res2 = tdinat - tspos
        assert res2[1] is NaT

    def test_timedeltaindex_add_timestamp_overflow(self):
        tdimax = pd.to_timedelta(['24658 days 11:15:00', Timedelta.max])
        tdimin = pd.to_timedelta(['24658 days 11:15:00', Timedelta.min])

        # tsneg.value < 0, tspos.value > 0
        tsneg = Timestamp('1950-01-01')
        tspos = Timestamp('1980-01-01')

        res1 = tdimax + tsneg
        res2 = tdimin + tspos

        with pytest.raises(OverflowError):
            tdimax + tspos

        with pytest.raises(OverflowError):
            tdimin + tsneg

    def test_timedeltaindex_add_timedelta_overflow(self):
        tdimax = pd.to_timedelta(['24658 days 11:15:00', Timedelta.max])
        tdimin = pd.to_timedelta(['24658 days 11:15:00', Timedelta.min])

        # tdpos.value > 0, tdneg.value < 0
        tdpos = Timedelta('1h')
        tdneg = Timedelta('-1h')

        with pytest.raises(OverflowError):
            res1 = tdimax + tdpos

        res2 = tdimax + tdneg

        res3 = tdimin + tdpos
        with pytest.raises(OverflowError):
            res4 = tdimin + tdneg

    def test_timedeltaindex_sub_timedelta_overflow(self):
        tdimax = pd.to_timedelta(['24658 days 11:15:00', Timedelta.max])
        tdimin = pd.to_timedelta(['24658 days 11:15:00', Timedelta.min])

        # tdpos.value > 0, tdneg.value < 0
        tdpos = Timedelta('1h')
        tdneg = Timedelta('-1h')

        res1 = tdimax - tdpos
        with pytest.raises(OverflowError):
            res2 = tdimax - tdneg
        with pytest.raises(OverflowError):
            res3 = tdimin - tdpos
        res4 = tdimin - tdneg

    def test_datetimeindex_add_nat_masking(self):
        # Checking for NaTs and checking that we don't get an OverflowError
        dtinat = pd.to_datetime(['now', 'NaT'])

        # tdpos.value > 0, tdneg.value < 0
        tdpos = Timedelta('1h')
        tdneg = Timedelta('-1h')

        res1 = dtinat + tdpos
        assert res1[1] is NaT
        res2 = dtinat + tdneg
        assert res2[1] is NaT

    def test_datetimeindex_sub_nat_masking(self):
        # Checking for NaTs and checking that we don't get an OverflowError
        dtinat = pd.to_datetime(['now', 'NaT'])

        # tdpos.value > 0, tdneg.value < 0
        tdpos = Timedelta('1h')
        tdneg = Timedelta('-1h')

        res1 = dtinat - tdpos
        assert res1[1] is NaT
        res2 = dtinat - tdneg
        assert res2[1] is NaT

    def test_datetimeindex_add_timedelta_overflow(self):
        dtimax = pd.to_datetime(['now', Timestamp.max])
        dtimin = pd.to_datetime(['now', Timestamp.min])

        # tdpos.value < 0, tdneg.value > 0
        tdpos = Timedelta('1h')
        tdneg = Timedelta('-1h')

        with pytest.raises(OverflowError):
            res1 = dtimax + tdpos

        res2 = dtimax + tdneg
        assert res2[1].value == Timestamp.max.value + tdneg.value

        res3 = dtimin + tdpos
        assert res3[1].value == Timestamp.min.value + tdpos.value

        with pytest.raises(OverflowError):
            res4 = dtimin + tdneg

    def test_datetimeindex_sub_timedelta_overflow(self):
        dtimax = pd.to_datetime(['now', Timestamp.max])
        dtimin = pd.to_datetime(['now', Timestamp.min])

        # tdpos.value < 0, tdneg.value > 0
        tdpos = Timedelta('1h')
        tdneg = Timedelta('-1h')

        res1 = dtimax - tdpos
        assert res1[1].value == Timestamp.max.value - tdpos.value

        with pytest.raises(OverflowError):
            res2 = dtimax - tdneg

        with pytest.raises(OverflowError):
            res3 = dtimin - tdpos

        res4 = dtimin - tdneg
        assert res4[1].value == Timestamp.min.value - tdneg.value

    def test_datetimeindex_sub_timestamp_overflow(self):
        dtimax = pd.to_datetime(['now', Timestamp.max])
        dtimin = pd.to_datetime(['now', Timestamp.min])

        # tsneg.value < 0, tspos.value > 0
        tsneg = Timestamp('1950-01-01')
        tspos = Timestamp('1980-01-01')

        with pytest.raises(OverflowError):
            res1 = dtimax - tsneg

        res2 = dtimax - tspos
        assert res2[1].value == Timestamp.max.value - tspos.value

        res3 = dtimin - tsneg
        assert res3[1].value == Timestamp.min.value - tsneg.value

        with pytest.raises(OverflowError):
            res4 = dtimin - tspos
