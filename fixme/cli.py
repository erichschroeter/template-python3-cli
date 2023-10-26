

from abc import abstractmethod
import argparse
import json
import os
import re
import yaml


def duration_in_seconds(time_str: str):
    '''
    Parse a time string with format <minutes>m<seconds>s and return the total number of seconds.
    '''
    match = re.match(r'^((?P<minutes>\d+)m)?((?P<seconds>\d+)s)?$', time_str)
    if match:
        minutes_str = match.group('minutes')
        seconds_str = match.group('seconds')
    else:
        match = re.match(r'^((?P<seconds>\d+)s)?((?P<minutes>\d+)m)?$', time_str)
        if match:
            minutes_str = match.group('minutes')
            seconds_str = match.group('seconds')
        else:
            raise ValueError(f'Invalid time string "{time_str}"')
    minutes = int(minutes_str) if minutes_str else 0
    seconds = int(seconds_str) if seconds_str else 0
    return minutes * 60 + seconds


class SecondsDurationAction(argparse.Action):
    '''
    Example usage:
    ```python
    parser = argparse.ArgumentParser()
    parser.add_argument('--duration', action=SecondsDurationAction)
    ```
    '''
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, duration_in_seconds(values))


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
    def __init__(self, data_dict={}, file_path=None, next_handler=None):
        super().__init__(next_handler)
        self.file_path = file_path
        self.data_dict = data_dict
        if self.file_path:
            with open(file_path, 'r') as config_file:
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
