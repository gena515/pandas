"""
Check files use pd_array from pandas.core.construction rather than pd.array.

This is only run within pandas/core and makes it easier to grep for usage of
pandas array.

This is meant to be run as a pre-commit hook - to run it manually, you can do:

    pre-commit run use-pd_array-in-core --all-files

"""

import argparse
import ast
import sys
from typing import (
    Optional,
    Sequence,
)

ERROR_MESSAGE = (
    "{path}:{lineno}:{col_offset}: "
    "Don't use pd.array in core, instead use "
    "'from pandas.core.construction import pd_array'\n"
)


class Visitor(ast.NodeVisitor):
    def __init__(self, path: str) -> None:
        self.path = path

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        # If array has been imported from somewhere in pandas,
        # check it's aliased as pd_array.
        if (
            node.module is not None
            and node.module.startswith("pandas")
            and any(i.name == "array" for i in node.names)
        ):
            msg = ERROR_MESSAGE.format(
                path=self.path, lineno=node.lineno, col_offset=node.col_offset
            )
            sys.stdout.write(msg)
            sys.exit(1)
        super().generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if (
            isinstance(node.value, ast.Name)
            and node.value.id == "pd"
            and node.attr == "array"
        ):
            msg = ERROR_MESSAGE.format(
                path=self.path, lineno=node.lineno, col_offset=node.col_offset
            )
            sys.stdout.write(msg)
            sys.exit(1)
        super().generic_visit(node)


def use_pd_array(content: str, path: str) -> None:
    tree = ast.parse(content)
    visitor = Visitor(path)
    visitor.visit(tree)
    return


def main(argv: Optional[Sequence[str]] = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*")
    args = parser.parse_args(argv)

    for path in args.paths:
        with open(path, encoding="utf-8") as fd:
            content = fd.read()
        use_pd_array(content, path)


if __name__ == "__main__":
    main()
