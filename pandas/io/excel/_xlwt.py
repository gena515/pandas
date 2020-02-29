from typing import Dict, Optional, Tuple

import pandas._libs.json as json

from pandas.io.excel._base import ExcelWriter
from pandas.io.excel._util import _validate_freeze_panes


class _XlwtWriter(ExcelWriter):
    engine = "xlwt"
    supported_extensions = (".xls",)

    def __init__(self, path, engine=None, encoding=None, mode="w", **engine_kwargs):
        # Use the xlwt module as the Excel writer.
        import xlwt

        engine_kwargs["engine"] = engine

        if mode == "a":
            raise ValueError("Append mode is not supported with xlwt!")

        super().__init__(path, mode=mode, **engine_kwargs)

        if encoding is None:
            encoding = "ascii"
        self.book = xlwt.Workbook(encoding=encoding)
        self.fm_datetime = xlwt.easyxf(num_format_str=self.datetime_format)
        self.fm_date = xlwt.easyxf(num_format_str=self.date_format)

    def save(self):
        """
        Save workbook to disk.
        """
        return self.book.save(self.path)

    def write_cells(
        self,
        cells,
        sheet_name: Optional[str] = None,
        startrow: int = 0,
        startcol: int = 0,
        freeze_panes: Optional[Tuple[int, int]] = None,
    ):
        # Write the frame cells using xlwt.

        sheet_name = self._get_sheet_name(sheet_name)

        if sheet_name in self.sheets:
            wks = self.sheets[sheet_name]
        else:
            assert self.book is not None
            wks = self.book.add_sheet(sheet_name)
            self.sheets[sheet_name] = wks

        if _validate_freeze_panes(freeze_panes):
            assert freeze_panes is not None
            wks.set_panes_frozen(True)
            row, column = freeze_panes
            wks.set_horz_split_pos(row)
            wks.set_vert_split_pos(column)

        style_dict: Dict = {}

        for cell in cells:
            val, fmt = self._value_with_fmt(cell.val)

            stylekey = json.dumps(cell.style)
            if fmt:
                stylekey += fmt

            if stylekey in style_dict:
                style = style_dict[stylekey]
            else:
                style = self._convert_to_style(cell.style, fmt)
                style_dict[stylekey] = style

            if cell.mergestart is not None and cell.mergeend is not None:
                wks.write_merge(
                    startrow + cell.row,
                    startrow + cell.mergestart,
                    startcol + cell.col,
                    startcol + cell.mergeend,
                    val,
                    style,
                )
            else:
                wks.write(startrow + cell.row, startcol + cell.col, val, style)

    @classmethod
    def _style_to_xlwt(
        cls, item, firstlevel: bool = True, field_sep=",", line_sep=";"
    ) -> str:
        """
        helper which recursively generate an xlwt easy style string
        for example:

            hstyle = {"font": {"bold": True},
            "border": {"top": "thin",
                    "right": "thin",
                    "bottom": "thin",
                    "left": "thin"},
            "align": {"horiz": "center"}}
            will be converted to
            font: bold on; \
                    border: top thin, right thin, bottom thin, left thin; \
                    align: horiz center;
        """
        if hasattr(item, "items"):
            if firstlevel:
                it = [
                    f"{key}: {cls._style_to_xlwt(value, False)}"
                    for key, value in item.items()
                ]
                out = f"{(line_sep).join(it)} "
                return out
            else:
                it = [
                    f"{key} {cls._style_to_xlwt(value, False)}"
                    for key, value in item.items()
                ]
                out = f"{(field_sep).join(it)} "
                return out
        else:
            item = f"{item}"
            item = item.replace("True", "on")
            item = item.replace("False", "off")
            return item

    @classmethod
    def _convert_to_style(cls, style_dict, num_format_str=None):
        """
        converts a style_dict to an xlwt style object

        Parameters
        ----------
        style_dict : style dictionary to convert
        num_format_str : optional number format string
        """
        import xlwt

        if style_dict:
            xlwt_stylestr = cls._style_to_xlwt(style_dict)
            style = xlwt.easyxf(xlwt_stylestr, field_sep=",", line_sep=";")
        else:
            style = xlwt.XFStyle()
        if num_format_str is not None:
            style.num_format_str = num_format_str

        return style
