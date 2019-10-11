""" Tests for pata.migrate_units """
# pylint: disable=protected-access
import unittest
from json.decoder import JSONDecodeError

from mock import patch

from pata.migrate_units import (
    create_parser,
    load_to_models,
    load_version,
    )
from pata.models.units import (
    UnitChanges, Units, UnitVersions,
    )


class ParserTests(unittest.TestCase):
    """  Tests for pata.migrate_units.create_parser """

    def test_defaults(self):
        """ Test state when no optional flags are sent. """
        # Given
        args = ["path/to/file"]

        # When
        result = create_parser(args)

        # Then
        self.assertEqual(len(result._get_kwargs()), 4)
        self.assertEqual(result.source, args[0])
        self.assertFalse(result.diff)
        self.assertFalse(result.insert)
        self.assertFalse(result.update)

    def test_optional(self):
        """ Test state when all optional flags are sent. """
        # Given
        args = ["path/to/file", "-d", "-i", "-u"]

        # When
        result = create_parser(args)

        # Then
        self.assertEqual(len(result._get_kwargs()), 4)
        self.assertEqual(result.source, args[0])
        self.assertTrue(result.diff)
        self.assertTrue(result.insert)
        self.assertTrue(result.update)


class LoadVersionTests(unittest.TestCase):
    """  Tests for pata.migrate_units.load_version """

    @patch("pata.migrate_units.os.path.isfile")
    def test_not_exist(self, isfile_mock):
        """ Test error message when file doesn't exist. """
        # Given
        file_path = "/path/to/file"
        expected_result = False, {"message": "File doesn't exist"}

        isfile_mock.return_value = False

        # When
        result = load_version(file_path)

        # Then
        self.assertEqual(result, expected_result)
        isfile_mock.assert_called_once_with(file_path)

    @patch("pata.migrate_units.json.loads")
    @patch("pata.migrate_units.os.path.isfile")
    def test_invalid_format(self, isfile_mock, json_mock):
        """ Test error message when file has invalid format. """
        # Given
        file_path = "/path/to/file"
        expected_result = False, {"message": "Invalid format"}

        isfile_mock.return_value = True
        json_mock.side_effect = JSONDecodeError("", "", 0)

        # When
        result = load_version(file_path)

        # Then
        self.assertEqual(result, expected_result)
        isfile_mock.assert_called_once_with(file_path)
        json_mock.assert_called_once_with(file_path)

    @patch("pata.migrate_units.json.loads")
    @patch("pata.migrate_units.os.path.isfile")
    def test_success(self, isfile_mock, json_mock):
        """ Test . """
        # Given
        file_path = "/path/to/file"
        expected_json = {"key": "val"}
        expected_result = True, expected_json

        isfile_mock.return_value = True
        json_mock.return_value = expected_json

        # When
        result = load_version(file_path)

        # Then
        self.assertEqual(result, expected_result)
        isfile_mock.assert_called_once_with(file_path)
        json_mock.assert_called_once_with(file_path)


class LoadToModelsTests(unittest.TestCase):
    """  Tests for pata.migrate_units.load_to_models """

    def test_empty(self):
        """ Test result when no data is available. """
        # Given
        data = {}
        expected_result = {}

        # When
        result = load_to_models(data)

        # Then
        self.assertEqual(result, expected_result)

    def test_data(self):
        """ Test result when data is available. """
        # Given
        data = {
            "unit1": {
                "name": "unit1",
                "position": "Top",
                "type": 4,
                "unit_spell": "Unit",
                "abilities": "ability X",
                "attributes": {
                    "blocker": False,
                    "fragile": True,
                    "frontline": False,
                    "prompt": True,
                    "build_time": 0,
                    "exhaust_ability": 1,
                    "exhaust_turn": 0,
                    "lifespan": 1,
                    "stamina": 0,
                    "supply": 1,
                    },
                "change_history": {
                    "2000-01-01": ["Change 1", "Change 2"],
                    },
                "costs": {
                    "blue": 3,
                    "energy": 0,
                    "gold": 13,
                    "green": 0,
                    "red": 0,
                    },
                "links": {
                    "image": "image X",
                    "panel": "panel X",
                    "path": "path X",
                    },
                "stats": {
                    "attack": 1,
                    "health": 1,
                    },
                },
            "unit2": {
                "name": "unit2",
                "position": "Bottom",
                "type": 1,
                "unit_spell": "Spell",
                "abilities": "ability Y",
                "attributes": {
                    "blocker": True,
                    "fragile": False,
                    "frontline": True,
                    "prompt": False,
                    "build_time": 1,
                    "exhaust_ability": 0,
                    "exhaust_turn": 1,
                    "lifespan": 0,
                    "stamina": 1,
                    "supply": 0,
                    },
                "change_history": {
                    "2000-02-02": ["Change 3", "Change 4"],
                    },
                "costs": {
                    "blue": 2,
                    "energy": 1,
                    "gold": 3,
                    "green": 1,
                    "red": 1,
                    },
                "links": {
                    "image": "image Y",
                    "panel": "panel Y",
                    "path": "path Y",
                    },
                "stats": {
                    "attack": 2,
                    "health": 2,
                    },
                },
            }
        unit1 = Units(
            name="unit1",
            wiki_path="path X",
            image_url="image X",
            panel_url="panel X",
            )
        unit2 = Units(
            name="unit2",
            wiki_path="path Y",
            image_url="image Y",
            panel_url="panel Y",
            )
        expected_result = {
            "unit1": {
                "unit": unit1,
                "unit_version": UnitVersions(
                    unit=unit1,
                    attack=1,
                    health=1,
                    gold=13,
                    green=0,
                    blue=3,
                    red=0,
                    energy=0,
                    supply=1,
                    unit_spell="Unit",
                    frontline=False,
                    fragile=True,
                    blocker=False,
                    prompt=True,
                    stamina=0,
                    lifespan=1,
                    build_time=0,
                    exhaust_turn=0,
                    exhaust_ability=1,
                    position="Top",
                    abilities="ability X",
                    ),
                "unit_changes": [
                    UnitChanges(
                        unit=unit1, day="2000-01-01", description="Change 1"),
                    UnitChanges(
                        unit=unit1, day="2000-01-01", description="Change 2"),
                    ]
                },
            "unit2": {
                "unit": unit2,
                "unit_version": UnitVersions(
                    unit=unit2,
                    attack=2,
                    health=2,
                    gold=3,
                    green=1,
                    blue=2,
                    red=1,
                    energy=1,
                    supply=0,
                    unit_spell="Spell",
                    frontline=True,
                    fragile=False,
                    blocker=True,
                    prompt=False,
                    stamina=1,
                    lifespan=0,
                    build_time=1,
                    exhaust_turn=1,
                    exhaust_ability=0,
                    position="Bottom",
                    abilities="ability Y",
                    ),
                "unit_changes": [
                    UnitChanges(
                        unit=unit2, day="2000-02-02", description="Change 3"),
                    UnitChanges(
                        unit=unit2, day="2000-02-02", description="Change 4"),
                    ]
                },
            }

        # When
        result = load_to_models(data)

        # Then
        self.assertEqual(
            result["unit1"]["unit"].diff(
                expected_result["unit1"]["unit"]),
            {})
        self.assertEqual(
            result["unit1"]["unit_version"].diff(
                expected_result["unit1"]["unit_version"]),
            {})
        self.assertEqual(
            result["unit1"]["unit_changes"][0].diff(
                expected_result["unit1"]["unit_changes"][0]),
            {})
        self.assertEqual(
            result["unit1"]["unit_changes"][1].diff(
                expected_result["unit1"]["unit_changes"][1]),
            {})
        self.assertEqual(
            result["unit2"]["unit"].diff(
                expected_result["unit2"]["unit"]),
            {})
        self.assertEqual(
            result["unit2"]["unit_version"].diff(
                expected_result["unit2"]["unit_version"]),
            {})
        self.assertEqual(
            result["unit2"]["unit_changes"][0].diff(
                expected_result["unit2"]["unit_changes"][0]),
            {})
        self.assertEqual(
            result["unit2"]["unit_changes"][1].diff(
                expected_result["unit2"]["unit_changes"][1]),
            {})
