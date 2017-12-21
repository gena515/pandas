import numpy as np
from pandas import DataFrame, date_range, ExcelWriter, read_excel
from pandas.compat import BytesIO
import pandas.util.testing as tm

from ..pandas_vb_common import BaseIO, setup  # noqa


class Excel(object):

    goal_time = 0.2
    params = ['openpyxl', 'xlsxwriter', 'xlwt']
    param_names = ['engine']

    def setup(self, engine):
        N = 2000
        C = 5
        self.df = DataFrame(np.random.randn(N, C),
                            columns=['float{}'.format(i) for i in range(C)],
                            index=date_range('20000101', periods=N, freq='H'))
        self.df['object'] = tm.makeStringIndex(N)
        self.bio_read = BytesIO()
        self.writer_read = ExcelWriter(self.bio_read, engine=engine)
        self.df.to_excel(self.writer_read, sheet_name='Sheet1')
        self.writer_read.save()
        self.bio_read.seek(0)

        self.bio_write = BytesIO()
        self.writer_write = ExcelWriter(self.bio_write, engine=engine)
        self.bio_write.seek(0)

    def time_read_excel(self, engine):
        read_excel(self.bio_read)

    def time_write_excel(self, engine):
        self.df.to_excel(self.bio_write, sheet_name='Sheet1')
        self.writer_write.save()
