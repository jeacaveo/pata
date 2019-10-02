""" Test for pata.models module. """
import unittest
from pata.models.utils import (
    AuditMixin,
    )


class AuditMixinTests(unittest.TestCase):
    """ Tests for pata.models.utils.AuditMixin mixin. """

    def test_fields(self):
        """ Tests fields. """
        # When
        mixin_obj = AuditMixin()

        # Then
        self.assertTrue(hasattr(mixin_obj, "created_by"))
        self.assertTrue(hasattr(mixin_obj, "created_at"))
        self.assertTrue(hasattr(mixin_obj, "modified_by"))
        self.assertTrue(hasattr(mixin_obj, "modified_at"))
