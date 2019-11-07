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


class CommonMixin():  # pylint: disable=too-few-public-methods
    """ Mixin for common fields/attributes/methods for all models. """
    created_by = Column(String(64), nullable=False, default="python")
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.now)
    modified_by = Column(String(64), nullable=False, default="python")
    modified_at = Column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.now)

    __tablename__: str = ""
    reserved_fields: Tuple[str, ...] = ()

    def get_columns(self) -> Tuple[str, ...]:
        """
        Get all columns for model (self).

        Returns
        -------
        tuple(str)

        """
        return (
            column.name
            for column in self.metadata.tables[self.__tablename__].columns
            if column.name not in self.reserved_fields
            )

    def diff(self, target: Any) -> Dict[str, Dict[str, Union[str, int]]]:
        """
        Compare current model obj with another.

        Expected type for both objects is the same sqlalchemy.orm.model.

        Parameters
        ----------
        target : sqlalchemy.orm.model
            Object to compare to.

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

        for column in self.get_columns():
            old_value = getattr(self, column)
            new_value = getattr(target, column)
            if old_value != new_value:
                result[column] = {"old": old_value, "new": new_value}

        return result

    def copy(self) -> Any:
        """
        Return a new object (of the same type) that's a
        copy of the current object, but without the reserved_fields.

        Returns
        -------
        pata.models.*

        """
        obj = type(self)()
        for column in self.get_columns():
            setattr(obj, column, getattr(self, column))
        return obj
