""" Test for pata.models module. """
import unittest

from pata.models.units import (
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
        unit_obj = Units()
        columns = [
            column.name
            for column in unit_obj.metadata.tables["users"].columns
            ]

        # Then
        self.assertEqual(columns, expected_result)
