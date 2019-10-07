""" Test for pata.models module. """
import unittest

from datetime import datetime

from pata.models.units import (
    UnitChanges,
    UnitVersions,
    Units,
    )


class UnitsTests(unittest.TestCase):
    """ Tests for pata.models.Units model. """

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

    def test_diff_same(self):
        """ Test no difference with another object. """
        # Given
        other_obj = Units()
        expected_result = {}

        # When
        result = Units().diff(other_obj)

        # Then
        self.assertEqual(result, expected_result)

    def test_diff(self):
        """ Test difference with another object. """
        # Given
        other_obj = Units(image_url="new image", panel_url="new panel")
        expected_result = {
            "image_url": {
                "old": "old image", "new": "new image"},
            "panel_url": {
                "old": "old panel", "new": "new panel"},
            }

        # When
        result = Units(
            id=1,
            image_url="old image",
            panel_url="old panel",
            created_by="",
            created_at=datetime.now(),
            modified_by="",
            modified_at=datetime.now(),
            ).diff(other_obj)

        # Then
        self.assertEqual(result, expected_result)


class UnitVersionsTests(unittest.TestCase):
    """ Tests for pata.models.UnitVersions model. """

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


class UnitChangesTests(unittest.TestCase):
    """ Tests for pata.models.UnitChanges model. """

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
