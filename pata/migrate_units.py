""" Command line tool to migrate data into pata.models.units models """
import json
import os
import sys
from argparse import (
    ArgumentParser,
    Namespace,
    )

from typing import (
    Any,
    Dict,
    List,
    Tuple,
    Union,
    )


def create_parser(args: List[str]) -> Namespace:
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


def load_version(
        path: str) -> Tuple[bool, Dict[str, Union[str, Dict[str, Any]]]]:
    """
    Load information for units from JSON file.

    Parameters
    ----------
    path : str
        List of commands to parse.

    Returns
    -------
    tuple(bool, dict)

    """
    if not os.path.isfile(path):
        return False, {"message": "File doesn't exist"}

    try:
        return True, json.loads(path)
    except json.decoder.JSONDecodeError:
        return False, {"message": "Invalid format"}


# Executed when run from the command line.
if __name__ == "__main__":
    PARSER = create_parser(sys.argv[1:])
