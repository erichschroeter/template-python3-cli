
import tempfile
import unittest


class FixmeTestCase(unittest.TestCase):
    def test_fixme(self):
        pass

    def test_fixme_with_temporary_directory(self):
        with tempfile.TemporaryDirectory() as t_dir:
            pass
