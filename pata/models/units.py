""" Unit related model """
from typing import (
    Dict,
    Union,
    )

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    Integer,
    ForeignKey,
    String,
    )
from sqlalchemy.orm import relationship

from pata.config import BASE
from pata.models.utils import CommonMixin


class Units(BASE, CommonMixin):  # type: ignore
    """ Units model. """
    __tablename__ = "units"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False, unique=True)
    wiki_path = Column(String(64))
    image_url = Column(String(128))
    panel_url = Column(String(128))

    versions = relationship(
        "UnitVersions",
        order_by="desc(UnitVersions.id)", back_populates="unit")
    changes = relationship(
        "UnitChanges",
        order_by="desc(UnitChanges.day)", back_populates="unit")

    def __repr__(self) -> str:
        """ String representation of model. """
        return f"{self.id} - {self.name}"

    def diff(self, obj: "Units") -> Dict[str, Dict[str, Union[str, int]]]:
        """
        Compare with another object.

        Parameters
        ----------
        obj : pata.models.units.Units
            Object to copmare with.

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
        return self.compare_models(
            obj,
            exclude=(
                "id",
                "created_by",
                "created_at",
                "modified_by",
                "modified_at",
                ))


class UnitVersions(BASE, CommonMixin):  # type: ignore
    """ UnitVersions model. """
    __tablename__ = "unit_versions"

    id = Column(Integer, primary_key=True)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False)
    gold = Column(Integer, nullable=False)
    green = Column(Integer, nullable=False)
    blue = Column(Integer, nullable=False)
    red = Column(Integer, nullable=False)
    energy = Column(Integer, nullable=False)
    attack = Column(Integer, nullable=False)
    health = Column(Integer, nullable=False)
    supply = Column(Integer, nullable=False)
    unit_spell = Column(String(32), nullable=False)
    frontline = Column(Boolean, nullable=False)
    fragile = Column(Boolean, nullable=False)
    blocker = Column(Boolean, nullable=False)
    prompt = Column(Boolean, nullable=False)
    stamina = Column(Integer, nullable=False)
    lifespan = Column(Integer, nullable=False)
    build_time = Column(Integer, nullable=False)
    exhaust_turn = Column(Integer, nullable=False)
    exhaust_ability = Column(Integer, nullable=False)
    position = Column(String(32))
    abilities = Column(String(256))

    unit = relationship("Units", back_populates="versions")

    def __repr__(self) -> str:
        """ String representation of model. """
        return (
            f"Version {self.id} for "
            f"{self.unit and self.unit.id} - "
            f"{self.unit and self.unit.name}")

    def diff(
            self, obj: "UnitVersions") -> Dict[
                str, Dict[str, Union[str, int]]]:
        """
        Compare with another object.

        Parameters
        ----------
        obj : pata.models.units.UnitVersions
            Object to copmare with.

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
        return self.compare_models(
            obj,
            exclude=(
                "id",
                "unit_id",
                "created_by",
                "created_at",
                "modified_by",
                "modified_at",
                ))


class UnitChanges(BASE, CommonMixin):  # type: ignore
    """ UnitChanges model. """
    __tablename__ = "unit_changes"

    id = Column(Integer, primary_key=True)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False)
    day = Column(Date, nullable=False)
    description = Column(String(1024), nullable=False)

    unit = relationship("Units", back_populates="changes")

    def __repr__(self) -> str:
        """ String representation of model. """
        return f"Change to {self.unit.id} - {self.unit.name} for {self.day}"

    def diff(
            self, obj: "UnitChanges") -> Dict[
                str, Dict[str, Union[str, int]]]:
        """
        Compare with another object.

        Parameters
        ----------
        obj : pata.models.units.UnitChanges
            Object to copmare with.

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
        return self.compare_models(
            obj,
            exclude=(
                "id",
                "unit_id",
                "created_by",
                "created_at",
                "modified_by",
                "modified_at",
                ))
