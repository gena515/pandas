# -*- coding: utf-8 -*-

from __future__ import print_function

from warnings import catch_warnings
import numpy as np

from pandas import DataFrame, Series, MultiIndex, Panel
import pandas as pd
import pandas.util.testing as tm

from pandas.tests.frame.common import TestData


class TestDataFrameSubclassing(TestData):

    def test_frame_subclassing_and_slicing(self):
        # Subclass frame and ensure it returns the right class on slicing it
        # In reference to PR 9632

        class CustomSeries(Series):

            @property
            def _constructor(self):
                return CustomSeries

            def custom_series_function(self):
                return 'OK'

        class CustomDataFrame(DataFrame):
            """
            Subclasses pandas DF, fills DF with simulation results, adds some
            custom plotting functions.
            """

            def __init__(self, *args, **kw):
                super(CustomDataFrame, self).__init__(*args, **kw)

            @property
            def _constructor(self):
                return CustomDataFrame

            _constructor_sliced = CustomSeries

            def custom_frame_function(self):
                return 'OK'

        data = {'col1': range(10),
                'col2': range(10)}
        cdf = CustomDataFrame(data)

        # Did we get back our own DF class?
        assert isinstance(cdf, CustomDataFrame)

        # Do we get back our own Series class after selecting a column?
        cdf_series = cdf.col1
        assert isinstance(cdf_series, CustomSeries)
        assert cdf_series.custom_series_function() == 'OK'

        # Do we get back our own DF class after slicing row-wise?
        cdf_rows = cdf[1:5]
        assert isinstance(cdf_rows, CustomDataFrame)
        assert cdf_rows.custom_frame_function() == 'OK'

        # Make sure sliced part of multi-index frame is custom class
        mcol = pd.MultiIndex.from_tuples([('A', 'A'), ('A', 'B')])
        cdf_multi = CustomDataFrame([[0, 1], [2, 3]], columns=mcol)
        assert isinstance(cdf_multi['A'], CustomDataFrame)

        mcol = pd.MultiIndex.from_tuples([('A', ''), ('B', '')])
        cdf_multi2 = CustomDataFrame([[0, 1], [2, 3]], columns=mcol)
        assert isinstance(cdf_multi2['A'], CustomSeries)

    def test_dataframe_metadata(self):
        df = tm.SubclassedDataFrame({'X': [1, 2, 3], 'Y': [1, 2, 3]},
                                    index=['a', 'b', 'c'])
        df.testattr = 'XXX'

        assert df.testattr == 'XXX'
        assert df[['X']].testattr == 'XXX'
        assert df.loc[['a', 'b'], :].testattr == 'XXX'
        assert df.iloc[[0, 1], :].testattr == 'XXX'

        # see gh-9776
        assert df.iloc[0:1, :].testattr == 'XXX'

        # see gh-10553
        unpickled = tm.round_trip_pickle(df)
        tm.assert_frame_equal(df, unpickled)
        assert df._metadata == unpickled._metadata
        assert df.testattr == unpickled.testattr

    def test_indexing_sliced(self):
        # GH 11559
        df = tm.SubclassedDataFrame({'X': [1, 2, 3],
                                     'Y': [4, 5, 6],
                                     'Z': [7, 8, 9]},
                                    index=['a', 'b', 'c'])
        res = df.loc[:, 'X']
        exp = tm.SubclassedSeries([1, 2, 3], index=list('abc'), name='X')
        tm.assert_series_equal(res, exp)
        assert isinstance(res, tm.SubclassedSeries)

        res = df.iloc[:, 1]
        exp = tm.SubclassedSeries([4, 5, 6], index=list('abc'), name='Y')
        tm.assert_series_equal(res, exp)
        assert isinstance(res, tm.SubclassedSeries)

        res = df.loc[:, 'Z']
        exp = tm.SubclassedSeries([7, 8, 9], index=list('abc'), name='Z')
        tm.assert_series_equal(res, exp)
        assert isinstance(res, tm.SubclassedSeries)

        res = df.loc['a', :]
        exp = tm.SubclassedSeries([1, 4, 7], index=list('XYZ'), name='a')
        tm.assert_series_equal(res, exp)
        assert isinstance(res, tm.SubclassedSeries)

        res = df.iloc[1, :]
        exp = tm.SubclassedSeries([2, 5, 8], index=list('XYZ'), name='b')
        tm.assert_series_equal(res, exp)
        assert isinstance(res, tm.SubclassedSeries)

        res = df.loc['c', :]
        exp = tm.SubclassedSeries([3, 6, 9], index=list('XYZ'), name='c')
        tm.assert_series_equal(res, exp)
        assert isinstance(res, tm.SubclassedSeries)

    def test_subclass_stack(self):
        # GH 15564
        df = tm.SubclassedDataFrame([[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                                    index=['a', 'b', 'c'],
                                    columns=['X', 'Y', 'Z'])

        res = df.stack()
        exp = tm.SubclassedSeries(
            [1, 2, 3, 4, 5, 6, 7, 8, 9],
            index=[list('aaabbbccc'), list('XYZXYZXYZ')])

        tm.assert_series_equal(res, exp)
        tm.assertIsInstance(res, tm.SubclassedSeries)

    def test_subclass_stack_multi(self):
        # GH 15564
        df = tm.SubclassedDataFrame([
            [10, 11, 12, 13],
            [20, 21, 22, 23],
            [30, 31, 32, 33],
            [40, 41, 42, 43]],
            index=MultiIndex.from_tuples(
                list(zip(list('AABB'), list('cdcd'))),
                names=['aaa', 'ccc']),
            columns=MultiIndex.from_tuples(
                list(zip(list('WWXX'), list('yzyz'))),
                names=['www', 'yyy']))

        exp = tm.SubclassedDataFrame([
            [10, 12],
            [11, 13],
            [20, 22],
            [21, 23],
            [30, 32],
            [31, 33],
            [40, 42],
            [41, 43]],
            index=MultiIndex.from_tuples(list(zip(
                list('AAAABBBB'), list('ccddccdd'), list('yzyzyzyz'))),
                names=['aaa', 'ccc', 'yyy']),
            columns=Index(['W', 'X'], name='www'))

        res = df.stack()
        tm.assert_frame_equal(res, exp)
        tm.assertIsInstance(res, tm.SubclassedDataFrame)

        res = df.stack('yyy')
        tm.assert_frame_equal(res, exp)
        tm.assertIsInstance(res, tm.SubclassedDataFrame)

        exp = tm.SubclassedDataFrame([
            [10, 11],
            [12, 13],
            [20, 21],
            [22, 23],
            [30, 31],
            [32, 33],
            [40, 41],
            [42, 43]],
            index=MultiIndex.from_tuples(list(zip(
                list('AAAABBBB'), list('ccddccdd'), list('WXWXWXWX'))),
                names=['aaa', 'ccc', 'www']),
            columns=Index(['y', 'z'], name='yyy'))

        res = df.stack('www')
        tm.assert_frame_equal(res, exp)
        tm.assertIsInstance(res, tm.SubclassedDataFrame)

    def test_subclass_unstack(self):
        # GH 15564
        df = tm.SubclassedDataFrame([[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                                    index=['a', 'b', 'c'],
                                    columns=['X', 'Y', 'Z'])

        res = df.unstack()
        exp = tm.SubclassedSeries(
            [1, 4, 7, 2, 5, 8, 3, 6, 9],
            index=[list('XXXYYYZZZ'), list('abcabcabc')])

        tm.assert_series_equal(res, exp)
        tm.assertIsInstance(res, tm.SubclassedSeries)

    def test_subclass_unstack_multi(self):
        # GH 15564
        df = tm.SubclassedDataFrame([
            [10, 11, 12, 13],
            [20, 21, 22, 23],
            [30, 31, 32, 33],
            [40, 41, 42, 43]],
            index=MultiIndex.from_tuples(
                list(zip(list('AABB'), list('cdcd'))),
                names=['aaa', 'ccc']),
            columns=MultiIndex.from_tuples(
                list(zip(list('WWXX'), list('yzyz'))),
                names=['www', 'yyy']))

        exp = tm.SubclassedDataFrame([
            [10, 20, 11, 21, 12, 22, 13, 23],
            [30, 40, 31, 41, 32, 42, 33, 43]],
            index=Index(['A', 'B'], name='aaa'),
            columns=MultiIndex.from_tuples(list(zip(
                list('WWWWXXXX'), list('yyzzyyzz'), list('cdcdcdcd'))),
            names=['www', 'yyy', 'ccc']))

        res = df.unstack()
        tm.assert_frame_equal(res, exp)
        tm.assertIsInstance(res, tm.SubclassedDataFrame)

        res = df.unstack('ccc')
        tm.assert_frame_equal(res, exp)
        tm.assertIsInstance(res, tm.SubclassedDataFrame)

        exp = tm.SubclassedDataFrame([
            [10, 30, 11, 31, 12, 32, 13, 33],
            [20, 40, 21, 41, 22, 42, 23, 43]],
            index=Index(['c', 'd'], name='ccc'),
            columns=MultiIndex.from_tuples(list(zip(
                list('WWWWXXXX'), list('yyzzyyzz'), list('ABABABAB'))),
                names=['www', 'yyy', 'aaa']))

        res = df.unstack('aaa')
        tm.assert_frame_equal(res, exp)
        tm.assertIsInstance(res, tm.SubclassedDataFrame)

    def test_subclass_pivot(self):
        # GH 15564
        df = tm.SubclassedDataFrame({
            'index': ['A', 'B', 'C', 'C', 'B', 'A'],
            'columns': ['One', 'One', 'One', 'Two', 'Two', 'Two'],
            'values': [1., 2., 3., 3., 2., 1.]})

        pivoted = df.pivot(
            index='index', columns='columns', values='values')

        expected = tm.SubclassedDataFrame({
            'One': {'A': 1., 'B': 2., 'C': 3.},
            'Two': {'A': 1., 'B': 2., 'C': 3.}})

        expected.index.name, expected.columns.name = 'index', 'columns'

        tm.assert_frame_equal(pivoted, expected)
        tm.assertIsInstance(pivoted, tm.SubclassedDataFrame)

    def test_to_panel_expanddim(self):
        # GH 9762

        with catch_warnings(record=True):
            class SubclassedFrame(DataFrame):

                @property
                def _constructor_expanddim(self):
                    return SubclassedPanel

            class SubclassedPanel(Panel):
                pass

            index = MultiIndex.from_tuples([(0, 0), (0, 1), (0, 2)])
            df = SubclassedFrame({'X': [1, 2, 3], 'Y': [4, 5, 6]}, index=index)
            result = df.to_panel()
            assert isinstance(result, SubclassedPanel)
            expected = SubclassedPanel([[[1, 2, 3]], [[4, 5, 6]]],
                                       items=['X', 'Y'], major_axis=[0],
                                       minor_axis=[0, 1, 2],
                                       dtype='int64')
            tm.assert_panel_equal(result, expected)

    def test_subclass_attr_err_propagation(self):
        # GH 11808
        class A(DataFrame):

            @property
            def bar(self):
                return self.i_dont_exist
        with tm.assert_raises_regex(AttributeError, '.*i_dont_exist.*'):
            A().bar

    def test_subclass_align(self):
        # GH 12983
        df1 = tm.SubclassedDataFrame({'a': [1, 3, 5],
                                      'b': [1, 3, 5]}, index=list('ACE'))
        df2 = tm.SubclassedDataFrame({'c': [1, 2, 4],
                                      'd': [1, 2, 4]}, index=list('ABD'))

        res1, res2 = df1.align(df2, axis=0)
        exp1 = tm.SubclassedDataFrame({'a': [1, np.nan, 3, np.nan, 5],
                                       'b': [1, np.nan, 3, np.nan, 5]},
                                      index=list('ABCDE'))
        exp2 = tm.SubclassedDataFrame({'c': [1, 2, np.nan, 4, np.nan],
                                       'd': [1, 2, np.nan, 4, np.nan]},
                                      index=list('ABCDE'))
        assert isinstance(res1, tm.SubclassedDataFrame)
        tm.assert_frame_equal(res1, exp1)
        assert isinstance(res2, tm.SubclassedDataFrame)
        tm.assert_frame_equal(res2, exp2)

        res1, res2 = df1.a.align(df2.c)
        assert isinstance(res1, tm.SubclassedSeries)
        tm.assert_series_equal(res1, exp1.a)
        assert isinstance(res2, tm.SubclassedSeries)
        tm.assert_series_equal(res2, exp2.c)

    def test_subclass_align_combinations(self):
        # GH 12983
        df = tm.SubclassedDataFrame({'a': [1, 3, 5],
                                     'b': [1, 3, 5]}, index=list('ACE'))
        s = tm.SubclassedSeries([1, 2, 4], index=list('ABD'), name='x')

        # frame + series
        res1, res2 = df.align(s, axis=0)
        exp1 = pd.DataFrame({'a': [1, np.nan, 3, np.nan, 5],
                             'b': [1, np.nan, 3, np.nan, 5]},
                            index=list('ABCDE'))
        # name is lost when
        exp2 = pd.Series([1, 2, np.nan, 4, np.nan],
                         index=list('ABCDE'), name='x')

        assert isinstance(res1, tm.SubclassedDataFrame)
        tm.assert_frame_equal(res1, exp1)
        assert isinstance(res2, tm.SubclassedSeries)
        tm.assert_series_equal(res2, exp2)

        # series + frame
        res1, res2 = s.align(df)
        assert isinstance(res1, tm.SubclassedSeries)
        tm.assert_series_equal(res1, exp2)
        assert isinstance(res2, tm.SubclassedDataFrame)
        tm.assert_frame_equal(res2, exp1)

    def test_subclass_iterrows(self):
        # GH 13977
        df = tm.SubclassedDataFrame({'a': [1]})
        for i, row in df.iterrows():
            assert isinstance(row, tm.SubclassedSeries)
            tm.assert_series_equal(row, df.loc[i])

    def test_subclass_sparse_slice(self):
        rows = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]
        ssdf = tm.SubclassedSparseDataFrame(rows)
        ssdf.testattr = "testattr"

        tm.assert_sp_frame_equal(ssdf.loc[:2],
                                 tm.SubclassedSparseDataFrame(rows[:3]))
        tm.assert_sp_frame_equal(ssdf.iloc[:2],
                                 tm.SubclassedSparseDataFrame(rows[:2]))
        tm.assert_sp_frame_equal(ssdf[:2],
                                 tm.SubclassedSparseDataFrame(rows[:2]))
        assert ssdf.loc[:2].testattr == "testattr"
        assert ssdf.iloc[:2].testattr == "testattr"
        assert ssdf[:2].testattr == "testattr"

        tm.assert_sp_series_equal(ssdf.loc[1],
                                  tm.SubclassedSparseSeries(rows[1]),
                                  check_names=False)
        tm.assert_sp_series_equal(ssdf.iloc[1],
                                  tm.SubclassedSparseSeries(rows[1]),
                                  check_names=False)

    def test_subclass_sparse_transpose(self):
        ossdf = tm.SubclassedSparseDataFrame([[1, 2, 3],
                                              [4, 5, 6]])
        essdf = tm.SubclassedSparseDataFrame([[1, 4],
                                              [2, 5],
                                              [3, 6]])
        tm.assert_sp_frame_equal(ossdf.T, essdf)
