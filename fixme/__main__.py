import argparse
import logging
import re
import sys
import textwrap

from fixme.cli import ArgHandler, DefaultHandler, DictHandler, EnvHandler, JSONFileHandler, SecondsDurationAction


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def get_max_widths(data, headers):
    '''Returns a list of maximum widths for each column.'''
    widths = []
    for header in headers:
        max_width = max(len(str(getattr(obj, header)).splitlines()[0]) for obj in data)  # Max width based on data
        widths.append(max(max_width, len(header)))  # Comparing with header width too
    return widths


def print_table(data, headers):
    '''
    Prints a table of the `data` with the specified `headers`.

    ```python
    from dataclasses import dataclass

    @dataclass
    class User:
        first_name: str
        last_name: str
        age: int

    data = {
        User('John', 'Smith', 19),
        User('Jane', 'Doe', 18),
    }
    print_table(data, ['first name', 'last name', 'age'])
    ```

    Keyword arguments
        data -- a map of header and its data value
        headers -- a list of header titles
    '''
    widths = get_max_widths(data, headers)

    # Print header
    for header, width in zip(headers, widths):
        print(f"{header:<{width}}", end=" ")
    print()  # Newline after headers

    # Print separator
    for width in widths:
        print(f"{'-'*width}", end=" ")
    print()  # Newline after separator

    # Print data rows
    for obj in data:
        for key, width in zip(headers, widths):
            print(f"{str(getattr(obj, key)).splitlines()[0]:<{width}}", end=" ")
        print()  # Newline after each row


#region Command line parsing  # noqa


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


def fixme1(args):
    default_config = {
        'FIXME_NAME': 'fixme'
    }
    name_handler = ArgHandler(args, EnvHandler(DictHandler(default_config)))
    name = name_handler.handle_request('FIXME_NAME')
    logging.debug(f'FIXME_NAME={name}')


def fixme2(args):
    config_path = args.config if args.config else ''
    name_handler = ArgHandler(args, EnvHandler(DictHandler(file_path=config_path, next_handler=DefaultHandler('fixme'))))
    name = name_handler.handle_request('FIXME_NAME')
    logging.debug(f'FIXME_NAME={name}')
    print(f'Duration is {args.duration} seconds')


class App:
    def __init__(self) -> None:
        self.args = None
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

    def parse_args(self, args=None):
        self.args = self.parser.parse_args(args)

    def run(self):
        if not self.args:
            self.parse_args()
        _init_logger(getattr(logging, self.args.verbosity.upper()))
        logging.debug(f'command-line args: {self.args}')
        self.args.func(self.args)


#endregion Command line parsing  # noqa


if __name__ == "__main__":
    app = App()
    app.run()
