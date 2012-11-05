import nose
import unittest

import numpy as np

from pandas import Series, date_range
import pandas.util.testing as tm

from datetime import datetime, date

from pandas.tseries.tools import normalize_date
from pandas.tseries.util import pivot_annual, isleapyear
from pandas.tseries import pivot


class TestPivotAnnualHourly(unittest.TestCase):
    """
    New pandas of scikits.timeseries pivot_annual for hourly with a new shape
    """
    def test_hourly(self):
        rng_hourly = date_range('1/1/1994', periods=(18* 8760 + 4*24), freq='H')
        data_hourly = np.random.randint(100, high=350, size=rng_hourly.size)
        data_hourly = data_hourly.astype('float64')
        ts_hourly = Series(data_hourly, index=rng_hourly)
        
        annual = pivot.pivot_annual_h(ts_hourly, dt_index=True)
        
        ### general
        ##test first column: if first value and data are the same as first value of timeseries
        #date
        def get_mdh(DatetimeIndex, index):
            #(m, d, h)
            mdh_tuple = (DatetimeIndex.month[index], DatetimeIndex.day[index], 
                        DatetimeIndex.hour[index])
            return mdh_tuple
#        ts_hourly.index.month[1], ts_hourly.index.month[1], ts_hourly.index.month[1]
            
        assert get_mdh(ts_hourly.index, 1) == get_mdh(annual.index, 1)
        #are the last dates of ts identical with the dates last row in the last column?
        assert get_mdh(ts_hourly.index, -1) == get_mdh(annual.index, (annual.index.size -1))
        #first values of the ts identical with the first col?        
        assert ts_hourly[0] == annual.ix[0].values[0]
        #last values of the ts identical with the last col and last row of the df?        
        assert ts_hourly[-1] == annual.ix[-1].values[-1]     
        #### index
        ##test if index has the right length
        assert annual.index.size == 8784
        ##test last column: if first value and data are the same as first value of timeseries
        ### leap
        ##test leap offset
        #leap year: 1996 - are the values of the ts and the 
        ser96_leap = ts_hourly[(ts_hourly.index.year == 1996) &  
                          (ts_hourly.index.month == 2) &
                          (ts_hourly.index.day == 29)                          
                          ]
                          
        df96 = annual[1996]
        df96_leap = df96[(df96.index.month == 2) & (df96.index.day == 29)]
        np.testing.assert_equal(ser96_leap.values, df96_leap.values)
        #non-leap year: 1994 - are all values NaN for day 29.02?
        nan_arr = np.empty(24)
        nan_arr.fill(np.nan)                  
        df94 = annual[1994]
        df94_noleap = df94[(df94.index.month == 2) & (df94.index.day == 29)]
        np.testing.assert_equal(df94_noleap.values, nan_arr)
        ### extended functionaliy
        ext = pivot.extended_info(annual)        
        ## descriptive statistics
        #mean        
        np.testing.assert_equal(annual.mean(1).values, ext['mean'].values)
        np.testing.assert_equal(annual.sum(1).values, ext['sum'].values)
        np.testing.assert_equal(annual.min(1).values, ext['min'].values)
        np.testing.assert_equal(annual.max(1).values, ext['max'].values)
        np.testing.assert_equal(annual.std(1).values, ext['std'].values)
        
        ## additional time columns for easier filtering
        np.testing.assert_equal(ext['doy'].values, annual.index.dayofyear)
        np.testing.assert_equal(ext['day'].values, annual.index.day)
        #the hour is incremented by 1
        np.testing.assert_equal(ext['hour'].values, (annual.index.hour +1))
    

class TestPivotAnnual(unittest.TestCase):
    """
    New pandas of scikits.timeseries pivot_annual
    """
    def test_daily(self):
        rng = date_range('1/1/2000', '12/31/2004', freq='D')
        ts = Series(np.random.randn(len(rng)), index=rng)

        annual = pivot_annual(ts, 'D')

        doy = ts.index.dayofyear
        doy[(-isleapyear(ts.index.year)) & (doy >= 60)] += 1

        for i in range(1, 367):
            subset = ts[doy == i]
            subset.index = [x.year for x in subset.index]

            tm.assert_series_equal(annual[i].dropna(), subset)

        # check leap days
        leaps = ts[(ts.index.month == 2) & (ts.index.day == 29)]
        day = leaps.index.dayofyear[0]
        leaps.index = leaps.index.year
        tm.assert_series_equal(annual[day].dropna(), leaps)


    def test_weekly(self):
        pass

    def test_monthly(self):
        rng = date_range('1/1/2000', '12/31/2004', freq='M')
        ts = Series(np.random.randn(len(rng)), index=rng)

        annual = pivot_annual(ts, 'M')

        month = ts.index.month

        for i in range(1, 13):
            subset = ts[month == i]
            subset.index = [x.year for x in subset.index]
            tm.assert_series_equal(annual[i].dropna(), subset)

    def test_period_monthly(self):
        pass

    def test_period_daily(self):
        pass

    def test_period_weekly(self):
        pass


def test_normalize_date():
    value = date(2012, 9, 7)

    result = normalize_date(value)
    assert(result == datetime(2012, 9, 7))

    value = datetime(2012, 9, 7, 12)

    result = normalize_date(value)
    assert(result == datetime(2012, 9, 7))

if __name__ == '__main__':
    nose.runmodule(argv=[__file__,'-vvs','-x','--pdb', '--pdb-failure'],
                   exit=False)

