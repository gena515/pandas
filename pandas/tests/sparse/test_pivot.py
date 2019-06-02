import numpy as np
import pytest

import pandas as pd
from pandas import _np_version_under1p17
import pandas.util.testing as tm


@pytest.mark.filterwarnings("ignore:Sparse:FutureWarning")
@pytest.mark.filterwarnings("ignore:Series.to_sparse:FutureWarning")
@pytest.mark.filterwarnings("ignore:DataFrame.to_sparse:FutureWarning")
class TestPivotTable:

    def setup_method(self, method):
        self.dense = pd.DataFrame({'A': ['foo', 'bar', 'foo', 'bar',
                                         'foo', 'bar', 'foo', 'foo'],
                                   'B': ['one', 'one', 'two', 'three',
                                         'two', 'two', 'one', 'three'],
                                   'C': np.random.randn(8),
                                   'D': np.random.randn(8),
                                   'E': [np.nan, np.nan, 1, 2,
                                         np.nan, 1, np.nan, np.nan]})
        self.sparse = self.dense.to_sparse()

    def test_pivot_table(self):
        res_sparse = pd.pivot_table(self.sparse, index='A', columns='B',
                                    values='C')
        res_dense = pd.pivot_table(self.dense, index='A', columns='B',
                                   values='C')
        tm.assert_frame_equal(res_sparse, res_dense)

        res_sparse = pd.pivot_table(self.sparse, index='A', columns='B',
                                    values='E')
        res_dense = pd.pivot_table(self.dense, index='A', columns='B',
                                   values='E')
        tm.assert_frame_equal(res_sparse, res_dense)

        res_sparse = pd.pivot_table(self.sparse, index='A', columns='B',
                                    values='E', aggfunc='mean')
        res_dense = pd.pivot_table(self.dense, index='A', columns='B',
                                   values='E', aggfunc='mean')
        tm.assert_frame_equal(res_sparse, res_dense)

        # ToDo: sum doesn't handle nan properly
        # res_sparse = pd.pivot_table(self.sparse, index='A', columns='B',
        #                             values='E', aggfunc='sum')
        # res_dense = pd.pivot_table(self.dense, index='A', columns='B',
        #                            values='E', aggfunc='sum')
        # tm.assert_frame_equal(res_sparse, res_dense)

    @pytest.mark.parametrize(
        'func',
        ['mean',
         'std',
         'var',
         'sem',
         pytest.param('median', marks=pytest.mark.xfail(
             not _np_version_under1p17, reason="fails on numpy > 1.16")),
         'first',
         'last'])
    @pytest.mark.parametrize('dropna', [True, False])
    def test_pivot_table_multi(self, func, dropna):

        res_sparse = pd.pivot_table(
            self.sparse, index='A', columns='B',
            values=['D', 'E'], aggfunc=func, dropna=dropna)
        res_dense = pd.pivot_table(
            self.dense, index='A', columns='B',
            values=['D', 'E'], aggfunc=func, dropna=dropna)
        res_dense = res_dense.apply(lambda x: x.astype("Sparse[float64]"))
        tm.assert_frame_equal(res_sparse, res_dense)
