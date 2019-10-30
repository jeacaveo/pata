""" Tests for pata.migrate_units """
# pylint: disable=protected-access
import unittest

from datetime import date
from json.decoder import JSONDecodeError

from mock import (
    call,
    MagicMock,
    Mock,
    patch,
    )
from sqlalchemy.exc import SQLAlchemyError

from pata.migrate_units import (
    create_parser,
    load_to_models,
    load_version,
    models_diff,
    process_transaction,
    run,
    run_command,
    )
from pata.models.units import (
    UnitChanges, Units, UnitVersions,
    )


class ParserCleanTests(unittest.TestCase):
    """ Tests success case for pata.migrate_units.create_parser """

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


class LoadVersionDirtyTests(unittest.TestCase):
    """ Tests fail cases for pata.migrate_units.load_version """

    @patch("pata.migrate_units.os.path.isfile")
    def test_not_exist(self, isfile_mock):
        """ Test fail message when file doesn't exist. """
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
    @patch("builtins.open")
    @patch("pata.migrate_units.os.path.isfile")
    def test_invalid_format(self, isfile_mock, open_mock, json_mock):
        """ Test fail message when file has invalid format. """
        # Given
        file_path = "/path/to/file"
        file_mock = MagicMock()
        file_content = MagicMock()
        expected_result = False, {"message": "Invalid format"}

        isfile_mock.return_value = True
        open_mock.return_value = open_mock
        open_mock.__enter__.return_value = file_mock
        file_mock.read.return_value = file_content
        json_mock.side_effect = JSONDecodeError("", "", 0)

        # When
        result = load_version(file_path)

        # Then
        self.assertEqual(result, expected_result)
        isfile_mock.assert_called_once_with(file_path)
        open_mock.assert_has_calls([
            call(file_path, "r"),
            call.__enter__(),
            call.__enter__().read(),
            call.__exit__(None, None, None),
            ])
        json_mock.assert_called_once_with(file_content)


class LoadVersionCleanTests(unittest.TestCase):
    """ Tests success case for pata.migrate_units.load_verson """

    @patch("pata.migrate_units.json.loads")
    @patch("builtins.open")
    @patch("pata.migrate_units.os.path.isfile")
    def test_success(self, isfile_mock, open_mock, json_mock):
        """ Test . """
        # Given
        file_path = "/path/to/file"
        file_mock = MagicMock()
        file_content = MagicMock()
        expected_json = {"key": "val"}
        expected_result = True, expected_json

        isfile_mock.return_value = True
        open_mock.return_value = open_mock
        open_mock.__enter__.return_value = file_mock
        file_mock.read.return_value = file_content
        json_mock.return_value = expected_json

        # When
        result = load_version(file_path)

        # Then
        self.assertEqual(result, expected_result)
        isfile_mock.assert_called_once_with(file_path)
        open_mock.assert_has_calls([
            call(file_path, "r"),
            call.__enter__(),
            call.__enter__().read(),
            call.__exit__(None, None, None),
            ])
        json_mock.assert_called_once_with(file_content)


class LoadToModelsCleanTests(unittest.TestCase):
    """  Tests success cases for pata.migrate_units.load_to_models """

    def test_empty(self):
        """ Test result when no data is available. """
        # Given
        data = {}

        # When
        result = load_to_models(data)

        # Then
        self.assertEqual(result.name, None)
        self.assertEqual(result.versions[0].unit.name, None)
        self.assertEqual(result.changes, [])

    def test_data(self):
        """ Test result when data is available. """
        # Given
        data = {
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
            }
        unit = Units(
            name="unit1",
            wiki_path="path X",
            image_url="image X",
            panel_url="panel X",
            )
        UnitVersions(
            unit=unit,
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
            )
        UnitChanges(
            unit=unit,
            day=date.fromisoformat("2000-01-01"),
            description="Change 1")
        UnitChanges(
            unit=unit,
            day=date.fromisoformat("2000-01-01"),
            description="Change 2")
        expected_result = unit

        # When
        result = load_to_models(data)

        # Then
        self.assertEqual(result.diff(expected_result), {})
        self.assertEqual(
            result.versions[0].diff(expected_result.versions[0]), {})
        self.assertEqual(
            result.changes[0].diff(expected_result.changes[0]), {})
        self.assertEqual(
            result.changes[1].diff(expected_result.changes[1]), {})


class ModelsDiffCleanTests(unittest.TestCase):
    """ Tests success cases for pata.migrate_units.models_diff """

    def test_no_changes(self):
        """ Test result when models are the same. """
        # Given
        base_unit = MagicMock()
        unit = MagicMock(
            versions=[],
            changes=[]
            )
        expected_result = {}

        # When
        result = models_diff(base_unit, unit)

        # Then
        self.assertEqual(result, expected_result)

    def test_unit_only(self):
        """ Test result when only changes in Units model. """
        # Given
        base_unit = MagicMock()
        unit = MagicMock(
            versions=[MagicMock()],
            changes=[],
            )
        expected_result = {"column1": "change1"}

        base_unit.diff.return_value = expected_result

        # When
        result = models_diff(base_unit, unit)

        # Then
        self.assertEqual(result, expected_result)
        base_unit.diff.assert_called_once_with(unit)

    def test_unit_version_only(self):
        """ Test result when only changes in Units and UnitVersions models. """
        # Given
        base_version = MagicMock()
        base_unit = MagicMock(versions=[base_version])
        unit = MagicMock(
            versions=[MagicMock()],
            changes=[],
            )
        expected_result = {
            "column1": "change1",
            "column2": "change2",
            }

        base_unit.diff.return_value = {"column1": "change1"}
        base_version.diff.return_value = {"column2": "change2"}

        # When
        result = models_diff(base_unit, unit)

        # Then
        self.assertEqual(result, expected_result)
        base_unit.diff.assert_called_once_with(unit)
        base_version.diff.assert_called_once_with(unit.versions[0])

    def test_all(self):
        """
        Test result with changes in Units, UnitVersions and UnitChanges models.

        """
        # Given
        base_change1 = MagicMock(day="day1")
        base_change2 = MagicMock(day="day2")
        base_version = MagicMock()
        base_unit = MagicMock(
            versions=[base_version],
            changes=[base_change1, base_change2],
            )
        unit = MagicMock(
            versions=[MagicMock()],
            changes=[MagicMock(day="day1"), MagicMock(day="day2")]
            )
        expected_result = {
            "column1": "change1",
            "column2": "change2",
            unit.changes[0].day: {"column3": "change3"},
            unit.changes[1].day: {"column4": "change4"},
            }

        base_unit.diff.return_value = {"column1": "change1"}
        base_version.diff.return_value = {"column2": "change2"}
        base_change1.diff.return_value = {"column3": "change3"}
        base_change2.diff.return_value = {"column4": "change4"}

        # When
        result = models_diff(base_unit, unit)

        # Then
        self.assertEqual(result, expected_result)
        base_unit.diff.assert_called_once_with(unit)
        base_version.diff.assert_called_once_with(unit.versions[0])
        base_change1.diff.assert_called_once_with(unit.changes[0])
        base_change2.diff.assert_called_once_with(unit.changes[1])


class ProcessTransactionCleanTests(unittest.TestCase):
    """ Tests success cases for pata.migrate_units.process_transaction """

    def test_insert_diff(self):
        """ Test result when models doesn't exist. """
        # Given
        session = MagicMock()
        unit = Mock(
            versions=[MagicMock()],
            changes=[]
            )
        unit.configure_mock(name="unit name")
        expected_result = {"insert": {}}

        session.query.return_value = session
        session.filter_by.return_value = session
        session.first.return_value = None

        # When
        result = process_transaction(session, unit)

        # Then
        self.assertEqual(result, expected_result)
        session.assert_has_calls([
            call.query(Units),
            call.filter_by(name=unit.name),
            call.first(),
            ])

    @patch("pata.migrate_units.models_diff")
    def test_no_change(self, diff_mock):
        """ Test result when models exists but no changes exist. """
        # Given
        session = MagicMock()
        unit = Mock(
            versions=[MagicMock()],
            changes=[]
            )
        unit.configure_mock(name="unit name")
        existing = MagicMock()
        expected_result = {"nochange": {}}

        session.query.return_value = session
        session.filter_by.return_value = session
        session.first.return_value = existing
        diff_mock.return_value = {}

        # When
        result = process_transaction(session, unit)

        # Then
        self.assertEqual(result, expected_result)
        session.assert_has_calls([
            call.query(Units),
            call.filter_by(name=unit.name),
            call.first(),
            ])
        diff_mock.assert_called_once_with(existing, unit)

    @patch("pata.migrate_units.models_diff")
    def test_update_diff(self, diff_mock):
        """ Test result when models exists but no changes exist. """
        # Given
        session = MagicMock()
        unit = Mock()
        unit = Mock(
            versions=[MagicMock()],
            changes=[]
            )
        unit.configure_mock(name="unit name")
        existing = MagicMock()
        expected_result = {"update": {"key": "val"}}

        session.query.return_value = session
        session.filter_by.return_value = session
        session.first.return_value = existing
        diff_mock.return_value = expected_result.get("update")

        # When
        result = process_transaction(session, unit)

        # Then
        self.assertEqual(result, expected_result)
        session.assert_has_calls([
            call.query(Units),
            call.filter_by(name=unit.name),
            call.first(),
            ])
        diff_mock.assert_called_once_with(existing, unit)

    def test_insert(self):
        """ Test result when models doesn't exist. """
        # Given
        session = MagicMock()
        unit = Mock(
            versions=[MagicMock()],
            changes=[]
            )
        unit.configure_mock(name="unit name")
        expected_result = {"insert": {}}

        session.query.return_value = session
        session.filter_by.return_value = session
        session.first.return_value = None

        # When
        result = process_transaction(session, unit, insert=True)

        # Then
        self.assertEqual(result, expected_result)
        session.assert_has_calls([
            call.query(Units),
            call.filter_by(name=unit.name),
            call.first(),
            call.add(unit),
            ])

    @patch("pata.migrate_units.models_diff")
    def test_update(self, diff_mock):
        """ Test result when models exists but no changes exist. """
        # Given
        session = MagicMock()
        unit = Mock()
        unit = Mock(
            versions=[MagicMock()],
            changes=[]
            )
        unit.configure_mock(name="unit name")
        existing = MagicMock()
        expected_result = {"update": {"key": "val"}}

        session.query.return_value = session
        session.filter_by.return_value = session
        session.first.return_value = existing
        diff_mock.return_value = expected_result.get("update")

        # When
        result = process_transaction(session, unit, update=True)

        # Then
        self.assertEqual(result, expected_result)
        session.assert_has_calls([
            call.query(Units),
            call.filter_by(name=unit.name),
            call.first(),
            call.first().__bool__(),
            call.add(unit),
            ])
        diff_mock.assert_called_once_with(existing, unit)


class RunDirtyTests(unittest.TestCase):
    """ Tests fail cases for pata.migrate_units.run """

    @patch("pata.migrate_units.load_to_models")
    @patch("pata.migrate_units.sessionmaker")
    @patch("pata.migrate_units.create_engine")
    def test_rollback(self, engine_mock, make_session_mock, model_mock):
        """
        Test result when when exception is raised.

        The side effect class must be first one inside the try/except block.

        """
        # Given
        data = {"key1": "val1"}
        engine = MagicMock()
        session = MagicMock()
        expected_result = {"error": {"message": "()\nDB error. Rolling back."}}

        engine_mock.return_value = engine
        make_session_mock.return_value = session
        model_mock.side_effect = SQLAlchemyError()

        # When
        result = run(data)

        # Then
        self.assertEqual(result, expected_result)
        engine_mock.assert_called_once_with("sqlite:///pata.sqlite")
        make_session_mock.assert_called_once_with(bind=engine)
        session.assert_has_calls([
            call(),
            call().rollback(),
            call().close(),
            ])


class RunCleanTests(unittest.TestCase):
    """ Tests success cases for pata.migrate_units.run """

    @patch("pata.migrate_units.sessionmaker")
    @patch("pata.migrate_units.create_engine")
    def test_empty(self, engine_mock, make_session_mock):
        """ Test result when data is empty. """
        # Given
        data = {}
        engine = MagicMock()
        session = MagicMock()
        expected_result = {}

        engine_mock.return_value = engine
        make_session_mock.return_value = session

        # When
        result = run(data)

        # Then
        self.assertEqual(result, expected_result)
        engine_mock.assert_called_once_with("sqlite:///pata.sqlite")
        make_session_mock.assert_called_once_with(bind=engine)
        session.assert_has_calls([
            call(),
            call().close(),
            ])

    @patch("pata.migrate_units.process_transaction")
    @patch("pata.migrate_units.load_to_models")
    @patch("pata.migrate_units.sessionmaker")
    @patch("pata.migrate_units.create_engine")
    def test_diff(
            self, engine_mock, make_session_mock, model_mock, process_mock):
        """ Test result when no insert or update. """
        # Given
        data = {
            "key1": "val1",
            "key2": "val2",
            }
        engine = MagicMock()
        session = MagicMock()
        unit1 = MagicMock()
        unit2 = MagicMock()
        expected_result = {
            "key1": {"nochange": {}},
            "key2": {"nochange": {}},
            }

        engine_mock.return_value = engine
        make_session_mock.return_value = session
        model_mock.side_effect = [unit1, unit2]
        process_mock.side_effect = [{"nochange": {}}, {"nochange": {}}]

        # When
        result = run(data)

        # Then
        self.assertEqual(result, expected_result)
        engine_mock.assert_called_once_with("sqlite:///pata.sqlite")
        make_session_mock.assert_called_once_with(bind=engine)
        session.assert_has_calls([
            call(),
            call().close(),
            ])
        model_mock.assert_has_calls([
            call("val1"),
            call("val2"),
            ])
        process_mock.assert_has_calls([
            call(session(), unit1, False, False),
            call(session(), unit2, False, False),
            ])

    @patch("pata.migrate_units.process_transaction")
    @patch("pata.migrate_units.load_to_models")
    @patch("pata.migrate_units.sessionmaker")
    @patch("pata.migrate_units.create_engine")
    def test_changes(
            self, engine_mock, make_session_mock, model_mock, process_mock):
        """ Test result when insert or update are required. """
        # Given
        data = {
            "key1": "val1",
            "key2": "val2",
            }
        engine = MagicMock()
        session = MagicMock()
        unit1 = MagicMock()
        unit2 = MagicMock()
        expected_result = {
            "key1": {"insert": {}},
            "key2": {"update": {}},
            }

        engine_mock.return_value = engine
        make_session_mock.return_value = session
        model_mock.side_effect = [unit1, unit2]
        process_mock.side_effect = [{"insert": {}}, {"update": {}}]

        # When
        result = run(data, True, True)

        # Then
        self.assertEqual(result, expected_result)
        engine_mock.assert_called_once_with("sqlite:///pata.sqlite")
        make_session_mock.assert_called_once_with(bind=engine)
        session.assert_has_calls([
            call(),
            call().commit(),
            call().close(),
            ])
        model_mock.assert_has_calls([
            call("val1"),
            call("val2"),
            ])
        process_mock.assert_has_calls([
            call(session(), unit1, True, True),
            call(session(), unit2, True, True),
            ])


class RunCommandDirtyTests(unittest.TestCase):
    """ Tests fail cases for pata.migrate_units.run_command """

    @patch("pata.migrate_units.load_version")
    def test_invalid(self, version_mock):
        """ Test error when loading version. """
        # Given
        path = "/path/to/file"
        expected_result = {"message": "error message"}

        version_mock.return_value = False, expected_result

        # When
        result = run_command(path)

        # Then
        self.assertEqual(result, expected_result)
        version_mock.assert_called_once_with(path)


class RunCommandCleanTests(unittest.TestCase):
    """ Tests success cases for pata.migrate_units.run_command """

    @patch("pata.migrate_units.run")
    @patch("pata.migrate_units.load_version")
    def test_no_diff(self, version_mock, run_mock):
        """ Test when diff param is not passed. """
        # Given
        path = "/path/to/file"
        data = MagicMock()
        expected_result = {}

        version_mock.return_value = True, data
        run_mock.return_value = MagicMock()

        # When
        result = run_command(path)

        # Then
        self.assertEqual(result, expected_result)
        version_mock.assert_called_once_with(path)
        run_mock.assert_called_once_with(data, insert=False, update=False)

    @patch("pata.migrate_units.run")
    @patch("pata.migrate_units.load_version")
    def test_diff(self, version_mock, run_mock):
        """ Test when diff param is passed. """
        # Given
        path = "/path/to/file"
        data = MagicMock()
        diff = MagicMock()
        expected_result = diff

        version_mock.return_value = True, data
        run_mock.return_value = diff

        # When
        result = run_command(path, True, True, True)

        # Then
        self.assertEqual(result, expected_result)
        version_mock.assert_called_once_with(path)
        run_mock.assert_called_once_with(data, insert=True, update=True)
