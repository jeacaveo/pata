""" Test for pata.models module. """
import unittest

from mock import (
    MagicMock,
    Mock,
    patch,
    )

from pata.models.utils import CommonMixin


class CommonMixinCleanTests(unittest.TestCase):
    """ Tests success cases for pata.models.utils.CommonMixin mixin. """

    def test_fields(self):
        """ Tests fields. """
        # When
        mixin_obj = CommonMixin()

        # Then
        self.assertTrue(hasattr(mixin_obj, "created_by"))
        self.assertTrue(hasattr(mixin_obj, "created_at"))
        self.assertTrue(hasattr(mixin_obj, "modified_by"))
        self.assertTrue(hasattr(mixin_obj, "modified_at"))
        self.assertEqual(mixin_obj.__tablename__, "")
        self.assertEqual(mixin_obj.reserved_fields, ())

    def test_columns(self):
        """ Test columns property. """
        # Given
        column_name = "field2"
        column1 = Mock()
        column1.configure_mock(name="field1")
        column2 = Mock()
        column2.configure_mock(name=column_name)
        mixin_obj = CommonMixin()
        mixin_obj.__tablename__ = "testname"
        mixin_obj.reserved_fields = ("field1",)
        mixin_obj.metadata = MagicMock(
            tables={
                mixin_obj.__tablename__:
                MagicMock(columns=[column1, column2])}
            )

        expected_result = (column_name,)

        # When
        result = mixin_obj.get_columns()

        # Then
        self.assertEqual(list(result), list(expected_result))

    @patch("pata.models.utils.CommonMixin.get_columns")
    def test_diff_same(self, columns_mock):
        """ Test no difference with another object. """
        # Given
        mixin_obj = CommonMixin()
        mixin_obj.field1 = "same"
        target_obj = MagicMock(field1="same")
        expected_result = {}

        columns_mock.return_value = ("field1",)

        # When
        result = mixin_obj.diff(target_obj)

        # Then
        self.assertEqual(result, expected_result)

    @patch("pata.models.utils.CommonMixin.get_columns")
    def test_diff(self, columns_mock):
        """ Test difference with another object. """
        mixin_obj = CommonMixin()
        mixin_obj.field1 = "old value"
        mixin_obj.field2 = 0
        mixin_obj.field3 = "same"
        target_obj = MagicMock(
            field1="new value", field2=1, field3="same")

        expected_result = {
            "field1": {
                "old": "old value", "new": "new value"},
            "field2": {
                "old": 0, "new": 1},
            }

        columns_mock.return_value = ("field1", "field2", "field3")

        # When
        result = mixin_obj.diff(target_obj)

        # Then
        self.assertEqual(result, expected_result)

    @patch("pata.models.utils.CommonMixin.get_columns")
    def test_copy(self, columns_mock):
        """ Test generating a copy of a model. """
        mixin_obj = CommonMixin()
        mixin_obj.valid_field = "valid"
        mixin_obj.invalid_field = "invalid"

        columns_mock.return_value = ("valid_field",)

        # When
        result = mixin_obj.copy()

        # Then
        self.assertEqual(type(result), type(mixin_obj))
        self.assertEqual(result.valid_field, mixin_obj.valid_field)
        self.assertFalse(hasattr(result, "invalid_field"))
