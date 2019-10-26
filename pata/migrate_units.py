""" Command line tool to migrate data into pata.models.units models """
import json
import os
import sys

from argparse import (
    ArgumentParser,
    Namespace,
    )
from pprint import pprint
from typing import (
    Any,
    Dict,
    List,
    Tuple,
    Union,
    )

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

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
        path: str
        ) -> Tuple[
            bool,
            Dict[
                str,
                Union[
                    str,
                    int,
                    Dict[str, Union[str, int, bool, List[str]]]]]]:
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
        with open(path, "r") as data_file:
            data = data_file.read()
        return True, json.loads(data)
    except json.decoder.JSONDecodeError:
        return False, {"message": "Invalid format"}


def load_to_models(data: Dict[str, Any]) -> Units:
    """
    Load data into pata.models.units models.

    Parameters
    ----------
    data : dict
        Units data (from JSON).

    Returns
    -------
    tuple(Units, UnitVersions, list(UnitChanges))

    Example
    -------
    input:
        {
            "name": "unit1",
            "position": "Top",
            "type": 4,
            "unit_spell": "Unit",
            "abilities": "ability X",
            "attributes": {
                "blocker": False,
                "fragile": True,
                "frontline": False,
                "prompt": True,
                "build_time": 0,
                "exhaust_ability": 1,
                "exhaust_turn": 0,
                "lifespan": 1,
                "stamina": 0,
                "supply": 1,
                },
            "change_history": {
                "2000-01-01": ["Change 1", "Change 2"],
                },
            "costs": {
                "blue": 3,
                "energy": 0,
                "gold": 13,
                "green": 0,
                "red": 0,
                },
            "links": {
                "image": "image X",
                "panel": "panel X",
                "path": "path X",
                },
            "stats": {
                "attack": 1,
                "health": 1,
                },
        }

    """
    # Units
    links = data.get("links") or {}
    unit = Units(
        name=data.get("name"),
        wiki_path=links.get("path"),
        image_url=links.get("image"),
        panel_url=links.get("panel"),
        )
    # UnitVersions
    stats = data.get("stats") or {}
    costs = data.get("costs") or {}
    attributes = data.get("attributes") or {}
    version = UnitVersions(
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
        unit_spell=data.get("unit_spell"),
        position=data.get("position"),
        abilities=data.get("abilities"),
        )
    # UnitChanges
    changes = [
        UnitChanges(
            unit=unit,
            day=day,
            description=change,
            )
        for day, items in data.get("change_history", {}).items()
        for change in items
        ]

    return unit


def models_diff(
        base: Units, unit: Units
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
    unit.versions and result.update(base.versions[0].diff(unit.versions[0]))
    for base_change in base.changes:
        day = base_change.day
        result.update({
            day:
            base_change.diff(
                next(
                    (change for change in unit.changes if change.day == day),
                    base_change)
                )
            })
    return result


def process_transaction(
        session: Session, unit: Units,
        insert: bool = False, update: bool = False
        ) -> Dict[str, Dict[str, Dict[str, Union[str, int]]]]:
    """
    Apply all changes based on the parameters received.

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQLAlchemy session object.
    unit : pata.models.units.Units
        Units objects.
    version : pata.models.units.UnitVersions
        Latest UnitVersions for unit.
    changes : list(pata.models.units.UnitChanges)
        List of all changes.
    insert : bool, optional
        Process inserts. Defaults to False.
    update : bool, optional
        Process updates. Defaults to False.

    Returns
    -------
    dict

    Example
    -------
    output:
        {
            "update":
                {
                    "column1": "change1",
                    "column2": "change2",
                    "2000-01-01": {"column3": "change3"},
                    ...
                }
        }

    """
    existing = session.query(Units).filter_by(name=unit.name).first()
    result: Dict[str, Dict[str, Dict[str, Union[str, int]]]] = {}

    if not existing:
        result.update({"insert": {}})
        # insert
    else:
        diff = models_diff(existing, unit)
        if not diff:
            result.update({"nochange": {}})
        else:
            result.update({"update": diff})
            # update

    return result


# Executed when ran from the command line.
if __name__ == "__main__":
    PARSER = create_parser(sys.argv[1:])
