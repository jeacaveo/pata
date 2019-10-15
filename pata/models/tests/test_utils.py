""" Test for pata.models module. """
import unittest

from mock import (
    MagicMock,
    Mock,
    )

from pata.models.utils import (
    AuditMixin,
    compare_models,
    )


class AuditMixinCleanTests(unittest.TestCase):
    """ Tests success cases for pata.models.utils.AuditMixin mixin. """

    def test_fields(self):
        """ Tests fields. """
        # When
        mixin_obj = AuditMixin()

        # Then
        self.assertTrue(hasattr(mixin_obj, "created_by"))
        self.assertTrue(hasattr(mixin_obj, "created_at"))
        self.assertTrue(hasattr(mixin_obj, "modified_by"))
        self.assertTrue(hasattr(mixin_obj, "modified_at"))


class CompareModelsCleanTests(unittest.TestCase):
    """ Tests success cases for pata.models.utils.compare_models. """

    def test_diff_same(self):
        """ Test no difference with another object. """
        # Given
        column1 = Mock()
        column1.configure_mock(name="field1")

        model = "model1"
        base_obj = MagicMock(
            field1="same",
            metadata=MagicMock(
                tables={model: MagicMock(columns=[column1])}
            ))
        target_obj = MagicMock(field1="same")
        expected_result = {}

        # When
        result = compare_models(model, base_obj, target_obj)

        # Then
        self.assertEqual(result, expected_result)

    def test_diff(self):
        """ Test difference with another object. """
        column1 = Mock()
        column1.configure_mock(name="id")
        column2 = Mock()
        column2.configure_mock(name="field1")
        column3 = Mock()
        column3.configure_mock(name="field2")
        column4 = Mock()
        column4.configure_mock(name="field3")

        model = "model1"
        base_obj = MagicMock(
            id=9, field1="old value", field2=0, field3="same",
            metadata=MagicMock(
                tables={
                    model: MagicMock(
                        columns=[column1, column2, column3, column4])}
            ))
        target_obj = MagicMock(
            field1="new value", field2=1, field3="same")
        expected_result = {}
        expected_result = {
            "field1": {
                "old": "old value", "new": "new value"},
            "field2": {
                "old": 0, "new": 1},
            }

        # When
        result = compare_models(
            model, base_obj, target_obj, exclude=("id",))

        # Then
        self.assertEqual(result, expected_result)
