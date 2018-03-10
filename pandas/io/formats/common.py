# -*- coding: utf-8 -*-
"""
Common helper methods used in different submodules of pandas.io.formats
"""

from pandas import compat


def get_level_lengths(levels, sentinel=''):
    """For each index in each level the function returns lengths of indexes.

    Parameters
    ----------
    levels : list of lists
        List of values on for level.
    sentinel : string, optional
        Value which states that no new index starts on there.

    Returns
    ----------
    Returns list of maps. For each level returns map of indexes (key is index
    in row and value is length of index).
    """
    if len(levels) == 0:
        return []

    control = [True for x in levels[0]]

    result = []
    for level in levels:
        last_index = 0

        lengths = {}
        for i, key in enumerate(level):
            if control[i] and key == sentinel:
                pass
            else:
                control[i] = False
                lengths[last_index] = i - last_index
                last_index = i

        lengths[last_index] = len(level) - last_index

        result.append(lengths)

    return result


def buffer_put_lines(buf, lines):
    """
    Appends lines to a buffer.

    Parameters
    ----------
    buf
        The buffer to write to
    lines
        The lines to append.
    """
    if any(isinstance(x, compat.text_type) for x in lines):
        lines = [compat.text_type(x) for x in lines]
    buf.write('\n'.join(lines))
