
import tempfile
import textwrap
import unittest

from contextlib import redirect_stdout
from dataclasses import dataclass
from fixme.__main__ import App, print_table
from io import StringIO


class Fixme1TestCase(unittest.TestCase):
    def setUp(self):
        self.app = App()

    def test_fixme1_dry_run_assigned_false_by_default(self):
        self.app.parse_args(['fixme1'])
        self.assertFalse(self.app.args.dry_run)

    def test_fixme1_dry_run_assigned_true(self):
        self.app.parse_args(['fixme1', '--dry-run'])
        self.assertTrue(self.app.args.dry_run)


class Fixme2TestCase(unittest.TestCase):
    def setUp(self):
        self.app = App()

    def test_fixme2_duration_assigned_None_by_default(self):
        self.app.parse_args(['fixme2'])
        self.assertEqual(self.app.args.duration, None)

    def test_fixme2_duration_assigned_value_in_seconds(self):
        self.app.parse_args(['fixme2', '--duration', '1m9s'])
        self.assertEqual(self.app.args.duration, 69)

    def test_fixme_with_temporary_directory(self):
        with tempfile.TemporaryDirectory() as t_dir:  # noqa
            pass


@dataclass
class User:
    first_name: str
    last_name: str
    age: int

    @classmethod
    def columns(cls):
        return [a for a in dir(User('', '', 0)) if not a.startswith('__') and not a == 'columns']


class TableTestCase(unittest.TestCase):
    def setUp(self):
        self.data = [
            User('John', 'Smith', 19),
            User('Jane', 'Doe', 18),
        ]

    def test_all_columns(self):
        actual = StringIO()
        with redirect_stdout(actual):
            print_table(self.data, User.columns())
            expected = textwrap.dedent('''\
                                       age first_name last_name 
                                       --- ---------- --------- 
                                       19  John       Smith     
                                       18  Jane       Doe       \n''')  # noqa
            actual = textwrap.dedent(actual.getvalue())
            self.assertEqual(expected.splitlines(), actual.splitlines())
