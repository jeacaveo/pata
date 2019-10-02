""" Unit related model """
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    )

from pata.config import BASE
from pata.models.utils import AuditMixin


class Units(BASE, AuditMixin):
    """ Units model. """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(64))
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
    abilities = Column(String(256))
