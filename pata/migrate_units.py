""" Command line tool to migrate data into pata.models.units models """
import json
import os
import sys
from argparse import (
    ArgumentParser,
    Namespace,
    )
from collections import defaultdict

from typing import (
    Any,
    Dict,
    List,
    Mapping,
    Tuple,
    Union,
    )

from pata.models.units import (
    UnitChanges,
    Units,
    UnitVersions,
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


def load_to_models(
        data: Dict[str, Dict[str, Any]]
        ) -> Dict[
            str, Dict[str, Union[Units, UnitVersions, List[UnitChanges]]]]:
    """
    Load data into pata.models.units models.

    Parameters
    ----------
    data : dict
        Units data (from JSON).

    Returns
    -------
    dict

    """
    result: Mapping[
        str, Dict[str, Union[Units, UnitVersions, List[UnitChanges]]]
        ] = defaultdict(dict)
    for name, values in data.items():
        # Units
        links = values.get("links") or {}
        unit = Units(
            name=name,
            wiki_path=links.get("path"),
            image_url=links.get("image"),
            panel_url=links.get("panel"),
            )
        result[name]["unit"] = unit
        # UnitVersions
        stats = values.get("stats") or {}
        costs = values.get("costs") or {}
        attributes = values.get("attributes") or {}
        result[name]["version"] = UnitVersions(
            unit=unit,
            attack=stats.get("attack"),
            health=stats.get("health"),
            gold=costs.get("gold"),
            green=costs.get("green"),
            blue=costs.get("blue"),
            red=costs.get("red"),
            energy=costs.get("energy"),
            supply=attributes.get("supply"),
            frontline=attributes.get("frontline"),
            fragile=attributes.get("fragile"),
            blocker=attributes.get("blocker"),
            prompt=attributes.get("prompt"),
            stamina=attributes.get("stamina"),
            lifespan=attributes.get("lifespan"),
            build_time=attributes.get("build_time"),
            exhaust_turn=attributes.get("exhaust_turn"),
            exhaust_ability=attributes.get("exhaust_ability"),
            unit_spell=values.get("unit_spell"),
            position=values.get("position"),
            abilities=values.get("abilities"),
            )
        # UnitChanges
        result[name]["changes"] = [
            UnitChanges(
                unit=unit,
                day=day,
                description=change,
                )
            for day, items in values.get("change_history", {}).items()
            for change in items
            ]
    return dict(result)


def models_diff(
        base: Units, unit: Units, version: UnitVersions, changes: UnitChanges
        ) -> Dict[str, Dict[str, Union[str, int]]]:
    """
    Get all differences for a unit and its related models.

    (Only differences with existing records, doesn't consider missing or new.

    Parameters
    ----------
    base : pata.models.units.Units
        Units objects (old/current state).
    unit : pata.models.units.Units
        Units objects (new state).
    version : pata.models.units.UnitVersions
        Latest UnitVersions for unit.
    changes : list(pata.models.units.UnitChanges)
        List of all changes (doesn't consider missing or new records)

    Returns
    -------
    dict

    Example
    -------
    output:
        {
            "column1": "change1",
            "column2": "change2",
            "2000-01-01": {"column3": "change3"},
            ...
        }

    """
    result = {}
    result.update(base.diff(unit))
    result.update(base.versions[0].diff(version))
    for base_change in base.changes:
        day = base_change.day
        result.update({
            day:
            base_change.diff(
                next(
                    (change for change in changes if change.day == day),
                    base_change)
                )
            })
    return result


# Executed when run from the command line.
if __name__ == "__main__":
    PARSER = create_parser(sys.argv[1:])
