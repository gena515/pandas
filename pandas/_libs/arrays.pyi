from typing import Sequence

import numpy as np

from pandas._typing import (
    ArrayLike,
    AxisInt,
    DtypeObj,
    PositionalIndexer,
    Self,
    Shape,
    type_t,
)

class NDArrayBacked:
    _dtype: DtypeObj
    _ndarray: np.ndarray
    def __init__(self, values: np.ndarray, dtype: DtypeObj) -> None: ...
    @classmethod
    def _simple_new(cls, values: np.ndarray, dtype: DtypeObj): ...
    def _from_backing_data(self, values: np.ndarray): ...
    def __setstate__(self, state): ...
    def __len__(self) -> int: ...
    @property
    def shape(self) -> Shape: ...
    @property
    def ndim(self) -> int: ...
    @property
    def size(self) -> int: ...
    @property
    def nbytes(self) -> int: ...
    def copy(self): ...
    def delete(self, loc, axis=...): ...
    def swapaxes(self, axis1, axis2): ...
    def repeat(self, repeats: int | Sequence[int], axis: int | None = ...): ...
    def reshape(self, *args, **kwargs): ...
    def ravel(self, order=...): ...
    @property
    def T(self): ...
    @classmethod
    def _concat_same_type(
        cls, to_concat: Sequence[Self], axis: AxisInt = ...
    ) -> Self: ...

class BitmaskArray:
    parent: Self
    def __init__(self, data: np.ndarray | Self) -> None: ...
    def __setitem__(self, key: PositionalIndexer, value: ArrayLike | bool) -> None: ...
    def __getitem__(self, key: PositionalIndexer) -> bool: ...
    def __invert__(self) -> Self: ...
    def __and__(self, other: np.ndarray | Self) -> np.ndarray: ...
    def __or__(self, other: np.ndarray | Self) -> np.ndarray: ...
    def __xor__(self, other: np.ndarray | Self) -> np.ndarray: ...
    def __getstate__(self) -> dict: ...
    def __setstate__(self, other: dict) -> None: ...
    def __iter__(self): ...
    @classmethod
    def concatenate(cls, objs: list[Self], axis: int) -> Self: ...
    @property
    def size(self) -> int: ...
    @property
    def nbytes(self) -> int: ...
    @property
    def bytes(self) -> bytes: ...
    @property
    def shape(self) -> tuple[int, ...]: ...
    @property
    def dtype(self) -> type_t[bool]: ...
    def any(self) -> bool: ...
    def all(self) -> bool: ...
    def sum(self) -> int: ...
    def take_1d(self, indices: np.ndarray, axis: int) -> Self: ...
    def copy(self) -> Self: ...
    def to_numpy(self) -> np.ndarray: ...
