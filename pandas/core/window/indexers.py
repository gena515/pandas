"""Indexer objects for computing start/end window bounds for rolling operations"""
from typing import Optional, Tuple

import numpy as np

from pandas._libs.window.indexers import calculate_variable_window_bounds


class BaseIndexer:
    """Base class for window bounds calculations"""

    def __init__(
        self, index: Optional[np.ndarray] = None, **kwargs,
    ):
        """
        Parameters
        ----------
        **kwargs :
            keyword argument that will be available when get_window_bounds is called
        """
        self.index = index
        self.__dict__.update(kwargs)

    def get_window_bounds(
        self,
        num_values: int = 0,
        window_size: int = 0,
        min_periods: Optional[int] = None,
        center: Optional[bool] = None,
        closed: Optional[str] = None,
        win_type: Optional[str] = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Computes the bounds of a window.

        Parameters
        ----------
        num_values : int, default 0
            number of values that will be aggregated over
        window_size : int, default 0
            the number of rows in a window
        min_periods : int, default None
            min_periods passed from the top level rolling API
        center : bool, default None
            center passed from the top level rolling API
        closed : str, default None
            closed passed from the top level rolling API
        win_type : str, default None
            win_type passed from the top level rolling API

        Returns
        -------
        A tuple of ndarray[int64]s, indicating the boundaries of each
        window
        """
        raise NotImplementedError


class FixedWindowIndexer(BaseIndexer):
    """Creates window boundaries that are of fixed length."""

    def get_window_bounds(
        self,
        num_values: int = 0,
        window_size: int = 0,
        min_periods: Optional[int] = None,
        center: Optional[bool] = None,
        closed: Optional[str] = None,
        win_type: Optional[str] = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Computes the fixed bounds of a window.

        Parameters
        ----------
        num_values : int, default 0
            number of values that will be aggregated over
        window_size : int, default 0
            the number of rows in a window
        min_periods : int, default None
            min_periods passed from the top level rolling API
        center : bool, default None
            center passed from the top level rolling API
        closed : str, default None
            closed passed from the top level rolling API
        win_type : str, default None
            win_type passed from the top level rolling API

        Returns
        -------
        A tuple of ndarray[int64]s, indicating the boundaries of each
        window
        """
        start_s = np.zeros(window_size, dtype="int64")
        start_e = np.arange(window_size, num_values, dtype="int64") - window_size + 1
        start = np.concatenate([start_s, start_e])[:num_values]

        end_s = np.arange(window_size, dtype="int64") + 1
        end_e = start_e + window_size
        end = np.concatenate([end_s, end_e])[:num_values]
        return start, end


class VariableWindowIndexer(BaseIndexer):
    """Creates window boundaries that are of variable length, namely for time series."""

    def get_window_bounds(
        self,
        num_values: int = 0,
        window_size: int = 0,
        min_periods: Optional[int] = None,
        center: Optional[bool] = None,
        closed: Optional[str] = None,
        win_type: Optional[str] = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Computes the variable bounds of a window.

        Parameters
        ----------
        num_values : int, default 0
            number of values that will be aggregated over
        window_size : int, default 0
            the number of rows in a window
        min_periods : int, default None
            min_periods passed from the top level rolling API
        center : bool, default None
            center passed from the top level rolling API
        closed : str, default None
            closed passed from the top level rolling API
        win_type : str, default None
            win_type passed from the top level rolling API

        Returns
        -------
        A tuple of ndarray[int64]s, indicating the boundaries of each
        window
        """
        return calculate_variable_window_bounds(
            num_values, window_size, min_periods, center, closed, win_type, self.index
        )
