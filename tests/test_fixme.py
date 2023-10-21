
import tempfile
import unittest

from fixme.__main__ import App


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
        with tempfile.TemporaryDirectory() as t_dir:
            pass
