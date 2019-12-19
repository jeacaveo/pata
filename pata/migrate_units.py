""" Command line tool to migrate data into pata.models.units models """
import json
import os
import sys

from argparse import (
    ArgumentParser,
    Namespace,
    )
from collections import defaultdict
from datetime import date
from pprint import pformat
from typing import (
    Any,
    Dict,
    List,
    Union,
    )

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from pata.config import (
    DATABASES,
    get_database_url,
    LOGGER as logger,
    ROOT_LOGGER as root_logger,
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


def load_version(path: str) -> Any:
    """
    Load information for units from JSON file.

    Parameters
    ----------
    path : str
        List of commands to parse.

    Returns
    -------
    dict

    """
    if not os.path.isfile(path):
        logger.error("File doesn't exist")
        return {}

    try:
        with open(path, "r") as data_file:
            data = data_file.read()
        return json.loads(data)
    except json.decoder.JSONDecodeError:
        logger.error("Invalid format")
        return {}


def load_to_models(data: Dict[str, Any]) -> Units:
    """
    Load data into pata.models.units models.

    Parameters
    ----------
    data : dict
        Units data (from JSON).

    Returns
    -------
    obj: pata.models.units.Units

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
    logger.info("Loading %s into model", data.get("name"))

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
    UnitVersions(
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
    for day, items in data.get("change_history", {}).items():
        for change in items:
            UnitChanges(
                unit=unit,
                day=date.fromisoformat(day),
                description=change,
                )

    return unit


def models_diff(base: Units, unit: Units) -> Dict[str, Any]:
    """
    Get all differences for a unit and its related models.

    Doesn't take under consideration missing/deleted/new records
    for Untis and UnitVersions.

    For UnitChanges, doesn't look for differences, only for new records.

    Parameters
    ----------
    base : pata.models.units.Units
        Units objects (old/current state).
    unit : pata.models.units.Units
        Units objects (new state).

    Returns
    -------
    dict

    Example
    -------
    output:
    {
        "units":
            {
                "column1": "change1",
                ...
            },
        "unit_versions":
            {
                "column2": "change2",
                ...
            },
        "unit_changes":
            {
                0: {"day": "change3", "description": "change4"},
                ...
            },
    }

    """
    result: Dict[str, Any] = defaultdict(dict)
    result["units"].update(base.diff(unit))

    if unit.versions:
        result["unit_versions"].update(base.versions[0].diff(unit.versions[0]))

    base_days = [base_change.day for base_change in base.changes]
    for index, change in enumerate(unit.changes):
        if change.day not in base_days:
            result["unit_changes"].update({
                index: UnitChanges().diff(change)})

    return dict(result)


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
    if not existing:
        insert and session.add(unit)  # pylint: disable=expression-not-assigned
        return {"insert": {}}

    diff = models_diff(existing, unit)
    if update:
        # Update specific fields when a field from Units model changes
        for key, value in diff.get("units", {}).items():
            setattr(existing, key, value.get("new"))

        # Always insert a new record when UnitVersions changes
        if diff.get("unit_versions", {}):
            existing.versions.append(unit.versions[0].copy())

        # Always insert a new record when UnitChanges changes
        new_changes = [
            changes.get("day", {}).get("new")
            for _, changes in diff.get("unit_changes", {}).items()
            ]
        for change in unit.changes:
            if change.day in new_changes:
                existing.changes.append(change.copy())

    updated = (
        diff.get("units")
        or diff.get("unit_versions")
        or diff.get("unit_changes")
        )
    return {"update": diff} if updated else {"nochange": {}}


def run(
        data: Dict[str, Any],
        insert: bool = False, update: bool = False
        ) -> Dict[str, Any]:
    """
    Insert/Update information in data into the database.

    Returns the summary of changes.

    Parameters
    ----------
    data : dict
        Information to insert/update.
    unit : pata.models.units.Units
        Units objects.
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
            "unit1":
                {
                    "update":
                        {
                            "column1": "change1",
                            "column2": "change2",
                            "2000-01-01": {"column3": "change3"},
                            ...
                        }
                },
            ...
        }

    """
    engine = create_engine(get_database_url(DATABASES.get("sqlite") or {}))
    session_class = sessionmaker(bind=engine)
    session = session_class()
    logger.info("Session: Opened")
    try:
        diff_result = {}
        for unit_name, unit_data in data.items():
            unit = load_to_models(unit_data)
            diff_result[unit_name] = process_transaction(
                session, unit, insert, update)

        diff_changes = (any(filter(
            lambda item: "insert" in item or "update" in item,  # type: ignore
            diff_result.values())))
        logger.info("Diff/Changes:\n%s", pformat(diff_result))
        if (update or insert) and diff_changes:
            session.commit()
            logger.info("Session: Committed")
    except SQLAlchemyError as exc:
        session.rollback()
        logger.error("DB error. Rolling back.\n%s", exc)
    finally:
        logger.info("Session: Closed")
        session.close()

    return diff_result


def run_command(
        path: str,
        diff: bool = False, insert: bool = False, update: bool = False
        ) -> Dict[str, Any]:
    """
    Execute command.

    Parameters
    ----------
    path : str
        Path to file to load data from.
    diff : bool, optional
        Show diff result. Defaults to False.
    insert : bool, optional
        Process inserts. Defaults to False.
    update : bool, optional
        Process updates. Defaults to False.

    Returns
    -------
    dict

    """
    logger.info("Loading units from: %s", path)
    changes = run(load_version(path), insert=insert, update=update)
    return changes if diff else {"status": "Done"}


# Executed when ran from the command line.
if __name__ == "__main__":
    PARSER = create_parser(sys.argv[1:])
    root_logger.info(
        pformat(
            run_command(
                PARSER.source, PARSER.diff, PARSER.insert, PARSER.update)))
