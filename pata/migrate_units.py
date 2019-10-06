""" Command line tool to migrate data into pata.models.units models """
import sys
from argparse import ArgumentParser

from typing import List


def create_parser(args: List[str]) -> ArgumentParser:
    """
    Create parser to call units migrations from the command line.

    Parameters
    ----------
    args : list(str)
        List of commands to parse.

    Returns
    -------
    ArgumentParser

    """
    parser_obj = ArgumentParser()

    # Required positional argument
    parser_obj.add_argument(
        "source",
        help="Path to JSON file with information to update")
    # Optional/Flags
    parser_obj.add_argument(
        "-d", "--diff",
        action="store_true", default=False,
        help="Only show differences (no insertd/updat).")
    parser_obj.add_argument(
        "-i", "--insert",
        action="store_true", default=False,
        help="Only insert new units (no updates)")
    parser_obj.add_argument(
        "-u", "--update",
        action="store_true", default=False,
        help="Only update new units (no inserts)")

    return parser_obj.parse_args(args)


# Executed when run from the command line.
if __name__ == "__main__":
    PARSER = create_parser(sys.argv[1:])
