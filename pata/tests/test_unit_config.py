""" Unit tests for pata.config """
import unittest

from pata.config import get_database_url


class DatabaseUrlTests(unittest.TestCase):
    """ Tests success case for pata.config.get_database_url """

    def test_config(self):
        """ Test different database configurations based on data provided. """
        # Given
        data = {
            "missing_required": {
                "config": {},
                "expected_url": "",
                },
            "no_optionals": {
                "config": {
                    "engine": "tengine",
                    },
                "expected_url": "tengine://",
                },
            "all_optionals": {
                "config": {
                    "engine": "tengine",
                    "driver": "tdriver",
                    "username": "tusername",
                    "password": "tpassword",
                    "host": "thost",
                    "port": "tport",
                    "database": "tdatabase",
                    },
                "expected_url":
                "tengine+tdriver://tusername:tpassword@thost:tport/tdatabase",
                },
            }

        # When/Then
        for name, params in data.items():
            with self.subTest(name):
                result = get_database_url(params["config"])
                self.assertEqual(result, params["expected_url"])
