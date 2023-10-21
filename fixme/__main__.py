from abc import abstractmethod
import argparse
import json
import logging
import os
import re
import sys
import textwrap
import yaml


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


#region Command line parsing  # noqa


def duration_in_seconds(time_str: str):
    '''
    Parse a time string with format <minutes>m<seconds>s and return the total number of seconds
    '''
    pattern = r'^(\d+m)?(\d+s)?$'
    match = re.match(pattern, time_str)
    if not match:
        raise ValueError(f'Invalid time string "{time_str}"')
    minutes_str, seconds_str = match.groups()
    minutes = int(minutes_str[:-1]) if minutes_str else 0
    seconds = int(seconds_str[:-1]) if seconds_str else 0
    return minutes * 60 + seconds


class ColorLogFormatter(logging.Formatter):
    '''
    Custom formatter that changes the color of logs based on the log level.
    '''

    grey = "\x1b[38;20m"
    green = "\u001b[32m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    blue = "\u001b[34m"
    cyan = "\u001b[36m"
    reset = "\x1b[0m"

    timestamp = '%(asctime)s - '
    loglevel = '%(levelname)s'
    message = ' - %(message)s'

    FORMATS = {
        logging.DEBUG:    timestamp + blue + loglevel + reset + message,
        logging.INFO:     timestamp + green + loglevel + reset + message,
        logging.WARNING:  timestamp + yellow + loglevel + reset + message,
        logging.ERROR:    timestamp + red + loglevel + reset + message,
        logging.CRITICAL: timestamp + bold_red + loglevel + reset + message
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def _init_logger(level=logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(level)

    formatter = ColorLogFormatter()
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)


class RawTextArgumentDefaultsHelpFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter):
    pass


class Handler:
    '''
    An interface for the [Chain of Responsibility](https://refactoring.guru/design-patterns/chain-of-responsibility/python/example) design pattern.
    '''  # noqa

    def __init__(self, next_handler=None):
        self._next_handler = next_handler

    @abstractmethod
    def handle_request(self, key):
        raise NotImplementedError

    def get_from_next_handler(self, key):
        if self._next_handler:
            return self._next_handler.handle_request(key)
        return None


class DefaultHandler(Handler):
    def __init__(self, default_value, next_handler=None):
        super().__init__(next_handler)
        self.default_value = default_value

    def handle_request(self, key):
        return self.default_value


class ArgHandler(Handler):
    def __init__(self, args, next_handler=None):
        super().__init__(next_handler)
        self.args = args

    def handle_request(self, key):
        if key in self.args:
            return getattr(self.args, key, None)
        return self.get_from_next_handler(key)


class EnvHandler(Handler):
    def __init__(self, next_handler=None):
        super().__init__(next_handler)

    def handle_request(self, key):
        if key in os.environ:
            return os.environ.get(key)
        return self.get_from_next_handler(key)


class DictHandler(Handler):
    def __init__(self, data_dict={}, config_path=None, next_handler=None):
        super().__init__(next_handler)
        self.config_path = config_path
        self.data_dict = data_dict
        if self.config_path:
            with open(config_path, 'r') as config_file:
                yaml_data = yaml.safe_load(config_file)
                self.data_dict = {**self.data_dict, **yaml_data}

    def handle_request(self, key):
        if key in self.data_dict:
            return self.data_dict[key]
        return self.get_from_next_handler(key)


class FileHandler(Handler):
    def __init__(self, file_path: str, mount_hook=None, next_handler=None):
        super().__init__(next_handler)
        self.file_path = file_path
        self.mount_hook = mount_hook

    def handle_request(self, key):
        if self.mount_hook:
            # Attempt to mount file system if file does not exist.
            if not os.path.exists(self.file_path):
                self.mount_hook()
        if os.path.exists(self.file_path):
            with open(self.file_path) as file:
                return file.read()
        return self.get_from_next_handler(key)


class JSONFileHandler(FileHandler):
    def __init__(self, file_path: str, mount_hook=None, next_handler=None):
        super().__init__(file_path, mount_hook, next_handler)

    def handle_request(self, key):
        file_data = super().handle_request(key)
        if file_data:
            json_data = json.loads(file_data)
            if key in json_data:
                return json_data[key]
        return self.get_from_next_handler(key)


def fixme1(args):
    default_config = {
        'FIXME_NAME': 'fixme'
    }
    name_handler = ArgHandler(args, EnvHandler(DictHandler(default_config)))
    name = name_handler.handle_request('FIXME_NAME')
    logging.debug(f'FIXME_NAME={name}')


def fixme2(args):
    name_handler = ArgHandler(args, EnvHandler(DefaultHandler('fixme')))
    name = name_handler.handle_request('FIXME_NAME')
    logging.debug(f'FIXME_NAME={name}')
    print(f'Duration is {args.duration} seconds')


class SecondsDurationAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, duration_in_seconds(values))


class App:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(
            description=textwrap.dedent('''\
                FIXME
                '''),
            formatter_class=RawTextArgumentDefaultsHelpFormatter)

        self.parser.add_argument('-v', '--verbosity',
                                 choices=['critical', 'error', 'warning', 'info', 'debug'],
                                 default='info',
                                 help='Set the logging verbosity level.')
        self.parser.add_argument('-c', '--config',
                                 help='A configuration file.')

        self.subparsers = self.parser.add_subparsers(dest='command')
        fixme1_parser = self.subparsers.add_parser('fixme1',
                                                   help='FIXME 1',
                                                   formatter_class=RawTextArgumentDefaultsHelpFormatter)
        fixme1_parser.add_argument('--dry-run',
                                   action='store_true',
                                   help='See what would happen without doing anything')
        fixme1_parser.set_defaults(func=fixme1)
        fixme2_parser = self.subparsers.add_parser('fixme2',
                                                   help='FIXME 2',
                                                   formatter_class=RawTextArgumentDefaultsHelpFormatter)
        fixme2_parser.add_argument('--duration',
                                   action=SecondsDurationAction,
                                   help='The duration to do something, for example 1m30s.')
        fixme2_parser.set_defaults(func=fixme2)

    def run(self):
        args = self.parser.parse_args()
        _init_logger(getattr(logging, args.verbosity.upper()))
        logging.debug(f'command-line args: {args}')
        args.func(args)


#endregion Command line parsing  # noqa


if __name__ == "__main__":
    app = App()
    app.run()
