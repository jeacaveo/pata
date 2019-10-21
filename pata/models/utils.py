""" Utility models """
from datetime import datetime
from typing import (
    Any,
    Dict,
    Tuple,
    Union,
    )

from sqlalchemy import (
    Column,
    String,
    TIMESTAMP,
    )


class AuditMixin():  # pylint: disable=too-few-public-methods
    """ Class for audit fields. """
    created_by = Column(String(64), nullable=False, default="python")
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.now)
    modified_by = Column(String(64), nullable=False, default="python")
    modified_at = Column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.now)


def compare_models(
        model: str, base: Any, target: Any, exclude: Tuple[str, ...] = ()
        ) -> Dict[str, Dict[str, Union[str, int]]]:
    """
    Compare two models.

    Expected type for both objects is the same sqlalchemy.orm.model.

    Parameters
    ----------
    model : str
        Name of model for objects.
    base : sqlalchemy.orm.model
        Object to copmare.
    target : sqlalchemy.orm.model
        Object to compare to.
    exclude : tuple
        List of fields to exclude.

    Returns
    -------
    dict

    Example
    -------
    output:
        {
            "field_name": {"old": 0, "new": 1},
            ...
        }

    """
    result = {}
    column_names = [
        column.name
        for column in base.metadata.tables[model].columns
        if column.name not in exclude
        ]

    for column_name in column_names:
        old_value = getattr(base, column_name)
        new_value = getattr(target, column_name)
        if old_value != new_value:
            result[column_name] = {"old": old_value, "new": new_value}

    return result
