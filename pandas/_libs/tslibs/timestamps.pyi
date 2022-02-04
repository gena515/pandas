from datetime import (
    date as _date,
    datetime,
    time as _time,
    timedelta,
    tzinfo as _tzinfo,
)
from time import struct_time
from typing import (
    ClassVar,
    TypeVar,
    overload,
)

import numpy as np

from pandas._libs.tslibs import (
    BaseOffset,
    NaTType,
    Period,
    Timedelta,
)

_DatetimeT = TypeVar("_DatetimeT", bound=datetime)

def integer_op_not_supported(obj: object) -> TypeError: ...

class Timestamp(datetime):
    min: ClassVar[Timestamp]
    max: ClassVar[Timestamp]

    resolution: ClassVar[Timedelta]
    value: int  # np.int64

    # error: "__new__" must return a class instance (got "Union[Timestamp, NaTType]")
    def __new__(  # type: ignore[misc]
        cls: type[_DatetimeT],
        ts_input: int
        | np.integer
        | float
        | str
        | _date
        | datetime
        | np.datetime64 = ...,
        freq: int | None | str | BaseOffset = ...,
        tz: str | _tzinfo | None | int = ...,
        unit: str | int | None = ...,
        year: int | None = ...,
        month: int | None = ...,
        day: int | None = ...,
        hour: int | None = ...,
        minute: int | None = ...,
        second: int | None = ...,
        microsecond: int | None = ...,
        nanosecond: int | None = ...,
        tzinfo: _tzinfo | None = ...,
        *,
        fold: int | None = ...,
    ) -> _DatetimeT | NaTType: ...
    def _set_freq(self, freq: BaseOffset | None) -> None: ...
    @property
    def year(self) -> int: ...
    @property
    def month(self) -> int: ...
    @property
    def day(self) -> int: ...
    @property
    def hour(self) -> int: ...
    @property
    def minute(self) -> int: ...
    @property
    def second(self) -> int: ...
    @property
    def microsecond(self) -> int: ...
    @property
    def tzinfo(self) -> _tzinfo | None: ...
    @property
    def tz(self) -> _tzinfo | None: ...
    @property
    def fold(self) -> int: ...
    @classmethod
    def fromtimestamp(
        cls: type[_DatetimeT], t: float, tz: _tzinfo | None = ...
    ) -> _DatetimeT: ...
    @classmethod
    def utcfromtimestamp(cls: type[_DatetimeT], t: float) -> _DatetimeT: ...
    @classmethod
    def today(cls: type[_DatetimeT], tz: _tzinfo | str | None = ...) -> _DatetimeT: ...
    @classmethod
    def fromordinal(
        cls: type[_DatetimeT],
        ordinal: int,
        freq: str | BaseOffset | None = ...,
        tz: _tzinfo | str | None = ...,
    ) -> _DatetimeT: ...
    @classmethod
    def now(cls: type[_DatetimeT], tz: _tzinfo | str | None = ...) -> _DatetimeT: ...
    @classmethod
    def utcnow(cls: type[_DatetimeT]) -> _DatetimeT: ...
    # error: Signature of "combine" incompatible with supertype "datetime"
    @classmethod
    def combine(cls, date: _date, time: _time) -> datetime: ...  # type: ignore[override]
    @classmethod
    def fromisoformat(cls: type[_DatetimeT], date_string: str) -> _DatetimeT: ...
    def strftime(self, format: str) -> str: ...
    def __format__(self, fmt: str) -> str: ...
    def toordinal(self) -> int: ...
    def timetuple(self) -> struct_time: ...
    def timestamp(self) -> float: ...
    def utctimetuple(self) -> struct_time: ...
    def date(self) -> _date: ...
    def time(self) -> _time: ...
    def timetz(self) -> _time: ...
    def replace(
        self,
        year: int = ...,
        month: int = ...,
        day: int = ...,
        hour: int = ...,
        minute: int = ...,
        second: int = ...,
        microsecond: int = ...,
        tzinfo: _tzinfo | None = ...,
        fold: int = ...,
    ) -> datetime: ...
    def astimezone(self: _DatetimeT, tz: _tzinfo | None = ...) -> _DatetimeT: ...
    def ctime(self) -> str: ...
    def isoformat(self, sep: str = ..., timespec: str = ...) -> str: ...
    @classmethod
    def strptime(cls, date_string: str, format: str) -> datetime: ...
    def utcoffset(self) -> timedelta | None: ...
    def tzname(self) -> str | None: ...
    def dst(self) -> timedelta | None: ...
    # error: Argument 1 of "__le__" is incompatible with supertype "date";
    # supertype defines the argument type as "date"
    def __le__(self, other: datetime) -> bool: ...  # type: ignore
    # error: Argument 1 of "__lt__" is incompatible with supertype "date";
    # supertype defines the argument type as "date"
    def __lt__(self, other: datetime) -> bool: ...  # type: ignore
    # error: Argument 1 of "__ge__" is incompatible with supertype "date";
    # supertype defines the argument type as "date"
    def __ge__(self, other: datetime) -> bool: ...  # type: ignore
    # error: Argument 1 of "__gt__" is incompatible with supertype "date";
    # supertype defines the argument type as "date"
    def __gt__(self, other: datetime) -> bool: ...  # type: ignore
    # error: Signature of "__add__" incompatible with supertype "date"/"datetime"
    @overload  # type: ignore[override]
    def __add__(self, other: np.ndarray) -> np.ndarray: ...
    @overload
    # TODO: other can also be Tick (but it cannot be resolved)
    def __add__(self: _DatetimeT, other: timedelta | np.timedelta64) -> _DatetimeT: ...
    def __radd__(self: _DatetimeT, other: timedelta) -> _DatetimeT: ...
    @overload  # type: ignore
    def __sub__(self, other: datetime) -> timedelta: ...
    @overload
    # TODO: other can also be Tick (but it cannot be resolved)
    def __sub__(self, other: timedelta | np.timedelta64) -> datetime: ...
    def __hash__(self) -> int: ...
    def weekday(self) -> int: ...
    def isoweekday(self) -> int: ...
    def isocalendar(self) -> tuple[int, int, int]: ...
    @property
    def is_leap_year(self) -> bool: ...
    @property
    def is_month_start(self) -> bool: ...
    @property
    def is_quarter_start(self) -> bool: ...
    @property
    def is_year_start(self) -> bool: ...
    @property
    def is_month_end(self) -> bool: ...
    @property
    def is_quarter_end(self) -> bool: ...
    @property
    def is_year_end(self) -> bool: ...
    def to_pydatetime(self, warn: bool = ...) -> datetime: ...
    def to_datetime64(self) -> np.datetime64: ...
    def to_period(self, freq: BaseOffset | str | None = ...) -> Period: ...
    def to_julian_date(self) -> np.float64: ...
    @property
    def asm8(self) -> np.datetime64: ...
    def tz_convert(self: _DatetimeT, tz: _tzinfo | str | None) -> _DatetimeT: ...
    # TODO: could return NaT?
    def tz_localize(
        self: _DatetimeT,
        tz: _tzinfo | str | None,
        ambiguous: str = ...,
        nonexistent: str = ...,
    ) -> _DatetimeT: ...
    def normalize(self: _DatetimeT) -> _DatetimeT: ...
    # TODO: round/floor/ceil could return NaT?
    def round(
        self: _DatetimeT, freq: str, ambiguous: bool | str = ..., nonexistent: str = ...
    ) -> _DatetimeT: ...
    def floor(
        self: _DatetimeT, freq: str, ambiguous: bool | str = ..., nonexistent: str = ...
    ) -> _DatetimeT: ...
    def ceil(
        self: _DatetimeT, freq: str, ambiguous: bool | str = ..., nonexistent: str = ...
    ) -> _DatetimeT: ...
    def day_name(self, locale: str | None = ...) -> str: ...
    def month_name(self, locale: str | None = ...) -> str: ...
    @property
    def day_of_week(self) -> int: ...
    @property
    def day_of_month(self) -> int: ...
    @property
    def day_of_year(self) -> int: ...
    @property
    def quarter(self) -> int: ...
    @property
    def week(self) -> int: ...
    def to_numpy(
        self, dtype: np.dtype | None = ..., copy: bool = ...
    ) -> np.datetime64: ...
