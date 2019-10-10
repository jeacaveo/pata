""" Tests for pata.migrate_units """
# pylint: disable=protected-access
import unittest
from json.decoder import JSONDecodeError

from mock import patch

from pata.migrate_units import (
    create_parser,
    load_version,
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
