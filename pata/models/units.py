""" Unit related model """
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
from pata.models.utils import AuditMixin


class Units(BASE, AuditMixin):
    """ Units model. """
    __tablename__ = "units"

    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    wiki_path = Column(String(64), nullable=True)
    image_url = Column(String(128), nullable=True)
    panel_url = Column(String(128), nullable=True)

    versions = relationship(
        "UnitVersions",
        order_by="desc(UnitVersions.id)", back_populates="unit")
    changes = relationship(
        "UnitChanges",
        order_by="desc(UnitChanges.day)", back_populates="unit")

    def __repr__(self):
        """ String representation of model. """
        return f"{self.id} - {self.name}"


class UnitVersions(BASE, AuditMixin):
    """ UnitVersions model. """
    __tablename__ = "unit_versions"

    id = Column(Integer, primary_key=True)
    unit_id = Column(Integer, ForeignKey("units.id"))
    gold = Column(Integer)
    green = Column(Integer)
    blue = Column(Integer)
    red = Column(Integer)
    energy = Column(Integer)
    attack = Column(Integer)
    health = Column(Integer)
    supply = Column(Integer)
    unit_spell = Column(String(32))
    frontline = Column(Boolean)
    fragile = Column(Boolean)
    blocker = Column(Boolean)
    prompt = Column(Boolean)
    stamina = Column(Integer)
    lifespan = Column(Integer)
    build_time = Column(Integer)
    exhaust_turn = Column(Integer)
    exhaust_ability = Column(Integer)
    position = Column(String(32))
    abilities = Column(String(256), nullable=True)

    unit = relationship("Units", back_populates="versions")

    def __repr__(self):
        """ String representation of model. """
        return f"Version {self.id} for {self.unit.id} - {self.unit.name}"


class UnitChanges(BASE, AuditMixin):
    """ UnitChanges model. """
    __tablename__ = "unit_changes"

    id = Column(Integer, primary_key=True)
    unit_id = Column(Integer, ForeignKey("units.id"))
    day = Column(Date)
    description = Column(String(1024))

    unit = relationship("Units", back_populates="changes")

    def __repr__(self):
        """ String representation of model. """
        return f"Change to {self.unit.id} - {self.unit.name} for {self.day}"
