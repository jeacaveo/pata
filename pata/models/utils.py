""" Utility models """
from sqlalchemy import (
    Column,
    String,
    TIMESTAMP,
    )


class AuditMixin():  # pylint: disable=too-few-public-methods
    """ Class for audit fields. """
    created_by = Column(String(64))
    created_at = Column(TIMESTAMP(timezone=True))
    modified_by = Column(String(64))
    modified_at = Column(TIMESTAMP(timezone=True))
