
import argparse
import os
import tempfile
import textwrap
import unittest
from unittest import mock

from fixme.cli import ArgHandler, DefaultHandler, DictHandler, EnvHandler, FileHandler, Handler, JSONFileHandler, SecondsDurationAction


class NoNextHandlerError(Exception):
    def __init__(self, *args: object):
        super().__init__(*args)


class NoNextHandler(Handler):
    '''Exists for testing purposes, for chain of responsibility feature of Handlers.'''

    def handle_request(self, key):
        raise NoNextHandlerError('No next handler')


class DefaultHandlerTestCase(unittest.TestCase):

    def test_with_key_returns_hardcoded_value(self):
        handler = DefaultHandler(default_value='hi there')
        self.assertEqual('hi there', handler.handle_request(None))

    def test_next_handler_not_called(self):
        handler = DefaultHandler(default_value=None, next_handler=NoNextHandler())
        try:
            handler.handle_request(None)
        except NoNextHandlerError:
            self.fail('DefaultHandler.handle_request() raised NoNextHandlerError unexpectedly!')


class ArgHandlerTestCase(unittest.TestCase):

    def setUp(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-v', '--verbosity',
                                 choices=['critical', 'error', 'warning', 'info', 'debug'],
                                 default='info',
                                 help='Set the logging verbosity level.')

    def test_specifying_key_returns_default_argument_value(self):
        self.handler = ArgHandler(self.parser.parse_args())
        self.assertEqual('info', self.handler.handle_request('verbosity'))

    def test_specifying_key_returns_commandline_argument_value(self):
        self.handler = ArgHandler(self.parser.parse_args(['--verbosity', 'error']))
        self.assertEqual('error', self.handler.handle_request('verbosity'))

    def test_next_handler_called(self):
        handler = ArgHandler(self.parser.parse_args(), next_handler=NoNextHandler())
        with self.assertRaises(NoNextHandlerError):
            handler.handle_request('does-not-exist')


class EnvHandlerTestCase(unittest.TestCase):

    @mock.patch.dict(os.environ, {'APP_VERBOSITY': 'warning'})
    def test_specifying_key_returns_environment_variable_value(self):
        handler = EnvHandler()
        self.assertEqual('warning', handler.handle_request('APP_VERBOSITY'))

    def test_next_handler_called(self):
        handler = EnvHandler(next_handler=NoNextHandler())
        with self.assertRaises(NoNextHandlerError):
            handler.handle_request('does-not-exist')


class DictHandlerTestCase(unittest.TestCase):

    def test_with_in_memory_dict_specifying_key_returns_key_value(self):
        handler = DictHandler(data_dict={'APP_VERBOSITY': 'critical'})
        self.assertEqual('critical', handler.handle_request('APP_VERBOSITY'))

    def test_with_yaml_file_specifying_key_returns_key_value(self):
        with tempfile.TemporaryDirectory() as tempdir:
            file_path = os.path.join(tempdir, 'myconfig.yaml')
            with open(file_path, 'w+') as f:
                f.write(textwrap.dedent('''\
                        ---
                        APP_VERBOSITY: 'critical'
                        '''))
            handler = DictHandler(file_path=file_path)
            self.assertEqual('critical', handler.handle_request('APP_VERBOSITY'))

    def test_next_handler_called(self):
        handler = DictHandler(next_handler=NoNextHandler())
        with self.assertRaises(NoNextHandlerError):
            handler.handle_request('does-not-exist')


class FileHandlerTestCase(unittest.TestCase):

    def test_with_json_file_specifying_key_returns_key_value(self):
        with tempfile.TemporaryDirectory() as tempdir:
            file_path = os.path.join(tempdir, 'verbosity.txt')
            with open(file_path, 'w+') as f:
                f.write('myvalue')
            handler = FileHandler(file_path)
            self.assertEqual('myvalue', handler.handle_request(None))

    def test_next_handler_called(self):
        handler = FileHandler(file_path='', next_handler=NoNextHandler())
        with self.assertRaises(NoNextHandlerError):
            handler.handle_request('does-not-exist')


class JSONFileHandlerTestCase(unittest.TestCase):

    def test_with_json_file_specifying_key_returns_key_value(self):
        with tempfile.TemporaryDirectory() as tempdir:
            file_path = os.path.join(tempdir, 'myconfig.json')
            with open(file_path, 'w+') as f:
                f.write(textwrap.dedent('''\
                        {
                            "APP_VERBOSITY": "something"
                        }'''))
            handler = JSONFileHandler(file_path)
            self.assertEqual('something', handler.handle_request('APP_VERBOSITY'))

    def test_next_handler_called(self):
        handler = JSONFileHandler(file_path='', next_handler=NoNextHandler())
        with self.assertRaises(NoNextHandlerError):
            handler.handle_request('does-not-exist')


class SecondsDurationActionTestCase(unittest.TestCase):

    def setUp(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--duration',
                                 action=SecondsDurationAction,
                                 help='The duration to do something, for example 1m30s.')

    def test_seconds(self):
        self.assertEqual(47, self.parser.parse_args(['--duration', '47s']).duration)

    def test_minutes(self):
        self.assertEqual(60, self.parser.parse_args(['--duration', '1m']).duration)

    def test_seconds_then_minutes(self):
        self.assertEqual(123, self.parser.parse_args(['--duration', '3s2m']).duration)

    def test_minutes_then_seconds(self):
        self.assertEqual(123, self.parser.parse_args(['--duration', '2m3s']).duration)
