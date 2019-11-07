""" Test for pata.models module. """
import unittest

from mock import patch

from pata.models.units import (
    UnitChanges,
    UnitVersions,
    Units,
    )


class UnitsCleanTests(unittest.TestCase):
    """ Tests success cases for pata.models.Units model. """

    def test_fields(self):
        """ Tests database fields. """
        # Given
        expected_result = [
            "created_by",
            "created_at",
            "modified_by",
            "modified_at",
            "id",
            "name",
            "wiki_path",
            "image_url",
            "panel_url",
            ]

        # When
        obj = Units()
        columns = [
            column.name
            for column in obj.metadata.tables["units"].columns
            ]

        # Then
        self.assertEqual(columns, expected_result)

    def test_repr(self):
        """ Tests string representation. """
        # Given
        unit_id = 99
        name = "unit name"
        expected_result = f"{unit_id} - {name}"

        # When
        obj = Units(id=unit_id, name=name)

        # Then
        self.assertEqual(str(obj), expected_result)

    @patch("pata.models.units.Units.compare_models")
    def test_diff(self, compare_mock):
        """ Test call to comparison function. """
        # Given
        other_obj = Units()
        expected_result = {}

        compare_mock.return_value = expected_result

        # When
        result = Units().diff(other_obj)

        # Then
        self.assertEqual(result, expected_result)
        compare_mock.assert_called_once_with(other_obj)


class UnitVersionsCleanTests(unittest.TestCase):
    """ Tests success cases for pata.models.UnitVersions model. """

    def test_fields(self):
        """ Tests database fields. """
        # Given
        expected_result = [
            "created_by",
            "created_at",
            "modified_by",
            "modified_at",
            "id",
            "unit_id",
            "gold",
            "green",
            "blue",
            "red",
            "energy",
            "attack",
            "health",
            "supply",
            "unit_spell",
            "frontline",
            "fragile",
            "blocker",
            "prompt",
            "stamina",
            "lifespan",
            "build_time",
            "exhaust_turn",
            "exhaust_ability",
            "position",
            "abilities",
            ]

        # When
        obj = UnitVersions()
        columns = [
            column.name
            for column in obj.metadata.tables["unit_versions"].columns
            ]

        # Then
        self.assertEqual(columns, expected_result)

    def test_repr(self):
        """ Tests string representation. """
        # Given
        version_id = 88
        unit_id = 99
        name = "unit name"
        expected_result = f"Version {version_id} for {unit_id} - {name}"

        # When
        obj = UnitVersions(id=version_id, unit=Units(id=unit_id, name=name))

        # Then
        self.assertEqual(str(obj), expected_result)

    @patch("pata.models.units.UnitVersions.compare_models")
    def test_diff(self, compare_mock):
        """ Test call to comparison function. """
        # Given
        other_obj = UnitVersions()
        expected_result = {}

        compare_mock.return_value = expected_result

        # When
        result = UnitVersions().diff(other_obj)

        # Then
        self.assertEqual(result, expected_result)
        compare_mock.assert_called_once_with(other_obj)


class UnitChangesCleanTests(unittest.TestCase):
    """ Tests sucess cases for pata.models.UnitChanges model. """

    def test_fields(self):
        """ Tests database fields. """
        # Given
        expected_result = [
            "created_by",
            "created_at",
            "modified_by",
            "modified_at",
            "id",
            "unit_id",
            "day",
            "description",
            ]

        # When
        obj = UnitChanges()
        columns = [
            column.name
            for column in obj.metadata.tables["unit_changes"].columns
            ]

        # Then
        self.assertEqual(columns, expected_result)

    def test_repr(self):
        """ Tests string representation. """
        # Given
        change_id = 77
        day = "1984-10-31"
        unit_id = 99
        name = "unit name"
        expected_result = f"Change to {unit_id} - {name} for {day}"

        # When
        obj = UnitChanges(
            id=change_id, day=day, unit=Units(id=unit_id, name=name))

        # Then
        self.assertEqual(str(obj), expected_result)

    @patch("pata.models.units.UnitChanges.compare_models")
    def test_diff(self, compare_mock):
        """ Test call to comparison function. """
        # Given
        other_obj = UnitChanges()
        expected_result = {}

        compare_mock.return_value = expected_result

        # When
        result = UnitChanges().diff(other_obj)

        # Then
        self.assertEqual(result, expected_result)
        compare_mock.assert_called_once_with(other_obj)
