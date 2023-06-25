from abc import ABC, abstractmethod
import argparse
import logging
import sys
import textwrap


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


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


class Command(ABC):
    @abstractmethod
    def execute(self):
        pass


class StatusCommand(Command):
    def execute(self):
        logging.info('running StatusCommand')


class StartCommand(Command):
    def execute(self):
        logging.info('running StartCommand')


class App:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(
            description=textwrap.dedent('''\
                FIXME
                '''),
            formatter_class=RawTextArgumentDefaultsHelpFormatter)

        self.parser.add_argument('-v', '--verbose',
                                 choices=['error', 'warn', 'info', 'debug'],
                                 default='error',
                                 help='Set the verbosity level.')
        self.subparsers = self.parser.add_subparsers(dest='command')
        start_parser = self.subparsers.add_parser(
            'fixme1',
            help='FIXME',
            formatter_class=RawTextArgumentDefaultsHelpFormatter)
        start_parser.add_argument('--dry-run',
                                  action='store_true',
                                  help='See what would happen without doing anything')
        status_parser = self.subparsers.add_parser(
            'fixme2',
            help='FIXME',
            formatter_class=RawTextArgumentDefaultsHelpFormatter)
        self.command_map = {
            'status': StatusCommand(),
            'start': StartCommand(),
        }
        start_parser.set_defaults(strategy='start')
        status_parser.set_defaults(strategy='status')

    def run(self):
        args = self.parser.parse_args()
        if args.verbose == 'debug' or args.dry_run:
            _init_logger(logging.DEBUG)
        elif args.verbose == 'info':
            _init_logger(logging.INFO)
        elif args.verbose == 'warn':
            _init_logger(logging.WARNING)
        else:
            _init_logger(logging.ERROR)
        logging.debug(f'command-line args: {args}')
        command = self.command_map.get(args.command)
        if command:
            command.execute()
        else:
            eprint(f"Invalid command '{command}'")
            sys.exit(1)


if __name__ == "__main__":
    app = App()
    app.run()
