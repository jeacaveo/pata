""" Test for pata.models module. """
import unittest

from pata.models.units import (
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
