import cython

from cpython.datetime cimport (
    date,
    datetime,
    time,
    tzinfo,
)

import numpy as np

cimport numpy as cnp
from numpy cimport (
    int64_t,
    intp_t,
    ndarray,
)

cnp.import_array()

from .conversion cimport normalize_i8_stamp

from .dtypes import Resolution
from .ccalendar cimport DAY_NANOS
from .nattype cimport (
    NPY_NAT,
    c_NaT as NaT,
)
from .np_datetime cimport (
    dt64_to_dtstruct,
    npy_datetimestruct,
)
from .offsets cimport BaseOffset
from .period cimport get_period_ordinal
from .timestamps cimport create_timestamp_from_ts
from .timezones cimport (
    get_dst_info,
    is_tzlocal,
    is_utc,
)
from .tzconversion cimport (
    bisect_right_i8,
    localize_tzinfo_api,
)


cdef const int64_t[::1] _deltas_placeholder = np.array([], dtype=np.int64)


@cython.freelist(16)
@cython.final
cdef class Localizer:
    cdef readonly:
        tzinfo tz
        bint use_utc, use_fixed, use_tzlocal, use_dst, use_pytz
        ndarray trans
        Py_ssize_t ntrans
        const int64_t[::1] deltas
        int64_t delta

    @cython.initializedcheck(False)
    @cython.boundscheck(False)
    def __cinit__(self, tzinfo tz):
        self.tz = tz
        self.use_utc = self.use_tzlocal = self.use_fixed = False
        self.use_dst = self.use_pytz = False
        self.ntrans = -1  # placeholder
        self.delta = -1  # placeholder
        self.deltas = _deltas_placeholder

        if is_utc(tz) or tz is None:
            self.use_utc = True

        elif is_tzlocal(tz):
            self.use_tzlocal = True

        else:
            trans, deltas, typ = get_dst_info(tz)
            self.trans = trans
            self.ntrans = trans.shape[0]
            self.deltas = deltas

            if typ != "pytz" and typ != "dateutil":
                # static/fixed; in this case we know that len(delta) == 1
                self.use_fixed = True
                self.delta = deltas[0]
            else:
                self.use_dst = True
                if typ == "pytz":
                    self.use_pytz = True


# -------------------------------------------------------------------------


@cython.wraparound(False)
@cython.boundscheck(False)
def ints_to_pydatetime(
    const int64_t[:] stamps,
    tzinfo tz=None,
    BaseOffset freq=None,
    bint fold=False,
    str box="datetime"
) -> np.ndarray:
    """
    Convert an i8 repr to an ndarray of datetimes, date, time or Timestamp.

    Parameters
    ----------
    stamps : array of i8
    tz : str, optional
         convert to this timezone
    freq : BaseOffset, optional
         freq to convert
    fold : bint, default is 0
        Due to daylight saving time, one wall clock time can occur twice
        when shifting from summer to winter time; fold describes whether the
        datetime-like corresponds  to the first (0) or the second time (1)
        the wall clock hits the ambiguous time

        .. versionadded:: 1.1.0
    box : {'datetime', 'timestamp', 'date', 'time'}, default 'datetime'
        * If datetime, convert to datetime.datetime
        * If date, convert to datetime.date
        * If time, convert to datetime.time
        * If Timestamp, convert to pandas.Timestamp

    Returns
    -------
    ndarray[object] of type specified by box
    """
    cdef:
        Localizer info = Localizer(tz)
        int64_t utc_val, local_val
        Py_ssize_t pos, i, n = stamps.shape[0]
        int64_t* tdata = NULL

        npy_datetimestruct dts
        tzinfo new_tz
        ndarray[object] result = np.empty(n, dtype=object)
        bint use_date = False, use_time = False, use_ts = False, use_pydt = False

    if box == "date":
        assert (tz is None), "tz should be None when converting to date"
        use_date = True
    elif box == "timestamp":
        use_ts = True
    elif box == "time":
        use_time = True
    elif box == "datetime":
        use_pydt = True
    else:
        raise ValueError(
            "box must be one of 'datetime', 'date', 'time' or 'timestamp'"
        )

    if info.use_dst:
        tdata = <int64_t*>cnp.PyArray_DATA(info.trans)

    for i in range(n):
        utc_val = stamps[i]
        new_tz = tz

        if utc_val == NPY_NAT:
            result[i] = <object>NaT
            continue

        if info.use_utc:
            local_val = utc_val
        elif info.use_tzlocal:
            local_val = utc_val + localize_tzinfo_api(utc_val, tz)
        elif info.use_fixed:
            local_val = utc_val + info.delta
        else:
            pos = bisect_right_i8(tdata, utc_val, info.ntrans) - 1
            local_val = utc_val + info.deltas[pos]

            if info.use_pytz:
                # find right representation of dst etc in pytz timezone
                new_tz = tz._tzinfos[tz._transition_info[pos]]

        dt64_to_dtstruct(local_val, &dts)

        if use_ts:
            result[i] = create_timestamp_from_ts(utc_val, dts, new_tz, freq, fold)
        elif use_pydt:
            result[i] = datetime(
                dts.year, dts.month, dts.day, dts.hour, dts.min, dts.sec, dts.us,
                new_tz, fold=fold,
            )
        elif use_date:
            result[i] = date(dts.year, dts.month, dts.day)
        else:
            result[i] = time(dts.hour, dts.min, dts.sec, dts.us, new_tz, fold=fold)

    return result


# -------------------------------------------------------------------------

cdef:
    int RESO_US = Resolution.RESO_US.value
    int RESO_MS = Resolution.RESO_MS.value
    int RESO_SEC = Resolution.RESO_SEC.value
    int RESO_MIN = Resolution.RESO_MIN.value
    int RESO_HR = Resolution.RESO_HR.value
    int RESO_DAY = Resolution.RESO_DAY.value


cdef inline int _reso_stamp(npy_datetimestruct *dts):
    if dts.us != 0:
        if dts.us % 1000 == 0:
            return RESO_MS
        return RESO_US
    elif dts.sec != 0:
        return RESO_SEC
    elif dts.min != 0:
        return RESO_MIN
    elif dts.hour != 0:
        return RESO_HR
    return RESO_DAY


@cython.wraparound(False)
@cython.boundscheck(False)
def get_resolution(const int64_t[:] stamps, tzinfo tz=None) -> Resolution:
    cdef:
        Localizer info = Localizer(tz)
        int64_t utc_val, local_val
        Py_ssize_t pos, i, n = stamps.shape[0]
        int64_t* tdata = NULL

        npy_datetimestruct dts
        int reso = RESO_DAY, curr_reso

    if info.use_dst:
        tdata = <int64_t*>cnp.PyArray_DATA(info.trans)

    for i in range(n):
        utc_val = stamps[i]
        if utc_val == NPY_NAT:
            continue

        if info.use_utc:
            local_val = utc_val
        elif info.use_tzlocal:
            local_val = utc_val + localize_tzinfo_api(utc_val, tz)
        elif info.use_fixed:
            local_val = utc_val + info.delta
        else:
            pos = bisect_right_i8(tdata, utc_val, info.ntrans) - 1
            local_val = utc_val + info.deltas[pos]

        dt64_to_dtstruct(local_val, &dts)
        curr_reso = _reso_stamp(&dts)
        if curr_reso < reso:
            reso = curr_reso

    return Resolution(reso)


# -------------------------------------------------------------------------

'''
When using info.use_utc checks inside the loop...
+     2.40±0.06ms       3.96±0.2ms     1.65  tslibs.normalize.Normalize.time_normalize_i8_timestamps(1000000, datetime.timezone(datetime.timedelta(seconds=3600)))
+        30.6±2μs         48.3±1μs     1.58  tslibs.normalize.Normalize.time_normalize_i8_timestamps(10000, datetime.timezone(datetime.timedelta(seconds=3600)))
+     3.56±0.08ms       5.24±0.4ms     1.47  tslibs.normalize.Normalize.time_normalize_i8_timestamps(1000000, tzfile('/usr/share/zoneinfo/Asia/Tokyo'))
+        39.5±2μs         57.5±3μs     1.46  tslibs.normalize.Normalize.time_normalize_i8_timestamps(10000, tzfile('/usr/share/zoneinfo/Asia/Tokyo'))

With info.use_utc checked just once...
+        30.3±2μs       38.7±0.8μs     1.27  tslibs.normalize.Normalize.time_normalize_i8_timestamps(10000, datetime.timezone(datetime.timedelta(seconds=3600)))
+        447±10ns         552±30ns     1.24  tslibs.normalize.Normalize.time_is_date_array_normalized(1, datetime.timezone.utc)
+      3.63±0.1ms       4.46±0.2ms     1.23  tslibs.normalize.Normalize.time_normalize_i8_timestamps(1000000, tzfile('/usr/share/zoneinfo/Asia/Tokyo'))
+     2.05±0.02μs       2.49±0.2μs     1.21  tslibs.normalize.Normalize.time_is_date_array_normalized(100, tzfile('/usr/share/zoneinfo/Asia/Tokyo'))
+      2.55±0.2ms      3.09±0.07ms     1.21  tslibs.normalize.Normalize.time_normalize_i8_timestamps(1000000, datetime.timezone(datetime.timedelta(seconds=3600)))
+        528±10ns         630±10ns     1.19  tslibs.normalize.Normalize.time_is_date_array_normalized(1, tzlocal())

With info.use_utc checked just once... (re-run)
+        29.7±1μs       37.7±0.7μs     1.27  tslibs.normalize.Normalize.time_normalize_i8_timestamps(10000, datetime.timezone(datetime.timedelta(seconds=3600)))
+         518±9ns         640±10ns     1.24  tslibs.normalize.Normalize.time_is_date_array_normalized(0, tzlocal())
+      40.1±0.8μs         46.7±1μs     1.17  tslibs.normalize.Normalize.time_normalize_i8_timestamps(10000, tzfile('/usr/share/zoneinfo/Asia/Tokyo'))
+        515±10ns         578±10ns     1.12  tslibs.normalize.Normalize.time_is_date_array_normalized(0, None)
+      9.15±0.2ms       10.1±0.4ms     1.11  tslibs.normalize.Normalize.time_is_date_array_normalized(1000000, tzfile('/usr/share/zoneinfo/Asia/Tokyo'))
-      8.27±0.3ms       7.11±0.2ms     0.86  tslibs.normalize.Normalize.time_is_date_array_normalized(1000000, datetime.timezone.utc)
-        90.2±7μs         70.4±2μs     0.78  tslibs.normalize.Normalize.time_is_date_array_normalized(10000, None)

'''

@cython.wraparound(False)
@cython.boundscheck(False)
cpdef ndarray[int64_t] normalize_i8_timestamps(const int64_t[:] stamps, tzinfo tz):
    """
    Normalize each of the (nanosecond) timezone aware timestamps in the given
    array by rounding down to the beginning of the day (i.e. midnight).
    This is midnight for timezone, `tz`.

    Parameters
    ----------
    stamps : int64 ndarray
    tz : tzinfo or None

    Returns
    -------
    result : int64 ndarray of converted of normalized nanosecond timestamps
    """
    cdef:
        Localizer info = Localizer(tz)
        int64_t utc_val, local_val, delta=info.delta
        Py_ssize_t pos, i, n = stamps.shape[0]
        int64_t* tdata = NULL
        bint use_utc=info.use_utc,use_tzlocal=info.use_tzlocal,use_fixed=info.use_fixed

        int64_t[::1] result = np.empty(n, dtype=np.int64)

    if info.use_dst:
        tdata = <int64_t*>cnp.PyArray_DATA(info.trans)

    for i in range(n):
        utc_val = stamps[i]
        if utc_val == NPY_NAT:
            result[i] = NPY_NAT
            continue

        if use_utc:
            local_val = utc_val
        elif use_tzlocal:
            local_val = utc_val + localize_tzinfo_api(utc_val, tz)
        elif use_fixed:
            local_val = utc_val + delta
        else:
            pos = bisect_right_i8(tdata, utc_val, info.ntrans) - 1
            local_val = utc_val + info.deltas[pos]

        result[i] = normalize_i8_stamp(local_val)

    return result.base  # `.base` to access underlying ndarray


@cython.wraparound(False)
@cython.boundscheck(False)
def is_date_array_normalized(const int64_t[:] stamps, tzinfo tz=None) -> bool:
    """
    Check if all of the given (nanosecond) timestamps are normalized to
    midnight, i.e. hour == minute == second == 0.  If the optional timezone
    `tz` is not None, then this is midnight for this timezone.

    Parameters
    ----------
    stamps : int64 ndarray
    tz : tzinfo or None

    Returns
    -------
    is_normalized : bool True if all stamps are normalized
    """
    cdef:
        Localizer info = Localizer(tz)
        int64_t utc_val, local_val
        Py_ssize_t pos, i, n = stamps.shape[0]
        int64_t* tdata = NULL

    if info.use_dst:
        tdata = <int64_t*>cnp.PyArray_DATA(info.trans)

    for i in range(n):
        utc_val = stamps[i]
        if info.use_utc:
            local_val = utc_val
        elif info.use_tzlocal:
            local_val = utc_val + localize_tzinfo_api(utc_val, tz)
        elif info.use_fixed:
            local_val = utc_val + info.delta
        else:
            pos = bisect_right_i8(tdata, utc_val, info.ntrans) - 1
            local_val = utc_val + info.deltas[pos]

        if local_val % DAY_NANOS != 0:
            return False

    return True


# -------------------------------------------------------------------------


@cython.wraparound(False)
@cython.boundscheck(False)
def dt64arr_to_periodarr(const int64_t[:] stamps, int freq, tzinfo tz):
    cdef:
        Localizer info = Localizer(tz)
        int64_t utc_val, local_val
        Py_ssize_t pos, i, n = stamps.shape[0]
        int64_t* tdata = NULL

        npy_datetimestruct dts
        int64_t[::1] result = np.empty(n, dtype=np.int64)

    if info.use_dst:
        tdata = <int64_t*>cnp.PyArray_DATA(info.trans)

    for i in range(n):
        utc_val = stamps[i]
        if utc_val == NPY_NAT:
            result[i] = NPY_NAT
            continue

        if info.use_utc:
            local_val = utc_val
        elif info.use_tzlocal:
            local_val = utc_val + localize_tzinfo_api(utc_val, tz)
        elif info.use_fixed:
            local_val = utc_val + info.delta
        else:
            pos = bisect_right_i8(tdata, utc_val, info.ntrans) - 1
            local_val = utc_val + info.deltas[pos]

        dt64_to_dtstruct(local_val, &dts)
        result[i] = get_period_ordinal(&dts, freq)

    return result.base  # .base to get underlying ndarray
